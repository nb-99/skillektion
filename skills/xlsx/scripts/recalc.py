#!/usr/bin/env python3
# recalc.py — recalculate a spreadsheet in place with headless LibreOffice so
# formula cells regain cached values, and report formula errors as JSON.
#
# Usage: python3 recalc.py FILE [--force] [--timeout S] [--soffice PATH] [--port N]
# Success JSON: {"status": "success"|"errors_found", "total_formulas": N,
#   "total_errors": M, "error_summary": [{"error": "#REF!", "cells": [...]}], "file": ...}
# Refusal/failure JSON has an "error" key and is the only non-zero exit
# (errors_found still exits 0; exit 2 = refused, 1 = failed).

import argparse
import json
import os
import pathlib
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import zipfile

EXIT_OK, EXIT_FAIL, EXIT_REFUSED = 0, 1, 2
RE_EXEC_MARK = "_XLSX_RECALC_UNO_REEXEC"

# Error-shaped cell results: canonical Excel tokens plus LibreOffice's Err:N.
ERROR_TEXT_RE = re.compile(
    r"^(#(REF!|NAME\?|VALUE!|DIV/0!|N/A|NULL!|NUM!|SPILL!|CALC!|GETTING_DATA)|Err:\d+)$")
# xlsx caches external references in worksheet XML as ='[1]Sheet'!$B$2, where
# [N] indexes the workbook's externalLinks part.
EXTERNAL_SIG_RE = re.compile(r"'\[\d+\]")


def emit(obj, code):
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    sys.stdout.flush()
    os._exit(code)  # never block on a stuck UNO worker thread


def emit_error(msg, code, **extra):
    obj = {"error": msg, "status": "error"}
    obj.update(extra)
    emit(obj, code)


def scan_external_references(path):
    """Reasons why the workbook links to files outside itself, or [] if none."""
    try:
        zf = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError):
        emit_error(f"not a readable xlsx/xlsm/ods zip archive: {path}", EXIT_REFUSED)
    reasons = []
    with zf:
        for name in zf.namelist():
            if "externalLink" in name:
                reasons.append(f"external-link part in package: {name}")
        for name in zf.namelist():
            if not re.search(r"^(xl/worksheets/|content\.xml$)", name):
                continue
            data = zf.read(name).decode("utf-8", "replace")
            if EXTERNAL_SIG_RE.search(data):
                reasons.append(
                    f"external-reference formula like ='[1]Sheet'!A1 in {name}")
            if "<externalReference" in data or "of:='file:" in data:
                reasons.append(f"external-reference markup in {name}")
    return reasons


def find_soffice(explicit=None):
    cands = ([explicit] if explicit else []) + \
        ([os.environ["SOFFICE_BIN"]] if os.environ.get("SOFFICE_BIN") else []) + \
        [shutil.which("soffice"), shutil.which("libreoffice"),
         "/Applications/LibreOffice.app/Contents/MacOS/soffice",
         "/usr/lib/libreoffice/program/soffice", "/opt/libreoffice/program/soffice"]
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def reexec_with_uno_python(soffice, argv):
    """os.execve into the first nearby python that can import uno. Candidate
    pythons live next to soffice (LibreOffice bundles one); the uno bridge
    needs URE_BOOTSTRAP pointing at fundamentalrc plus uno.py/pyuno.so on
    PYTHONPATH."""
    sdir = os.path.dirname(os.path.abspath(soffice))
    parent = os.path.dirname(sdir)
    app = os.path.dirname(parent) if os.path.basename(parent) == "Contents" else parent
    dirs = [sdir, parent]
    if os.path.basename(parent) == "Contents":
        dirs += [os.path.join(parent, "Resources"),
                 os.path.join(parent, "Frameworks")]
    extra = {}
    for d in dirs:
        frc = os.path.join(d, "fundamentalrc")
        if os.path.isfile(frc):
            extra["URE_BOOTSTRAP"] = "vnd.sun.star.pathname:" + frc
            break
    parts = [d for d in dirs if os.path.isfile(os.path.join(d, "uno.py"))
             or os.path.isfile(os.path.join(d, "pyuno.so"))]
    if parts:
        extra["PYTHONPATH"] = os.pathsep.join(
            parts + [os.environ.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    cands = [os.path.join(sdir, "python"), os.path.join(sdir, "python3"),
             os.path.join(parent, "Frameworks", "LibreOfficePython.framework",
                          "Versions", "Current", "bin", "python3"),
             os.path.join(app, "program", "python")]
    for cand in cands:
        if not (os.path.isfile(cand) and os.access(cand, os.X_OK)):
            continue
        for env in ({}, extra):
            e = os.environ.copy()
            e.update(env)
            try:
                if subprocess.run([cand, "-c", "import uno"], capture_output=True,
                                  timeout=20, env=e).returncode == 0:
                    e[RE_EXEC_MARK] = "1"
                    os.execve(cand, [cand, os.path.abspath(__file__)] + argv, e)
            except (OSError, subprocess.SubprocessError):
                continue



def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def launch_soffice(soffice, port, profile):
    argv = [soffice, "--headless", "--invisible", "--nologo", "--nolockcheck",
            "--nodefault", "--norestore",
            "-env:UserInstallation=" + pathlib.Path(profile).as_uri(),
            f"--accept=socket,host=127.0.0.1,port={port};urp;"]
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, start_new_session=True)


def col_name(idx):
    name = ""
    idx += 1
    while idx:
        idx, rem = divmod(idx - 1, 26)
        name = chr(65 + rem) + name
    return name


def scan_sheet(sheet, sheet_name):
    """One walk over the used area: count formulas, collect error cells.
    getFormula() returns the formula (with '=') for formula cells, the plain
    value as text for filled cells, and '' for empty cells."""
    total = 0
    errs = {}
    cur = sheet.createCursor()
    cur.gotoEndOfUsedArea(False)
    a = cur.RangeAddress
    for r in range(a.EndRow + 1):
        for c in range(a.EndColumn + 1):
            cell = sheet.getCellByPosition(c, r)
            try:
                f = cell.getFormula()
            except Exception:
                continue
            if not f:
                continue  # empty
            total += f.startswith("=")
            try:
                err = cell.getError() or 0
            except Exception:
                err = 0
            s = cell.getString()
            if err:
                sym = s if (s or "").startswith(("#", "Err:")) else f"Err:{err}"
            elif ERROR_TEXT_RE.match(s or ""):
                sym = s  # formula result or literal cell showing an error string
            else:
                continue
            errs.setdefault(sym, []).append(f"{sheet_name}.{col_name(c)}{r + 1}")
    return total, errs


def uno_work(path, port):
    import uno
    from com.sun.star.beans import PropertyValue

    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local)
    ctx = None
    for _ in range(20):  # soffice accepts TCP before the bridge is fully up
        try:
            ctx = resolver.resolve(f"uno:socket,host=127.0.0.1,port={port};urp;"
                                   "StarOffice.ComponentContext")
            break
        except Exception:
            time.sleep(0.3)
    if ctx is None:
        raise RuntimeError("could not connect to the LibreOffice UNO bridge")
    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx)
    hidden = PropertyValue()
    hidden.Name, hidden.Value = "Hidden", True
    doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(path), "_blank", 0,
                                       (hidden,))
    if doc is None:
        lock = os.path.join(os.path.dirname(path),
                            f".~lock.{os.path.basename(path)}#")
        hint = (f" (stale lock file {lock} present? Remove it if no LibreOffice "
                "instance has the file open)" if os.path.exists(lock) else "")
        raise RuntimeError("LibreOffice failed to load the document" + hint)
    try:
        doc.calculateAll()
        sheets = doc.Sheets
        total_formulas = total_errors = 0
        err_cells = {}
        for i in range(sheets.Count):
            nf, errs = scan_sheet(sheets.getByIndex(i), sheets.getByIndex(i).Name)
            total_formulas += nf
            total_errors += sum(len(v) for v in errs.values())
            for sym, cells in errs.items():
                err_cells.setdefault(sym, []).extend(cells)
        doc.store()  # same format as loaded; now carries cached values
    finally:
        for closer in (lambda: doc.close(False), desktop.terminate):
            try:
                closer()
            except Exception:
                pass
    return {"status": "errors_found" if total_errors else "success",
            "total_formulas": total_formulas, "total_errors": total_errors,
            "error_summary": [{"error": k, "cells": v}
                              for k, v in sorted(err_cells.items())],
            "file": os.path.abspath(path), "engine": "uno"}


def kill_tree(proc, grace=3.0):
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, 15)  # SIGTERM
    except OSError:
        proc.terminate()
    for _ in range(int(grace * 10)):
        if proc.poll() is not None:
            return
        time.sleep(0.1)
    try:
        os.killpg(proc.pid, 9)  # SIGKILL
    except OSError:
        proc.kill()


def uno_recalc(path, soffice, args):
    port = args.port or free_port()
    profile = tempfile.mkdtemp(prefix="lo-recalc-")
    try:
        proc = launch_soffice(soffice, port, profile)
    except OSError as e:
        shutil.rmtree(profile, ignore_errors=True)
        emit_error(f"failed to start LibreOffice ({soffice}): {e}", EXIT_FAIL)
    result = {}

    def work():
        try:
            result["report"] = uno_work(path, port)
        except BaseException as e:
            result["exception"] = f"{type(e).__name__}: {e}"

    t = threading.Thread(target=work, daemon=True)
    t.start()
    t.join(timeout=max(0.5, args.timeout))
    kill_tree(proc)
    shutil.rmtree(profile, ignore_errors=True)
    if "report" in result:
        emit(result["report"], EXIT_OK)
    if t.is_alive():
        emit_error(f"timed out after {args.timeout}s; LibreOffice was killed",
                   EXIT_FAIL)
    emit_error(f"LibreOffice recalculation failed: "
               f"{result.get('exception', 'unknown error')}", EXIT_FAIL)


CONVERT_FILTERS = {".xlsx": "xlsx:Calc MS Excel 2007 XML",
                   ".xlsm": "xlsm:Calc MS Excel 2007 VBA XML",
                   ".ods": "ods", ".xls": "xls:MS Excel 97"}

# Fresh user profile that forces recalculation on load (LibreOffice's default
# for OOXML is to trust cached values, which would make the roundtrip a no-op).
RECALC_XCU = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry"
 xmlns:xs="http://www.w3.org/2001/XMLSchema"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load">
  <prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop>
 </item>
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load">
  <prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop>
 </item>
</oor:items>
"""


def convert_to_recalc(path, soffice, timeout):
    """Last resort when no uno-capable python exists: a convert-to roundtrip
    with recalc-on-load forced to 'always'. Cannot count errors — say so."""
    ext = os.path.splitext(path)[1].lower()
    if ext not in CONVERT_FILTERS:
        emit_error(f"unsupported extension {ext!r}; expected .xlsx/.xlsm/.ods/.xls",
                   EXIT_FAIL)
    profile = tempfile.mkdtemp(prefix="lo-recalc-cfg-")
    os.makedirs(os.path.join(profile, "user"), exist_ok=True)
    with open(os.path.join(profile, "user", "registrymodifications.xcu"), "w") as f:
        f.write(RECALC_XCU)
    outdir = tempfile.mkdtemp(prefix="lo-recalc-out-")
    argv = [soffice, "--headless", "--invisible", "--nologo", "--norestore",
            "-env:UserInstallation=" + pathlib.Path(profile).as_uri(),
            "--convert-to", CONVERT_FILTERS[ext], "--outdir", outdir, path]
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                           start_new_session=True)
    except subprocess.TimeoutExpired:
        emit_error(f"convert-to roundtrip timed out after {timeout}s", EXIT_FAIL)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    produced = os.path.join(outdir, os.path.basename(path))
    if r.returncode != 0 or not os.path.isfile(produced):
        detail = (r.stderr or r.stdout or "").strip().splitlines()
        emit_error("LibreOffice convert-to failed: " +
                   (detail[-1] if detail else str(r.returncode)), EXIT_FAIL)
    shutil.move(produced, path)
    shutil.rmtree(outdir, ignore_errors=True)
    emit({"status": "success", "total_formulas": None, "total_errors": None,
          "error_summary": [], "file": os.path.abspath(path),
          "engine": "convert-to",
          "warnings": ["fallback engine: values were recalculated and saved, but "
                       "formula errors could not be counted — verify the output "
                       "by reading cells back independently"]}, EXIT_OK)


def main():
    ap = argparse.ArgumentParser(
        description="Recalculate a spreadsheet in place with headless LibreOffice.")
    ap.add_argument("file")
    ap.add_argument("--force", action="store_true",
                    help="recalculate even though the workbook links external files")
    ap.add_argument("--timeout", type=float, default=30.0,
                    help="seconds before LibreOffice is killed (default 30)")
    ap.add_argument("--soffice", help="path to the soffice binary")
    ap.add_argument("--port", type=int, help="TCP port for the UNO socket")
    args = ap.parse_args()

    path = os.path.abspath(args.file)
    if not os.path.isfile(path):
        emit_error(f"file not found: {path}", EXIT_REFUSED)
    reasons = scan_external_references(path)
    if reasons and not args.force:
        emit_error(
            "workbook links to external files. Re-saving through LibreOffice "
            "cannot resolve them (the linked file is missing), so linked cells "
            "turn into #NAME? and the links are deleted. Copy the linked cells' "
            "cached values into this workbook first, or pass --force to accept "
            "the loss.", EXIT_REFUSED, external_references=reasons)

    soffice = find_soffice(args.soffice)
    if not soffice:
        emit_error("LibreOffice (soffice) not found. Install it (e.g. "
                   "https://www.libreoffice.org/download, or your system "
                   "package manager) or pass --soffice /path/to/soffice.",
                   EXIT_FAIL)
    try:
        import uno  # noqa: F401
    except ImportError:
        if os.environ.get(RE_EXEC_MARK) != "1":
            reexec_with_uno_python(soffice, sys.argv[1:])
        return convert_to_recalc(path, soffice, args.timeout)
    return uno_recalc(path, soffice, args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Coalesce adjacent runs in word/document.xml that share identical formatting.

Word fragments visible phrases across many <w:r> elements (spellcheck
markers, revision ids, IME input), which makes programmatic editing hard:
a phrase you want to wrap in <w:ins> or anchor a comment to may not be
contiguous XML. This tool merges adjacent sibling runs that are
text-only and have byte-identical <w:rPr> content, so the phrase becomes
one run. It never changes text content or visible formatting.

Usage:
    merge_runs.py unpacked-dir/          # edit word/document.xml in place
    merge_runs.py file.docx              # rewrite the archive in place
    merge_runs.py file.docx -o out.docx  # write to a new archive

Exit codes: 0 = merged or already clean, 1 = usage/IO error, 2 = safety
check failed (input left untouched in dir mode; archive never written).
"""
import argparse
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

DOC_PART = "word/document.xml"

_RUN_OPEN = r"<w:r(?:\s[^>]*)?>"
_PIECE = (r"<w:t(?:\s[^>]*)?>(?:[^<]*)</w:t>|<w:t(?:\s[^>]*)?/>"
          r"|<w:delText(?:\s[^>]*)?>(?:[^<]*)</w:delText>|<w:delText(?:\s[^>]*)?/>")
_TEXT_ONLY = re.compile(rf"^(?:\s*(?:{_PIECE})\s*)+$", re.S)
_RUN_RE = re.compile(rf"({_RUN_OPEN})(.*?)</w:r>", re.S)


def _mergeable_pair(open_a, body_a, open_b, body_b):
    """Decide whether two adjacent runs may merge; return merged body or None."""
    if open_a != open_b:
        return None
    ra = re.search(r"<w:rPr>.*?</w:rPr>", body_a, re.S)
    rb = re.search(r"<w:rPr>.*?</w:rPr>", body_b, re.S)
    rpr = ra.group(0) if ra else ""
    if rpr != (rb.group(0) if rb else ""):
        return None
    rest_a = body_a[:ra.start()] + body_a[ra.end():] if ra else body_a
    rest_b = body_b[:rb.start()] + body_b[rb.end():] if rb else body_b
    if not (_TEXT_ONLY.match(rest_a) and _TEXT_ONLY.match(rest_b)):
        return None  # tabs, drawings, field chars, breaks: leave alone
    kind = "delText" if "delText" in rest_a or "delText" in rest_b else "t"
    texts = re.findall(rf"<w:{kind}[^>]*>([^<]*)</w:{kind}>", rest_a + rest_b, re.S)
    if not texts:
        return ""  # both empty -> drop both
    return f"{rpr}<w:{kind} xml:space=\"preserve\">{''.join(texts)}</w:{kind}>"


def merge_once(xml: str):
    """One fixpoint pass; returns (new_xml, pairs_merged)."""
    runs = [{"start": m.start(), "end": m.end(), "open": m.group(1), "body": m.group(2)}
            for m in _RUN_RE.finditer(xml)]
    edits, i = [], 0
    while i < len(runs) - 1:
        a, b = runs[i], runs[i + 1]
        i += 1
        if a["end"] != b["start"]:
            continue  # not adjacent siblings (something sits between them)
        merged = _mergeable_pair(a["open"], a["body"], b["open"], b["body"])
        if merged is None:
            continue
        replacement = "" if merged == "" else f"{a['open']}{merged}</w:r>"
        edits.append((a["start"], b["end"], replacement))
        i += 1  # b is consumed; don't also edit pair (b, next)
    if not edits:
        return xml, 0
    out, pos, count = [], 0, 0
    for start, end, replacement in edits:
        out.append(xml[pos:start])
        out.append(replacement)
        pos, count = end, count + 1
    out.append(xml[pos:])
    return "".join(out), count


def merge_document_xml(xml: str):
    """Merge runs to a fixpoint; returns (new_xml, total_merges)."""
    total = 0
    while True:
        xml, n = merge_once(xml)
        if n == 0:
            return xml, total
        total += n


def _visible_text(xml: str) -> str:
    """Concatenated w:t + w:delText, for an unchanged-output check."""
    return "".join(re.findall(r"<w:(?:t|delText)[^>]*>([^<]*)</w:(?:t|delText)>", xml))



def main(argv=None):
    ap = argparse.ArgumentParser(description="Merge adjacent same-format text runs in a .docx.")
    ap.add_argument("path", help="unpacked docx directory or a .docx file")
    ap.add_argument("-o", "--output", help="output .docx path (input must be a .docx)")
    args = ap.parse_args(argv)
    path = Path(args.path)

    if path.is_dir():
        target = path / DOC_PART
        if not target.exists():
            sys.exit(f"error: {target} not found (is this an unpacked .docx?)")
        original = target.read_text(encoding="utf-8")
        merged, n = merge_document_xml(original)
        ET.fromstring(merged)
        if n and _visible_text(original) != _visible_text(merged):
            sys.exit("error: merge would change visible text; aborting")
        target.write_text(merged, encoding="utf-8")
        print(f"{target}: {n} run pair(s) merged")
        return 0

    if not path.is_file():
        sys.exit(f"error: {path} is not a file or directory")
    with zipfile.ZipFile(path) as zf:
        if DOC_PART not in zf.namelist():
            sys.exit(f"error: {DOC_PART} missing from {path}")
        original = zf.read(DOC_PART).decode("utf-8")
    merged, n = merge_document_xml(original)
    ET.fromstring(merged)
    if n and _visible_text(original) != _visible_text(merged):
        sys.exit("error: merge would change visible text; aborting")
    out = Path(args.output) if args.output else path
    fd, tmp = tempfile.mkstemp(suffix=".docx", dir=str(out.parent))
    Path(tmp).unlink()  # zipfile wants to create it itself
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = merged.encode("utf-8") if item.filename == DOC_PART else zin.read(item.filename)
            zout.writestr(item, data)
    shutil.move(tmp, out)
    print(f"{out}: {n} run pair(s) merged")
    return 0


if __name__ == "__main__":
    # Purpose: coalesce adjacent same-format text runs so fragmented phrases
    # become contiguous. Usage: merge_runs.py DIR|file.docx [-o out.docx]
    sys.exit(main())

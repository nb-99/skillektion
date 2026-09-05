#!/usr/bin/env python3
"""Fill AcroForm fields of a PDF and report what was set.

Usage:
    fill_form.py FILE.pdf field=value [field2=value2 ...] [-o OUT.pdf]
    fill_form.py FILE.pdf --json values.json [-o OUT.pdf]

Field values come from ``key=value`` arguments (value may contain ``=``) or a
JSON file mapping field names to values (checkboxes accept true/false).
``--flatten`` stamps the filled appearance into the page content so the text
survives in viewers that ignore form fields (the widget annotations are kept;
pypdf cannot remove them during the same pass). Prints a JSON summary listing
set and missing fields to stdout; exits 1 if any requested field is missing.
"""
import argparse
import json
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject


def _field_map(reader):
    """Fully-qualified name -> field dict (pypdf Field objects)."""
    fields = reader.get_fields() or {}
    return {name: dict(f) for name, f in fields.items()}


def _on_states(raw_reader, name):
    """On-state names of a checkbox/radio field, from its appearance dict."""
    root = raw_reader.trailer["/Root"]
    acroform = root.get("/AcroForm")
    if not acroform:
        return []
    for top in acroform.get("/Fields", []):
        for cand in _walk_names(top, ""):
            fq, node = cand
            if fq == name:
                ap = node.get("/AP")
                normal = ap.get("/N") if ap else None
                if normal:
                    return sorted(str(k) for k in normal if str(k) != "/Off")
    return []


def _walk_names(node, prefix):
    kids = node.get("/Kids")
    name = node.get("/T")
    fq = f"{prefix}.{name}" if prefix else (str(name) if name is not None else "")
    if kids:
        for child in kids:
            if child.get("/T") is not None:
                yield from _walk_names(child, fq)
            else:
                yield (fq, child)
    else:
        yield (fq, node)


def _coerce(value, ftype, on_states):
    """Convert a CLI/JSON value into what pypdf expects for this field."""
    if ftype in ("checkbox", "radio", "pushbutton", "Btn"):
        if isinstance(value, bool):
            v = "Yes" if value else "Off"
        else:
            v = str(value)
        if v.lower() in ("true", "yes", "1", "on"):
            v = on_states[0] if on_states else "Yes"
        elif v.lower() in ("false", "no", "0", "off"):
            v = "/Off"
        return NameObject(v)
    if isinstance(value, list):
        return [TextStringObject(str(v)) for v in value]
    return TextStringObject(str(value))


def main():
    ap = argparse.ArgumentParser(description="Fill AcroForm fields in a PDF.")
    ap.add_argument("pdf", help="input PDF")
    ap.add_argument("values", nargs="*", metavar="field=value",
                    help="field assignments; value may contain '='")
    ap.add_argument("--json", metavar="FILE", help="JSON file mapping field names to values")
    ap.add_argument("-o", "--out", help="output PDF (default <input>_filled.pdf)")
    ap.add_argument("--flatten", action="store_true",
                    help="stamp filled appearance into page content")
    args = ap.parse_args()

    assignments = {}
    for pair in args.values:
        if "=" not in pair:
            ap.error(f"argument {pair!r}: expected field=value")
        key, value = pair.split("=", 1)
        assignments[key] = value
    if args.json:
        import pathlib
        assignments.update(json.loads(pathlib.Path(args.json).read_text()))

    if not assignments:
        ap.error("no values given (use field=value or --json)")

    out_path = args.out
    if not out_path:
        stem = args.pdf
        for suffix in (".pdf", ".PDF"):
            if stem.lower().endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        out_path = stem + "_filled.pdf"

    reader = PdfReader(args.pdf)
    fields = _field_map(reader)
    if not fields:
        print(json.dumps({"error": f"{args.pdf} has no AcroForm fields"}))
        sys.exit(1)

    # Button on-states only; for text/choice fields /AP//N is a form
    # XObject whose keys are unrelated PDF keys.
    on_states = {name: (_on_states(reader, name)
                        if str(fields[name].get("/FT", "")).lstrip("/") == "Btn"
                        else []) for name in fields}

    writer_values = {}
    set_fields = []
    missing = []
    for key, value in assignments.items():
        field = fields.get(key)
        if field is None:
            missing.append(key)
            continue
        ftype = str(field.get("/FT", field.get("field_type", ""))).lstrip("/")
        if ftype not in ("Btn", "Tx", "Ch", "Sig"):
            ftype = str(field.get("field_type", "")).lstrip("/")
        if ftype == "Sig":
            missing.append(key)
            continue
        writer_values[key] = _coerce(value, ftype, on_states.get(key, []))
        set_fields.append(key)

    writer = PdfWriter(clone_from=args.pdf)
    # auto_regenerate=False clears /NeedAppearances: pypdf regenerates the
    # appearance streams for text and choice fields itself, so the filled
    # values are visible in any viewer without viewer-side regeneration.
    writer.update_page_form_field_values(
        None, writer_values, auto_regenerate=False, flatten=args.flatten
    )
    with open(out_path, "wb") as fh:
        writer.write(fh)

    result = {
        "input": args.pdf,
        "output": out_path,
        "requested": len(assignments),
        "set": set_fields,
        "missing": missing,
        "flatten": bool(args.flatten),
    }
    print(json.dumps(result, indent=2))
    sys.exit(1 if missing else 0)


# Purpose: fill named AcroForm fields from CLI args or a JSON file.
# Usage:   fill_form.py FILE.pdf field=value [-o OUT.pdf] [--json F] [--flatten]
if __name__ == "__main__":
    main()

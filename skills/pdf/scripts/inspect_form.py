#!/usr/bin/env python3
"""List the AcroForm fields of a PDF as JSON.

Usage:
    inspect_form.py FILE.pdf

For every form field (terminal widgets and parent fields with inherited
attributes) it reports: fully-qualified name, type, current value, options
(choice entries or button on-states), rectangle, required and read-only
flags. Prints a JSON document to stdout; exits 1 on a malformed PDF.
"""
import argparse
import json
import sys

from pypdf import PdfReader
from pypdf.generic import DictionaryObject

READ_ONLY = 1 << 0
REQUIRED = 1 << 1
RADIO = 1 << 15
PUSHBUTTON = 1 << 16
COMBO = 1 << 17
EDIT = 1 << 18
MULTISELECT = 1 << 21

# Attribute keys a child field inherits from its parent (PDF 32000-1, 12.7.3.1).
INHERITED = ("/FT", "/Ff", "/V", "/DV", "/Opt")


def _plain(obj):
    """Convert a pypdf generic object to a JSON-safe plain Python value."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, DictionaryObject):
        if obj.get("/Type") == "/Sig" or obj.get("/FT") == "/Sig":
            return {"signature": True}
        return {str(k): _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    try:
        return str(obj)
    except Exception:
        return repr(obj)


def _ff_inherited(node, inherited):
    ff = node.get("/Ff", inherited.get("/Ff", 0))
    try:
        return int(ff)
    except (TypeError, ValueError):
        return 0


def _field_type(node, inherited):
    ft = node.get("/FT", inherited.get("/FT"))
    if ft is None:
        return None
    ft = str(ft)
    if ft == "/Btn":
        ff = _ff_inherited(node, inherited)
        if ff & PUSHBUTTON:
            return "pushbutton"
        if ff & RADIO:
            return "radio"
        return "checkbox"
    if ft == "/Ch":
        ff = _ff_inherited(node, inherited)
        if ff & MULTISELECT or not (ff & COMBO):
            return "listbox"
        return "combobox"
    if ft == "/Tx":
        return "text"
    if ft == "/Sig":
        return "signature"
    return ft.lstrip("/")


def _on_states(widget):
    """On-state names of a button widget, from its normal appearance dict."""
    ap = widget.get("/AP")
    if not ap:
        return []
    normal = ap.get("/N")
    if not normal:
        return []
    return sorted(str(k) for k in normal if str(k) != "/Off")


def _choice_options(node, inherited):
    opt = node.get("/Opt", inherited.get("/Opt"))
    if not opt:
        return []
    out = []
    for entry in opt:
        entry = _plain(entry)
        if isinstance(entry, list) and entry:
            out.append(str(entry[-1]))  # [export, display] pairs -> display
        else:
            out.append(str(entry))
    return out


def _records(node, inherited, prefix):
    """Yield one record per terminal widget below *node*."""
    inherited = dict(inherited)
    for key in INHERITED:
        if key in node:
            inherited[key] = node[key]

    kids = node.get("/Kids")
    if kids:
        child_fields = [k for k in kids if k.get("/T") is not None]
        widgets = [k for k in kids if k.get("/T") is None and k.get("/Subtype") == "/Widget"]
        if child_fields:
            for child in child_fields:
                name = child.get("/T")
                fq = f"{prefix}.{name}" if prefix else str(name)
                yield from _records(child, inherited, fq)
            # A parent with both named kids and own widgets is unusual; treat
            # its own widgets as belonging to the parent name.
            for widget in widgets:
                yield from _widget_records(node, widget, inherited, prefix)
        elif widgets:
            # A group of widgets sharing one field (e.g. radio group): report
            # the group once, with the union of on-states.
            for widget in widgets:
                records = list(_widget_records(node, widget, inherited, prefix))
                for rec in records:
                    yield rec
            # collapse: only emit first widget's record per field is handled by
            # dedup below
        else:
            # Non-terminal field without widgets: still useful to report.
            yield {
                "name": prefix,
                "type": _field_type(node, inherited),
                "value": _plain(node.get("/V", inherited.get("/V"))),
                "options": _choice_options(node, inherited),
                "rectangle": None,
                "required": bool(_ff_inherited(node, inherited) & REQUIRED),
                "read_only": bool(_ff_inherited(node, inherited) & READ_ONLY),
            }
    elif node.get("/Subtype") == "/Widget" or node.get("/AP") or node.get("/Rect"):
        yield from _widget_records(node, node, inherited, prefix)
    else:
        # Field node without kids and without a widget: report as-is.
        yield {
            "name": prefix,
            "type": _field_type(node, inherited),
            "value": _plain(node.get("/V", inherited.get("/V"))),
            "options": _choice_options(node, inherited),
            "rectangle": None,
            "required": bool(_ff_inherited(node, inherited) & REQUIRED),
            "read_only": bool(_ff_inherited(node, inherited) & READ_ONLY),
        }


def _widget_records(field, widget, inherited, fq):
    rect = widget.get("/Rect", field.get("/Rect"))
    rectangle = None
    if rect:
        try:
            rectangle = [round(float(v), 2) for v in rect]
        except (TypeError, ValueError):
            rectangle = None
    ff = _ff_inherited(field, inherited)
    value = _plain(widget.get("/V", field.get("/V", inherited.get("/V"))))
    ftype = _field_type(field, inherited)
    options = []
    if ftype in ("radio", "checkbox"):
        options = _on_states(widget)
    elif ftype in ("combobox", "listbox"):
        options = _choice_options(field, inherited)
    yield {
        "name": fq,
        "type": ftype,
        "value": value,
        "options": options,
        "rectangle": rectangle,
        "required": bool(ff & REQUIRED),
        "read_only": bool(ff & READ_ONLY),
    }


def main():
    ap = argparse.ArgumentParser(description="List AcroForm fields of a PDF as JSON.")
    ap.add_argument("pdf", help="path to the PDF")
    args = ap.parse_args()

    try:
        reader = PdfReader(args.pdf)
    except Exception as exc:
        print(json.dumps({"error": f"cannot read {args.pdf}: {exc}"}))
        sys.exit(1)

    root = reader.trailer["/Root"]
    acroform = root.get("/AcroForm")
    fields = []
    if acroform:
        for top in acroform.get("/Fields", []):
            name = top.get("/T")
            fields.extend(_records(top, {}, str(name) if name is not None else ""))

    # A field may yield several widget records under the same name (radio
    # groups). Keep the first, but merge option lists so the group's
    # on-states survive.
    merged = {}
    order = []
    for rec in fields:
        if rec["name"] in merged:
            for opt in rec["options"]:
                if opt not in merged[rec["name"]]["options"]:
                    merged[rec["name"]]["options"].append(opt)
            if merged[rec["name"]]["rectangle"] is None:
                merged[rec["name"]]["rectangle"] = rec["rectangle"]
        else:
            merged[rec["name"]] = rec
            order.append(rec["name"])

    print(json.dumps(
        {"pdf": args.pdf, "field_count": len(order),
         "fields": [merged[n] for n in order]},
        indent=2,
    ))


# Purpose: inspect AcroForm fields of a PDF and emit them as JSON.


# Usage:   inspect_form.py FILE.pdf > fields.json
if __name__ == "__main__":
    main()

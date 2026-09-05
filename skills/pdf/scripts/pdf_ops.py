#!/usr/bin/env python3
"""Everyday PDF page operations via pypdf: merge, split, rotate, encrypt,
decrypt, watermark, and info.

Usage:
    pdf_ops.py merge   IN1.pdf IN2.pdf [...] -o OUT.pdf
    pdf_ops.py split   IN.pdf --outdir DIR
    pdf_ops.py rotate  IN.pdf --degrees 90 [--pages 1-3,5] -o OUT.pdf
    pdf_ops.py encrypt IN.pdf -o OUT.pdf --user-pw PW [--owner-pw PW]
    pdf_ops.py decrypt IN.pdf -o OUT.pdf --password PW
    pdf_ops.py stamp   OVERLAY.pdf BASE.pdf -o OUT.pdf   # overlay page 1 of
                       OVERLAY on every page of BASE (e.g. a watermark stamp)
    pdf_ops.py info    IN.pdf

info prints a JSON summary (page count, encryption status, metadata). Other
subcommands exit 0 on success and print a one-line result.
"""
import argparse
import json
import sys

from pypdf import PdfReader, PdfWriter


def _out_path(args, default_suffix):
    return getattr(args, "out", None) or args.input[0] + default_suffix


def _parse_pages(spec, total):
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            for n in range(int(lo), int(hi) + 1):
                if not 1 <= n <= total:
                    raise ValueError(f"page {n} out of range (1..{total})")
                pages.add(n - 1)
        else:
            n = int(part)
            if not 1 <= n <= total:
                raise ValueError(f"page {n} out of range (1..{total})")
            pages.add(n - 1)
    return sorted(pages)


def cmd_merge(args):
    writer = PdfWriter()
    for path in args.input:
        reader = PdfReader(path)
        if reader.is_encrypted:
            reader.decrypt(args.password or "")
        writer.append(reader)
    with open(_out_path(args, "_merged.pdf"), "wb") as fh:
        writer.write(fh)
    print(f"merged {len(writer.pages)} pages -> {_out_path(args, '_merged.pdf')}")


def cmd_split(args):
    reader = PdfReader(args.input)
    if reader.is_encrypted:
        reader.decrypt(args.password or "")
    import os
    os.makedirs(args.outdir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.input))[0]
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        out = os.path.join(args.outdir, f"{stem}-{i + 1:04d}.pdf")
        with open(out, "wb") as fh:
            writer.write(fh)
    print(f"split {len(reader.pages)} pages -> {args.outdir}/{stem}-NNNN.pdf")


def cmd_rotate(args):
    reader = PdfReader(args.input)
    if reader.is_encrypted:
        reader.decrypt(args.password or "")
    if args.degrees % 90 != 0:
        ap = args.__dict__.setdefault("_ap", None)
        sys.exit("--degrees must be a multiple of 90")
    indices = _parse_pages(args.pages, len(reader.pages)) if args.pages else None
    writer = PdfWriter(clone_from=args.input) if reader.is_encrypted else PdfWriter()
    if not reader.is_encrypted:
        writer.append(reader)
    else:
        writer.append(reader)
    for i, page in enumerate(writer.pages):
        if indices is None or i in indices:
            page.rotate(args.degrees)
    out = _out_path(args, "_rotated.pdf")
    with open(out, "wb") as fh:
        writer.write(fh)
    print(f"rotated {len(indices) if indices else len(writer.pages)} page(s) "
          f"by {args.degrees} degrees -> {out}")


def cmd_encrypt(args):
    writer = PdfWriter(clone_from=args.input)
    writer.encrypt(user_password=args.user_pw or "", owner_password=args.owner_pw)
    out = _out_path(args, "_encrypted.pdf")
    with open(out, "wb") as fh:
        writer.write(fh)
    print(f"encrypted -> {out}")


def cmd_decrypt(args):
    reader = PdfReader(args.input)
    if not reader.is_encrypted:
        print(f"{args.input} is not encrypted; nothing to do")
        return
    if not reader.decrypt(args.password or ""):
        sys.exit("wrong password")
    writer = PdfWriter()
    writer.append(reader)
    out = _out_path(args, "_decrypted.pdf")
    with open(out, "wb") as fh:
        writer.write(fh)
    print(f"decrypted -> {out}")


def cmd_stamp(args):
    stamp_reader = PdfReader(args.overlay)
    stamp = stamp_reader.pages[0]
    base = PdfReader(args.base)
    writer = PdfWriter(clone_from=args.base)
    for page in writer.pages:
        # merge_transformed_page lets you scale the stamp; plain merge_page
        # pastes it at 1:1 using the overlay's own coordinates.
        page.merge_page(stamp)
    out = _out_path(args, "_stamped.pdf")
    with open(out, "wb") as fh:
        writer.write(fh)
    print(f"stamped {len(writer.pages)} page(s) -> {out}")


def cmd_info(args):
    reader = PdfReader(args.input)
    if reader.is_encrypted:
        ok = reader.decrypt(args.password or "")
        encrypted = bool(ok)
    else:
        encrypted = False
    meta = reader.metadata or {}
    print(json.dumps({
        "pdf": args.input,
        "pages": len(reader.pages),
        "encrypted": encrypted,
        "metadata": {k.lstrip("/"): str(v) for k, v in meta.items()},
    }, indent=2))


def main():
    ap = argparse.ArgumentParser(description="Merge, split, rotate, encrypt, decrypt, stamp, and inspect PDFs.")
    ap.add_argument("--password", help="password for opening encrypted inputs")
    sub = ap.add_subparsers(dest="command", required=True)

    subs = []
    p = sub.add_parser("merge")
    p.add_argument("input", nargs="+")
    p.add_argument("-o", "--out", required=True)
    subs.append(p)

    p = sub.add_parser("split")
    p.add_argument("input")
    p.add_argument("--outdir", default="split")
    p.add_argument("-o", "--out")
    subs.append(p)

    p = sub.add_parser("rotate")
    p.add_argument("input")
    p.add_argument("--degrees", type=int, default=90)
    p.add_argument("--pages", help="e.g. 1-3,5 (default: all)")
    p.add_argument("-o", "--out")
    subs.append(p)

    p = sub.add_parser("encrypt")
    p.add_argument("input")
    p.add_argument("-o", "--out")
    p.add_argument("--user-pw", default="")
    p.add_argument("--owner-pw", default="")
    subs.append(p)

    p = sub.add_parser("decrypt")
    p.add_argument("input")
    p.add_argument("-o", "--out")
    subs.append(p)

    p = sub.add_parser("stamp")
    p.add_argument("overlay")
    p.add_argument("base")
    p.add_argument("-o", "--out")
    subs.append(p)

    p = sub.add_parser("info")
    p.add_argument("input")
    subs.append(p)

    # Every subcommand accepts --password (for encrypted inputs); it may
    # appear before or after the subcommand name.
    for p in subs:
        p.add_argument("--password", dest="password_sub", default=None)

    args = ap.parse_args()
    if getattr(args, "password_sub", None):
        args.password = args.password_sub
    try:
        {"merge": cmd_merge, "split": cmd_split, "rotate": cmd_rotate,
         "encrypt": cmd_encrypt, "decrypt": cmd_decrypt, "stamp": cmd_stamp,
         "info": cmd_info}[args.command](args)
    except ValueError as exc:
        sys.exit(str(exc))


# Purpose: pypdf-powered page operations (merge/split/rotate/encrypt/decrypt/stamp/info).
# Usage:   pdf_ops.py COMMAND ... (see module docstring)
if __name__ == "__main__":
    main()

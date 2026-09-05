#!/usr/bin/env python3
"""Duplicate a slide or slide layout inside an unpacked .pptx directory.

Performs the full OPC package bookkeeping needed for the duplicate to be a
first-class part:

  slide mode   - copies ppt/slides/slideN.xml to the next free number,
                 copies its rels (dropping the notesSlide relationship, so the
                 duplicate starts without speaker notes), registers a
                 [Content_Types].xml Override, adds a slide relationship to
                 ppt/_rels/presentation.xml.rels, and appends a p:sldId entry
                 to p:sldIdLst in ppt/presentation.xml (after --after, or at
                 the end).
  layout mode  - copies ppt/slideLayouts/slideLayoutN.xml, copies its rels,
                 registers the content-type Override, and adds the layout to
                 the owning slideMaster's rels. Layouts are not listed in
                 sldIdLst, so presentation.xml is not touched.

The duplicate SHARES the source slide's referenced parts (charts, embedded
workbooks, media): relationships are copied, referenced parts are NOT cloned.
Two slides pointing at one chart part is valid OOXML; edit that part only
when both copies should change, or re-target one relationship first.
Duplicated slides start without speaker notes; add notes to the copy later.

Usage:
    add_slide.py UNPACKED_DIR [--source ppt/slides/slide2.xml]
                             [--after ppt/slides/slide1.xml]
    add_slide.py deck.pptx -o out.pptx [--source ppt/slides/slide2.xml]

`--source` may be a slide path (ppt/slides/slideN.xml), a bare slide file
name (slide2.xml), or a layout path (ppt/slideLayouts/slideLayoutN.xml).
Default source: the last slide in sldIdLst order. Prints the created path.
"""
from __future__ import annotations

import argparse
import posixpath
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

CT = "[Content_Types].xml"
PRES = "ppt/presentation.xml"
PRES_RELS = "ppt/_rels/presentation.xml.rels"
SLIDE_CT = ("application/vnd.openxmlformats-officedocument"
            ".presentationml.slide+xml")
LAYOUT_CT = ("application/vnd.openxmlformats-officedocument"
             ".presentationml.slideLayout+xml")
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_REL_SLIDE = NS_R + "/slide"
NS_REL_LAYOUT = NS_R + "/slideLayout"
NS_REL_NOTES = NS_R + "/notesSlide"


def die(msg):
    sys.exit(f"add_slide.py: error: {msg}")


def read(root: Path, rel: str) -> str:
    p = root / rel
    if not p.is_file():
        die(f"missing package member: {rel}")
    return p.read_text(encoding="utf-8")


def rel_attrs(rels_text: str):
    """Yield (id, target) for every Relationship in a .rels document."""
    for rel in re.findall(r"<Relationship[^>]*/>", rels_text):
        mid = re.search(r'Id="(rId\d+)"', rel)
        mtg = re.search(r'Target="([^"]+)"', rel)
        if mid and mtg:
            yield mid.group(1), mtg.group(1)


def next_free(directory: Path, stem: str) -> int:
    nums = [int(m.group(1)) for f in directory.glob(f"{stem}*.xml")
            if (m := re.fullmatch(rf"{re.escape(stem)}(\d+)\.xml", f.name))]
    return (max(nums) + 1) if nums else 1


def normalize_source(src: str) -> str:
    src = src.lstrip("/")
    if src.startswith(("ppt/slides/", "ppt/slideLayouts/")):
        return src
    return f"ppt/slides/{src}"


def next_rid(rels_text: str) -> str:
    ids = [int(i[3:]) for i, _ in rel_attrs(rels_text)]
    return f"rId{max(ids, default=0) + 1}"


def slide_paths_in_order(root: Path):
    """Slide part paths in sldIdLst order, resolved via presentation rels."""
    pres, rels = read(root, PRES), read(root, PRES_RELS)
    rmap = dict(rel_attrs(rels))
    out = []
    for rid in re.findall(r'<p:sldId[^>]*r:id="(rId\d+)"', pres):
        tgt = rmap.get(rid)
        if not tgt:
            die(f"sldIdLst references {rid} but {PRES_RELS} has no such rel")
        if tgt.startswith("/"):
            out.append(tgt.lstrip("/"))
        else:
            out.append(posixpath.normpath(posixpath.join("ppt", tgt)))
    return out


def add_rel(rels_text: str, rid: str, rel_type: str, target: str) -> str:
    entry = f'<Relationship Id="{rid}" Type="{rel_type}" Target="{target}"/>'
    return rels_text.replace("</Relationships>", entry + "</Relationships>")


def add_override(ct_text: str, part: str, content_type: str) -> str:
    entry = f'<Override PartName="/{part}" ContentType="{content_type}"/>'
    return ct_text.replace("</Types>", entry + "</Types>")


def duplicate(root: Path, src_rel: str, after_rel: str | None) -> str:
    """Prepare all edits in memory, then write them in one pass so a
    failure never leaves a half-registered part behind."""
    for req in (CT, PRES, PRES_RELS):
        read(root, req)
    src_rel = normalize_source(src_rel)
    is_layout = src_rel.startswith("ppt/slideLayouts/")
    src = root / src_rel
    if not src.is_file():
        die(f"source part not found: {src_rel}")
    stem = re.sub(r"\d+$", "", src.stem)
    if not re.fullmatch(r"[A-Za-z]+", stem):
        die(f"cannot derive numbering from {src.name}")
    n = next_free(src.parent, stem)
    new_rel = posixpath.join(posixpath.dirname(src_rel), f"{stem}{n}.xml")

    # copy the rels; for slides drop the notesSlide relationship (a
    # notesSlide part belongs to exactly one slide, so the copy starts
    # without speaker notes). Layout/media/chart rels are kept: their
    # targets are shared parts and may legally back multiple slides.
    src_rels = src.parent / "_rels" / f"{src.name}.rels"
    if src_rels.is_file():
        new_rels_text = src_rels.read_text(encoding="utf-8")
    else:
        new_rels_text = ('<?xml version="1.0" encoding="UTF-8" '
                         'standalone="yes"?>'
                         f'<Relationships xmlns="{NS_REL_PKG}"/>'
                         "</Relationships>")
    if not is_layout:
        new_rels_text = re.sub(
            r'<Relationship[^>]*Type="' + re.escape(NS_REL_NOTES) +
            r'"[^>]*/>', "", new_rels_text)

    ct = add_override(read(root, CT), new_rel,
                      LAYOUT_CT if is_layout else SLIDE_CT)
    writes = []  # (path, text)
    if is_layout:
        # register the layout in the slideMaster that owns the source layout
        for master_rels in sorted((root / "ppt/slideMasters/_rels").glob(
                "slideMaster*.xml.rels")):
            mtext = master_rels.read_text(encoding="utf-8")
            for _, tgt in rel_attrs(mtext):
                if tgt.startswith("/"):
                    tgt = tgt.lstrip("/")
                else:
                    tgt = posixpath.normpath(
                        posixpath.join("ppt/slideMasters", tgt))
                if tgt == src_rel:
                    writes.append((master_rels, add_rel(
                        mtext, next_rid(mtext), NS_REL_LAYOUT,
                        posixpath.relpath(new_rel, "ppt/slideMasters"))))
                    break
            else:
                continue
            break
        else:
            print(f"warning: no slideMaster references {src.name}; "
                  "master rels not updated", file=sys.stderr)
    else:
        rid = next_rid(read(root, PRES_RELS))
        pres = read(root, PRES)
        if f'xmlns:r="{NS_R}"' not in pres or f'xmlns:p="{NS_P}"' not in pres:
            die("presentation.xml uses unexpected namespace prefixes; "
                "duplicate by hand")
        if "</p:sldIdLst>" not in pres:
            die("presentation.xml has no <p:sldIdLst>; nothing to append to")
        sld_id = max([int(i)
                      for i in re.findall(r'<p:sldId id="(\d+)"', pres)]
                     or [255]) + 1
        entry = f'<p:sldId id="{sld_id}" r:id="{rid}"/>'
        after = after_rel and normalize_source(after_rel)
        if after:
            order = slide_paths_in_order(root)
            if after not in order:
                die(f"--after {after} is not in sldIdLst (have: {order})")
            idx = order.index(after) + 1
            entries = re.findall(r"<p:sldId[^>]*/>", pres)
            if idx < len(entries):
                pres = pres.replace(entries[idx], entry + entries[idx], 1)
            else:
                pres = pres.replace("</p:sldIdLst>",
                                    entry + "</p:sldIdLst>")
        else:
            pres = pres.replace("</p:sldIdLst>", entry + "</p:sldIdLst>")
        writes.append((root / PRES_RELS, add_rel(
            read(root, PRES_RELS), rid, NS_REL_SLIDE,
            posixpath.relpath(new_rel, "ppt"))))
        writes.append((root / PRES, pres))

    # all validation passed - now mutate the package
    shutil.copyfile(src, root / new_rel)
    (root / posixpath.join(posixpath.dirname(new_rel), "_rels")).mkdir(
        exist_ok=True)
    (root / posixpath.join(posixpath.dirname(new_rel), "_rels",
                           f"{posixpath.basename(new_rel)}.rels")
     ).write_text(new_rels_text, encoding="utf-8")
    (root / CT).write_text(ct, encoding="utf-8")
    for path, text in writes:
        path.write_text(text, encoding="utf-8")
    return new_rel


def rezip(src_dir: Path, out: Path) -> None:
    """Zip an unpacked package; [Content_Types].xml and root rels go first."""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        names = [CT, "_rels/.rels"]
        for p in sorted(src_dir.rglob("*")):
            if p.is_file():
                rel = p.relative_to(src_dir).as_posix()
                if rel not in names:
                    names.append(rel)
        for rel in names:
            zf.write(src_dir / rel, rel)


def main():
    ap = argparse.ArgumentParser(
        description="Duplicate a slide or slide layout in an unpacked pptx "
                    "directory, with full package bookkeeping.")
    ap.add_argument("package", help="unpacked pptx directory, or a .pptx "
                    "file when -o is given")
    ap.add_argument("--source", help="slide or layout part to duplicate "
                    "(default: last slide in sldIdLst)")
    ap.add_argument("--after", help="insert the new slide after this slide "
                    "in sldIdLst (default: append at end)")
    ap.add_argument("-o", "--out", help="with a .pptx input: write the "
                    "updated package here")
    args = ap.parse_args()

    pkg = Path(args.package)
    if args.out:
        if pkg.suffix != ".pptx" or not pkg.is_file():
            die("with -o, PACKAGE must be a .pptx file")
        tmp = Path(tempfile.mkdtemp(prefix="addslide-"))
        try:
            with zipfile.ZipFile(pkg) as zf:
                zf.extractall(tmp)
            src = args.source or slide_paths_in_order(tmp)[-1]
            created = duplicate(tmp, src, args.after)
            rezip(tmp, Path(args.out))
            print(f"created {created} -> {args.out}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return

    if not pkg.is_dir():
        die(f"{pkg} is not a directory (or use -o for a .pptx file)")
    src = args.source or slide_paths_in_order(pkg)[-1]
    print(f"created {duplicate(pkg, src, args.after)}")


if __name__ == "__main__":
    main()

# Purpose: duplicate a slide or slide layout inside an unpacked pptx with all
# OPC bookkeeping (rels, content-type override, presentation.xml sldIdLst),
# so scripted deck surgery does not have to hand-wire package internals.
# Usage: add_slide.py UNPACKED_DIR [--source P] [--after P]
#        add_slide.py deck.pptx -o out.pptx [--source P]

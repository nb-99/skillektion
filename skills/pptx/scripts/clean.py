#!/usr/bin/env python3
"""Garbage-collect an unpacked .pptx directory after structural edits.

Run this after you remove or reorder entries in p:sldIdLst (by hand or with
a script). It computes the set of parts still reachable from the package
root (officeDocument -> slides in sldIdLst -> layouts, masters, notes,
media, charts, embedded workbooks, ...) and deletes everything else:

  - slide parts whose sldIdLst entry or presentation relationship is gone
  - notesSlides, media, charts, embeddings only referenced by removed parts
  - the .rels files of removed parts, plus dangling rels of the document
    part (slide relationships whose r:id no longer appears in sldIdLst)
  - [Content_Types].xml Overrides pointing at removed parts

Unreachable parts are determined transitively, so one pass is enough after
any deletion. Everything is printed so the removal is reviewable; the
directory can be rezipped afterwards from inside it:
`cd UNPACKED_DIR && zip -r ../out.pptx .`

Usage:
    clean.py UNPACKED_DIR [--dry-run]

Prints one line per removed part and one per removed content-type Override.
"""
from __future__ import annotations

import argparse
import posixpath
import re
import shutil
import sys
from pathlib import Path

CT = "[Content_Types].xml"
ROOT_RELS = "_rels/.rels"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL_SLIDE = NS_R + "/slide"


def die(msg):
    sys.exit(f"clean.py: error: {msg}")


def rel_attrs(rels_text: str):
    """Yield (id, type, target, external) for each Relationship."""
    for rel in re.findall(r"<Relationship[^>]*/>", rels_text):
        mtg = re.search(r'Target="([^"]+)"', rel)
        if not mtg:
            continue
        mid = re.search(r'Id="(rId\d+)"', rel)
        mty = re.search(r'Type="([^"]+)"', rel)
        external = 'TargetMode="External"' in rel
        yield (mid.group(1) if mid else None,
               mty.group(1) if mty else "",
               mtg.group(1),
               external)


def rels_path_for(part: str) -> str:
    d, name = posixpath.split(part)
    return posixpath.join(d, "_rels", f"{name}.rels")


def resolve_target(part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base = posixpath.dirname(part)
    return posixpath.normpath(posixpath.join(base, target)) if base else target


def effective_rels(root: Path, part: str):
    """Rels of `part` as they should be honored for reachability.

    For ppt/presentation.xml this drops slide relationships whose r:id no
    longer appears in p:sldIdLst - that is exactly the state after a slide
    was taken out of the slide list by hand.
    """
    rp = root / rels_path_for(part)
    if not rp.is_file():
        return []
    text = rp.read_text(encoding="utf-8")
    live_rids = None
    if part == "ppt/presentation.xml":
        pres = (root / part).read_text(encoding="utf-8")
        m = re.search(r"<p:sldIdLst>(.*?)</p:sldIdLst>", pres, re.S)
        live_rids = set(re.findall(r'r:id="(rId\d+)"', m.group(1))) if m else set()
    out = []
    for rid, rtype, target, external in rel_attrs(text):
        if external:
            continue
        if live_rids is not None and rtype == NS_REL_SLIDE:
            if rid not in live_rids:
                continue
        out.append(resolve_target(part, target))
    return out


def reachable_parts(root: Path) -> set[str]:
    all_files = {p.relative_to(root).as_posix() for p in root.rglob("*")
                 if p.is_file()}
    starts = []
    if (root / ROOT_RELS).is_file():
        for _, rtype, target, external in rel_attrs(
                (root / ROOT_RELS).read_text(encoding="utf-8")):
            if external:
                continue
            tgt = resolve_target("", target)
            if tgt in all_files:
                starts.append(tgt)
            if rtype == NS_R + "/officeDocument":
                starts.append(tgt)
    if not starts:
        die("cannot find the officeDocument part in _rels/.rels")
    seen, queue = set(starts), list(starts)
    while queue:
        part = queue.pop()
        for tgt in effective_rels(root, part):
            if tgt in all_files and tgt not in seen:
                seen.add(tgt)
                queue.append(tgt)
    return seen

def kept_files(reachable: set[str]) -> set[str]:
    keep = set(reachable)
    for part in reachable:
        keep.add(rels_path_for(part))
    keep.add(ROOT_RELS)
    keep.add(CT)
    return keep


def fix_content_types(root: Path, removed: set[str]) -> list[str]:
    ct_path = root / CT
    text = ct_path.read_text(encoding="utf-8")
    drop = []
    for m in re.finditer(
            r'<Override PartName="/([^"]+)"[^>]*/>', text):
        if m.group(1) in removed:
            drop.append(m.group(0))
    for entry in drop:
        text = text.replace(entry, "")
    ct_path.write_text(text, encoding="utf-8")
    return [re.search(r'PartName="/([^"]+)"', e).group(1) for e in drop]


def prune_empty_dirs(root: Path) -> None:
    for d in sorted((p for p in root.rglob("*") if p.is_dir()),
                    key=lambda p: len(p.parts), reverse=True):
        try:
            d.rmdir()
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser(
        description="Remove parts unreachable from the package root of an "
                    "unpacked pptx directory (post sldIdLst edits).")
    ap.add_argument("directory", help="unpacked pptx directory")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be removed; change nothing")
    args = ap.parse_args()

    root = Path(args.directory)
    if not root.is_dir():
        die(f"{root} is not a directory")
    all_files = {p.relative_to(root).as_posix() for p in root.rglob("*")
                 if p.is_file()}
    keep = kept_files(reachable_parts(root))
    removed = sorted(f for f in all_files if f not in keep)
    if not removed:
        print("nothing to remove: every part is reachable")
        return
    for f in removed:
        print(f"removed: {f}")
    if not args.dry_run:
        for f in removed:
            (root / f).unlink()
        prune_empty_dirs(root)
        ct_drops = fix_content_types(root, set(removed))
        for part in ct_drops:
            print(f"removed override: /{part}")
        print(f"clean.py: removed {len(removed)} parts, "
              f"{len(ct_drops)} content-type overrides")
    else:
        print(f"clean.py (dry run): would remove {len(removed)} parts")


if __name__ == "__main__":
    main()

# Purpose: garbage-collect orphaned slides, media, notes, and rels from an
# unpacked pptx directory after sldIdLst edits, and fix [Content_Types].xml.
# Usage: clean.py UNPACKED_DIR [--dry-run]

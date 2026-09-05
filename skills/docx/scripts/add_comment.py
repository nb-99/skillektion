#!/usr/bin/env python3
"""Add a comment to a .docx (or its unpacked directory) and print the anchor.

A Word comment spans several cross-linked parts: word/comments.xml (bodies),
the modern state parts (commentsExtended.xml, commentsIds.xml,
commentsExtensible.xml), one relationship per part, content-type overrides,
and finally the commentRangeStart / commentRangeEnd / commentReference
anchor triplet in word/document.xml — the comment is invisible without it.

This script creates or updates all supporting parts and either inserts the
anchor itself (--insert; only when the target phrase lies inside a single
<w:t>) or prints the exact anchor XML plus run offsets to place by hand.

Usage:
    add_comment.py unpacked-dir/ --text "phrase" [--comment "body"]
        [--author A] [--initials I] [--date ISO] [--parent ID] [--insert]
    add_comment.py file.docx -o out.docx [same options]

A phrase spanning several runs is not anchorable directly: run
scripts/merge_runs.py first, then re-run with --insert.
"""
import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

DOC_PART = "word/document.xml"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
# part name -> (content type, relationship type)
COMMENT_PARTS = {
    "word/comments.xml": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"),
    "word/commentsExtended.xml": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml",
        "http://schemas.microsoft.com/office/2011/relationships/commentsExtended"),
    "word/commentsIds.xml": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsIds+xml",
        "http://schemas.microsoft.com/office/2016/relationships/commentsIds"),
    "word/commentsExtensible.xml": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtensible+xml",
        "http://schemas.microsoft.com/office/2018/relationships/commentsExtensible"),
}

_RUN_RE = re.compile(r"(<w:r(?:\s[^>]*)?>)(.*?)</w:r>", re.S)
_T_RE = re.compile(r"(<w:t(?:\s[^>]*)?>)([^<]*)</w:t>", re.S)
_P_RE = re.compile(r"<w:p(?:\s[^>]*)?>.*?</w:p>", re.S)
_BASIC = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&apos;": "'"}


def unescape_entities(s: str) -> str:
    s = re.sub(r"&#x([0-9A-Fa-f]+);", lambda m: chr(int(m.group(1), 16)), s)
    s = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), s)
    for k, v in _BASIC.items():
        s = s.replace(k, v)
    return s


def escape_text(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def next_hex(taken: set, width: int) -> str:
    while True:
        val = format(int.from_bytes(os.urandom((width + 1) // 2), "big"), f"0{width}X")
        if val not in taken:
            taken.add(val)
            return val


def collect_para_ids(doc_xml: str, comments_xml: str) -> set:
    pat = r'(?:w14:)?paraId="([0-9A-Fa-f]{8})"'
    return set(re.findall(pat, doc_xml)) | set(re.findall(pat, comments_xml))


def existing_comment_ids(doc: str, comments: str):
    ids = {int(v) for v in re.findall(r'<w:comment(?:Reference|Range(?:Start|End)) w:id="(\d+)"', doc)}
    ids |= {int(v) for v in re.findall(r'<w:comment w:id="(\d+)"', comments)}
    return ids


def _state_part(root: str, extra_ns: str, entries: str) -> str:
    """Wrap entries in one of the three comment-state parts."""
    ignorable = root.split(":")[0]
    return (f'{XML_DECL}<{root} xmlns:mc="{MC}" {extra_ns} mc:Ignorable="{ignorable}">'
            f"{entries}</{root}>")


def build_comment_parts(cid, author, initials, date, body, parent_pid, taken):
    """Return (comments_xml, commext_xml, commids_xml, commexts_xml)."""
    paras, pids = [], []
    for line in body.split("\n"):
        pid = next_hex(taken, 8)
        pids.append(pid)
        paras.append(f'<w:p w14:paraId="{pid}" w14:textId="{pid}">'
                     f'<w:r><w:t xml:space="preserve">{escape_text(line)}</w:t></w:r></w:p>')
    comments = (f'{XML_DECL}<w:comments xmlns:w="{W}" xmlns:w14="{W14}">'
                f'<w:comment w:id="{cid}" w:author="{escape_text(author)}" '
                f'w:date="{date}" w:initials="{escape_text(initials)}">'
                + "".join(paras) + "</w:comment></w:comments>")
    # commentsExtended: one entry per comment paragraph; a reply threads via
    # paraIdParent on its first entry, pointing at the parent's paraId.
    parent_attr = f' w15:paraIdParent="{parent_pid}"' if parent_pid else ""
    entries = "".join(
        f'<w15:commentEx w15:paraId="{pid}" w15:done="0"{parent_attr if i == 0 else ""}/>'
        for i, pid in enumerate(pids))
    commext = _state_part(
        "w15:commentsEx",
        f'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w="{W}"',
        entries)
    durable = next_hex(taken, 16)
    commids = _state_part(
        "w16cid:commentsIds",
        'xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid"',
        f'<w16cid:commentEx w16cid:paraId="{pids[-1]}" w16cid:durableId="{durable}"/>')
    commexts = _state_part(
        "w16cex:commentsExtensible",
        'xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex"',
        f'<w16cex:commentEx w16cex:durableId="{durable}" w16cex:date="{date}"/>')
    return comments, commext, commids, commexts


def _into_root(existing: str, root: str, inner: str) -> str:
    """Append `inner` into an existing part root, or exit on a bad shape."""
    if existing.rstrip().endswith(f"</{root}>"):
        return existing.replace(f"</{root}>", inner + f"</{root}>")
    # docx-js emits empty self-closing scaffold roots: expand them.
    m = re.search(rf"<{root}(\s[^>]*)/>", existing)
    if m:
        return (existing[:m.start()] + f"<{root}{m.group(1)}>" + inner
                + f"</{root}>" + existing[m.end():])
    sys.exit(f"error: existing part with root <{root}> is malformed")


def merge_comment_parts(comments: str, new_comment_xml: str) -> str:
    """Append the new w:comment into comments.xml (wrap when absent)."""
    m = re.search(r"<w:comment\b.*</w:comment>", new_comment_xml, re.S)
    if not m:
        sys.exit("error: internal: no w:comment element in new part")
    if not comments:
        return new_comment_xml
    return _into_root(comments, "w:comments", m.group(0))


def find_anchor(doc: str, phrase: str):
    """Return ((t_match, pos), None) when the phrase lies inside one <w:t>,
    (None, pieces) with (start, end, text) fragments when it spans runs of a
    paragraph, (None, None) when not found."""
    for tm in _T_RE.finditer(doc):
        pos = unescape_entities(tm.group(2)).find(phrase)
        if pos >= 0:
            return (tm, pos), None
    first = phrase.split()[0]
    for pm in _P_RE.finditer(doc):
        pieces = [(m.start(2), m.end(2), unescape_entities(m.group(2)))
                  for m in _T_RE.finditer(pm.group(0))]
        if any(first in t for _, _, t in pieces):
            return None, [p for p in pieces if p[2]]
    return None, None


def anchor_xml(cid: int):
    start = f'<w:commentRangeStart w:id="{cid}"/>'
    end = (f'<w:commentRangeEnd w:id="{cid}"/>'
           f'<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>'
           f'<w:commentReference w:id="{cid}"/></w:r>')
    return start, end


def insert_anchor(doc: str, cid: int, tm, pos: int, phrase: str) -> str:
    """Split the containing run and inject the anchor triplet around phrase."""
    run = next(rm for rm in _RUN_RE.finditer(doc)
               if rm.start() <= tm.start() and tm.end() <= rm.end())
    text = tm.group(2)
    pre, post = text[:pos], text[pos + len(phrase):]
    open_tag, body = run.group(1), run.group(2)
    rpr_m = re.search(r"<w:rPr>.*?</w:rPr>", body, re.S)
    rpr = rpr_m.group(0) if rpr_m else ""

    def run_with(t):
        if t == "":
            return ""
        return f'{open_tag}{rpr}<w:t xml:space="preserve">{escape_text(t)}</w:t></w:r>'

    start, end = anchor_xml(cid)
    replacement = (start + run_with(pre) + run_with(phrase) + end + run_with(post))
    return doc[:run.start()] + replacement + doc[run.end():]


def update_support_files(root: Path):
    """Extend [Content_Types].xml and document.xml.rels for the comment parts."""
    ct_path = root / "[Content_Types].xml"
    ct = ct_path.read_text(encoding="utf-8")
    adds = "".join(
        f'<Override PartName="/{name}" ContentType="{ctype}"/>'
        for name, (ctype, _) in COMMENT_PARTS.items()
        if f'PartName="/{name}"' not in ct)
    if adds:
        ct_path.write_text(ct.replace("</Types>", adds + "</Types>"), encoding="utf-8")
    rels_path = root / "word/_rels/document.xml.rels"
    rels = rels_path.read_text(encoding="utf-8")
    used = set(re.findall(r'Id="(rId\d+)"', rels))
    nxt = max((int(r[3:]) for r in used), default=0) + 1
    adds = ""
    for name, (_, reltype) in COMMENT_PARTS.items():
        target = name.split("/", 1)[1]
        if f'Target="{target}"' in rels:
            continue
        while f"rId{nxt}" in used:
            nxt += 1
        adds += f'<Relationship Id="rId{nxt}" Type="{reltype}" Target="{target}"/>'
        used.add(f"rId{nxt}")
        nxt += 1
    if adds:
        rels_path.write_text(
            rels.replace("</Relationships>", adds + "</Relationships>"), encoding="utf-8")


def write_parts(root: Path, comments_full, commext, commids, commexts):
    """Write comments.xml and merge entries into the three state parts."""
    for name, fresh, rootname in (
        ("word/commentsExtended.xml", commext, "w15:commentsEx"),
        ("word/commentsIds.xml", commids, "w16cid:commentsIds"),
        ("word/commentsExtensible.xml", commexts, "w16cex:commentsExtensible"),
    ):
        p = root / name
        existing = p.read_text(encoding="utf-8") if p.exists() else ""
        if existing:
            entry = re.search(rf"<\w+:commentEx\b.*?/>", fresh, re.S).group(0)
            p.write_text(_into_root(existing, rootname, entry), encoding="utf-8")
        else:
            p.write_text(fresh, encoding="utf-8")
    (root / "word/comments.xml").write_text(comments_full, encoding="utf-8")
    update_support_files(root)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Add a Word comment and print its anchor XML.")
    ap.add_argument("path", help="unpacked docx directory or a .docx file")
    ap.add_argument("-o", "--output", help="output .docx (when input is a .docx)")
    ap.add_argument("--text", help="document phrase the comment anchors to")
    ap.add_argument("--comment", default="Comment.", help="comment body (\\n splits paragraphs)")
    ap.add_argument("--author", default="Agent", help="comment author name")
    ap.add_argument("--initials", help="author initials (default: derived from author)")
    ap.add_argument("--date", help="ISO-8601 date (default: now UTC)")
    ap.add_argument("--parent", type=int, help="id of the comment this one replies to")
    ap.add_argument("--insert", action="store_true",
                    help="insert the anchor into document.xml (single-run targets only)")
    args = ap.parse_args(argv)
    path = Path(args.path)

    if path.is_dir():
        root, cleanup = path, False
    elif path.is_file():
        root, cleanup = Path(tempfile.mkdtemp(prefix="docx-add-comment-")), True
        with zipfile.ZipFile(path) as zf:
            zf.extractall(root)
    else:
        sys.exit(f"error: {path} is not a file or directory")

    def done(code=0):
        if cleanup:
            shutil.rmtree(root, ignore_errors=True)
        return code

    if not (root / DOC_PART).exists():
        sys.exit(f"error: {DOC_PART} missing (is this a .docx or unpacked .docx?)")
    doc = (root / DOC_PART).read_text(encoding="utf-8")
    cp = root / "word/comments.xml"
    comments = cp.read_text(encoding="utf-8") if cp.exists() else ""

    taken = collect_para_ids(doc, comments)
    cid = next(i for i in range(20000) if i not in existing_comment_ids(doc, comments))
    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    initials = args.initials or "".join(w[0] for w in args.author.split()[:2]).upper() or "A"

    parent_pid = None
    if args.parent is not None:
        if args.parent not in existing_comment_ids(doc, comments):
            print(f"error: --parent {args.parent} is not an existing comment id")
            return done(1)
        cx = root / "word/commentsExtended.xml"
        if cx.exists():
            m = re.findall(r'w15:paraId="([0-9A-Fa-f]{8})"', cx.read_text(encoding="utf-8"))
            parent_pid = m[-1] if m else None

    comments_xml, commext, commids, commexts = build_comment_parts(
        cid, args.author, initials, date, args.comment, parent_pid, taken)
    comments_full = merge_comment_parts(comments, comments_xml)
    start, end = anchor_xml(cid)

    if args.text is None:
        write_parts(root, comments_full, commext, commids, commexts)
        print(f"comment id {cid} created (no --text given).")
        print("anchor triplet to insert in word/document.xml:")
        print(f"  {start}  ...commented runs...  {end}")
        return done()

    tm_pos, pieces = find_anchor(doc, args.text)
    if tm_pos is not None:
        tm, pos = tm_pos
        if args.insert:
            doc = insert_anchor(doc, cid, tm, pos, args.text)
            (root / DOC_PART).write_text(doc, encoding="utf-8")
        else:
            run_abs_start = doc.rfind("<w:r", 0, tm.start())
            print(f"target found inside one <w:t>; text starts at char offset "
                  f"{tm.start(2) + pos}, containing run at offset {run_abs_start} "
                  f"(document.xml, UTF-8 decoded offsets)")
            print("insert BEFORE that run:")
            print(f"  {start}")
            print("insert directly AFTER that run:")
            print(f"  {end}")
        write_parts(root, comments_full, commext, commids, commexts)
        print(f"comment id {cid} by {args.author} written to comments.xml.")
    elif pieces:
        print(f'phrase "{args.text}" spans multiple runs; anchors cannot be inserted yet.')
        print("run merge_runs.py first, then re-run. fragments found in one paragraph:")
        for s, e, t in pieces:
            print(f"  offset {s}-{e}: {t!r}")
        return done(2)
    else:
        print(f'phrase "{args.text}" not found in document text.')
        return done(1)

    ET.fromstring(doc)
    ET.fromstring(comments_full)

    if not path.is_dir():
        out = Path(args.output) if args.output else path
        fd, tmp = tempfile.mkstemp(suffix=".docx", dir=str(out.parent))
        Path(tmp).unlink()
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zipfile.ZipFile(path).infolist():
                if item.is_dir():
                    continue
                p = root / item.filename
                zout.writestr(item, p.read_bytes() if p.exists() else b"")
        shutil.move(tmp, out)
        print(f"wrote {out}")
    else:
        print(f"anchor {'inserted' if args.insert else 'NOT inserted (use --insert)'}; "
              f"files updated in {path}")
    return done()


if __name__ == "__main__":
    # Purpose: create comment support parts + print/insert the anchor triplet.
    # Usage: add_comment.py DIR|file.docx --text PHRASE [--comment BODY] [--insert]
    sys.exit(main())

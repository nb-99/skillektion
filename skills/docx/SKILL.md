---
name: docx
description: Create, edit, redline, and verify Word .docx files. Use when generating documents with the docx npm package, editing a .docx's XML directly, adding tracked changes (redlining) or comments, or verifying rendered output. Not for .odt, .rtf, .pages, or PDF files.
---

# Word documents (.docx)

A .docx is a zip of XML parts. Generating from scratch is easiest through the
`docx` npm package; changing an existing file is usually surgical XML editing
of its unpacked parts. Pick the row that matches the task:

| Task | Approach |
| --- | --- |
| Create a new document | Write a Node script with the `docx` package, `Packer.toBuffer` to a file |
| Edit an existing document | Unzip, edit `word/document.xml` (and friends), rezip from inside the directory |
| Read the text | `pandoc -t markdown file.docx` (or `textutil -convert txt` on macOS) |
| Verify visually | `soffice --headless --convert-to pdf` then `pdftoppm -png` and inspect |
| Redline / tracked changes | Edit XML: wrap runs in `w:ins` / `w:del` (see below) |
| Add a comment | `scripts/add_comment.py` to create the parts and print/insert the anchor |

## Generating with the `docx` npm package

Everything below is verified against docx 9.x behavior; treat older versions
with suspicion.

```js
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow,
        TableCell, WidthType, ShadingType, AlignmentType, LevelFormat,
        TableOfContents, ImageRun, PageBreak, PositionalTab, PositionalTabAlignment,
        PositionalTabLeader, PositionalTabRelativeTo, PageOrientation } = require("docx");

const doc = new Document({
  numbering: { config: [{ reference: "bullets",
    levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
               style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },  // US Letter
    children: [ /* Paragraphs and Tables */ ],
  }],
});
Packer.toBuffer(doc).then((buf) => fs.writeFileSync("out.docx", buf));
```

Dimensions are DXA: **1440 DXA = 1 inch**. The default page is A4
(11906 x 16838); for US Letter pass `width: 12240, height: 15840` explicitly.
Landscape keeps the same two numbers swapped plus
`orientation: PageOrientation.LANDSCAPE` — the library writes both the
swapped `w:pgSz` values and `w:orient="landscape"`, so don't pre-swap them
yourself.

Hard-won gotchas:

- **Tables need widths twice**: `columnWidths: [dxa, ...]` on the Table AND
  `width: { size: dxa, type: WidthType.DXA }` on every TableCell. DXA only —
  percentage widths resolve against different bases in Word, LibreOffice, and
  pandoc, and tables come out squashed or sprawling somewhere.
- **Cell shading is `ShadingType.CLEAR`, never SOLID.** SOLID darkens the
  fill; CLEAR (the Word default `w:shd w:val="clear"`) renders the plain fill
  color you chose.
- **Bullets come from a numbering config** (`numbering.config` + a Paragraph
  with `numbering: { reference, level }`). Never type a literal "•" into a
  run — it loses list semantics, indentation, and hanging indents.
- **`ImageRun` needs an explicit `type: "png"` (or jpeg/gif/svg).** Omit it
  and docx 9.x silently stores the media part as `image.undefined` with no
  content type; LibreOffice tolerates that, Word offers to "repair" the file.
- **`PageBreak` must sit inside a Paragraph's children**, not bare in a
  section. A break not wrapped in a paragraph is dropped or corrupts output.
- **No `\n` inside a TextRun.** It is written to the XML as a literal
  backslash-n and shows up in the document as that text. One paragraph per
  line, or `new TextRun({ break: 1 })` for a line break within a paragraph.
- **`TableOfContents` writes an empty field marked dirty** (`TOC \h \o "1-2"`
  with `w:dirty="true"`). It renders empty everywhere until a field update:
  Word populates it on open/print, LibreOffice via Tools > Update > Indexes —
  `soffice --headless --convert-to pdf` does NOT populate it, so don't panic
  when the PDF shows no TOC.
- **TOC and pandoc headings need heading styles that resolve.** Give body
  headings `heading: HeadingLevel.HEADING_1` (or `outlineLevel`). pandoc
  recognizes headings through the styles part; docx-js emits
  `<w:basedOn w:val="Normal"/>` on every style but never *defines* a `Normal`
  style, and pandoc's style resolution then fails, demoting every heading to
  a plain paragraph in the pandoc read-back. Fix by injecting one style into
  `word/styles.xml` before (or after) generation:
  `<w:style w:type="paragraph" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>`
- **Dot leaders are positional tabs**, not padded dots: `new PositionalTab({
  alignment: PositionalTabAlignment.RIGHT, leader: PositionalTabLeader.DOT,
  relativeTo: PositionalTabRelativeTo.MARGIN })` inside the paragraph
  produces `<w:ptab w:leader="dot"/>` — real right-aligned dot leaders that
  survive font changes.
- **Namespaces in output are heavy but harmless.** docx-js declares a dozen
  namespaces and drops an empty self-closing `<w:comments .../>` scaffold
  into the package. Word and LibreOffice ignore both.

## Editing an existing .docx

Unzip to a directory and edit the XML parts by hand (or with a script):

```sh
mkdir dir && unzip -o file.docx -d dir      # word/document.xml is the body
# ... edit ...
cd dir && zip -Xr ../out.docx .             # rezip FROM INSIDE the directory
```

- **Check for symlink entries in untrusted files first.** `zipinfo
  file.docx` prints a mode column; any entry starting with `l` (e.g.
  `lrwxrwxrwx`) is a symlink, and command-line `unzip` will happily create
  it (pointing wherever the archive wants, e.g. `/etc/passwd` when you later
  read or follow it). Python's `zipfile` is safe — it writes symlink entries
  as regular files — so for anything you didn't generate yourself, either
  extract with python or filter out `l`-mode entries.
- **Rezip from inside the directory** (`cd dir && zip -Xr ../out.docx .`).
  Zipping with paths (`zip -r out.docx dir/`) nests a `dir/` prefix inside
  the archive and Word can't find the parts. `-X` strips filesystem extra
  fields; unlike odt/epub there is no stored-first entry requirement, so any
  entry order works.
- **Visible phrases are usually fragmented XML.** Word splits text across
  many `<w:r>` runs (spellcheck markers, rsid revision ids, IME input), so
  "the quick brown fox" is rarely one `<w:t>` — you often can't wrap it in a
  `w:ins`, delete it, or anchor a comment to it directly. Run
  `scripts/merge_runs.py` to coalesce adjacent same-format runs (it never
  changes text or formatting), then re-read.
- **`w:rsid*` attributes are inert session bookkeeping** — safe to ignore
  and safe to keep; don't try to "clean" them while editing.
- **Validate after every edit**: `python3 -c "from
  xml.etree import ElementTree; ElementTree.parse('dir/word/document.xml')"`.
  Attribute order never matters; element order often does (see rPr below).
- **Legacy .doc is not .docx.** It's an OLE2 compound file; python's zipfile
  and your XML tooling will fail on it. Convert first with
  `soffice --headless --convert-to docx file.doc`, edit the result, and
  convert back with `--convert-to doc` if the user needs .doc again.

`scripts/merge_runs.py dir/` merges in place on an unpacked directory;
`scripts/merge_runs.py file.docx -o out.docx` on an archive.

## Tracked changes (redlining)

All state lives in `word/document.xml` (plus `w:author`/`w:date`):

```xml
<w:ins w:id="100" w:author="Reviewer" w:date="2026-09-06T10:00:00Z">
  <w:r><w:t>inserted text</w:t></w:r>
</w:ins>
<w:del w:id="101" w:author="Reviewer" w:date="2026-09-06T10:00:00Z">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
```

- Inside `w:del`, the text element is **`w:delText`, not `w:t`** — a plain
  `w:t` inside `w:del` renders the text as if never deleted.
- Every `w:id` must be unique document-wide. Use one author name
  consistently; a mix of authors looks like several people edited the file.
- **Deleting a whole paragraph** is two operations: wrap every run in
  `w:del`, AND mark the paragraph mark itself deleted by adding
  `<w:rPr><w:del w:id="N" .../></w:rPr>` inside that paragraph's `w:pPr`.
  Without the second part the paragraph mark survives and you get an empty
  line; with it, Word merges the paragraph with the next one when the change
  is accepted.
- **Element order inside `w:rPr` is schema-constrained**: in the
  paragraph-mark rPr (`w:pPr > w:rPr`), `w:ins`/`w:del` come first, before
  other properties like `w:rFonts`/`w:b`. Order violations are tolerated by
  some readers and rejected by others — keep the schema order.
- Verify redlines mechanically, not by eye: `pandoc -f docx
  --track-changes=all -t markdown` renders `[text]{.insertion ...}` /
  `[text]{.deletion ...}` / paragraph-mark deletions as `.paragraph-deletion`;
  then diff `--track-changes=accept` vs `=reject` plain-text output to prove
  each edit flips the right way. As a second opinion,
  `soffice --headless --convert-to docx` round-trips the file — LibreOffice
  re-emits its own `w:ins`/`w:del` for anything it understood, and a
  round-trip that loses a change means your markup was wrong.

## Comments

A visible comment is several cross-linked parts, not one:

- `word/comments.xml` — the comment bodies (`w:comment` with `w:id`,
  `w:author`, `w:date`, `w:initials`)
- `word/commentsExtended.xml`, `word/commentsIds.xml`,
  `word/commentsExtensible.xml` — modern Word state (resolved/resolved
  status, durable ids); linked by `w14:paraId` on the comment's paragraphs
- one relationship per part in `word/_rels/document.xml.rels` and one
  `<Override>` per part in `[Content_Types].xml`
- the **anchor triplet in `word/document.xml`** — the comment is invisible
  until this exists:
  `<w:commentRangeStart w:id="0"/> ...commented runs...
  <w:commentRangeEnd w:id="0"/><w:r><w:rPr><w:rStyle w:val="CommentReference"/>
  </w:rPr><w:commentReference w:id="0"/></w:r>`

`scripts/add_comment.py` does all the parts bookkeeping (id allocation,
paraIds, threading via `--parent`, relationships, content types) and either
inserts the anchor itself (`--insert`, when the target phrase sits inside a
single run) or prints the exact anchor XML plus offsets to place by hand.
For a phrase that spans runs, run `scripts/merge_runs.py` first.

pandoc shows comments ONLY with `--track-changes=all`
(`[text]{.comment-start id="0" author="..." date="..."}anchored text
[]{.comment-end id="0"}`); with the default `accept-changes` they vanish
silently. LibreOffice renders comments in the UI but headless PDF export
omits them unless you enable annotation export.

## Verify the output

Never trust generation code — render and read back:

```sh
# render to images (best proxy for "what Word will show")
soffice --headless --convert-to pdf file.docx
pdftoppm -png -r 100 file.pdf page            # then inspect page-*.png

# independent text read-back
pandoc -t plain file.docx                      # cross-platform
textutil -convert txt file.docx -output -      # macOS built-in

# structural check (every edited part)
python3 -c "from xml.etree import ElementTree as ET; ET.parse('dir/word/document.xml')"
```

Assertions worth scripting per task: the table's `gridCol`/`tcW` widths sum
to the table width; each redline edit appears inside a `w:ins`/`w:del` (and
`w:delText` inside `w:del`); comment anchors sit inside the same paragraph
as their target text; page count matches expectation via `pdfinfo`.

## Dependencies

Check, then install what's missing:

- `node` + `docx`: `npm install docx` in a scratch directory (v9.x assumed
  above).
- `pandoc`: `brew install pandoc` or `apt install pandoc`.
- LibreOffice (`soffice`): `brew install --cask libreoffice` or
  `apt install libreoffice`. On some distros the binary is versioned, e.g.
  `libreoffice25.2`.
- poppler (`pdftoppm`, `pdftotext`, `pdfinfo`): `brew install poppler` or
  `apt install poppler-utils`.
- `zip`/`unzip`/`zipinfo`: system defaults. `textutil`: macOS built-in.

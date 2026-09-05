---
name: pdf
description: Work with PDF files. Use when the user mentions a PDF and wants to extract text or tables, fill form fields, merge, split, rotate, encrypt, or decrypt pages, stamp a watermark, generate a PDF, or OCR a scan — phrases like "extract the text from this PDF", "fill out this form", "merge these PDFs", "add a watermark". Not for converting documents between office formats (docx, xlsx have their own skills) or for rendering PDFs in a browser.
---

# Working with PDFs

Pick the library by job, not by preference:

| Task | Tool |
|------|------|
| Read text preserving layout | `pdftotext -layout` (poppler CLI) |
| Programmatic text + tables, per-character geometry | `pdfplumber` |
| Page surgery: merge, split, rotate, stamp, encrypt | `pypdf` (bundled `scripts/pdf_ops.py`) |
| Inspect / fill AcroForm fields | bundled `scripts/inspect_form.py` / `fill_form.py` |
| Generate PDFs | `reportlab` (canvas for pixel control, platypus for flowing documents) |
| Rasterize for visual checks | `pdftoppm` (poppler), or `pdf2image` + `pytesseract` for OCR |

## Read and extract

- `pdftotext -layout in.pdf out.txt` keeps column alignment; plain `pdftotext` reflows and is better for prose. Both are poppler CLI tools.
- `pdfplumber` when you need positions or tables. `page.extract_text(layout=True)` approximates the CLI layout mode; `page.extract_tables()` finds ruled tables. For tables without ruling lines pass `page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})` — the default `lines` strategy returns `[]` when the PDF has no drawn cell borders. `extract_table` returns list-of-lists; wrap in `pandas.DataFrame(...)` yourself (pandas is optional).
- Rotated or diagonal text (stamps, landscape pages) extracts per-character or out of order. When checking for a watermark, strip whitespace from `pdftotext` output before searching, or read back with pypdf per page.

## Page operations

The bundled `scripts/pdf_ops.py` wraps the pypdf calls (merge, split, rotate, encrypt, decrypt, watermark stamp, info as JSON). Use it first; drop to pypdf directly for anything finer.

pypdf gotchas:

- `PdfReader.is_encrypted` then `reader.decrypt(password)` before any page access; `decrypt` returns a truthy password type — check it, a wrong password yields `PasswordType.NOT_DECRYPTED`.
- `writer.encrypt(user_password=..., owner_password=...)` defaults to RC4-128. Pass `algorithm="AES-256"` for modern encryption (writes /V 5).
- `page.rotate(90)` accumulates into `/Rotate`; multiples of 90 only.
- `writer.append(reader)` copies pages plus outline/named destinations; `add_page` copies bare pages.

## Forms (AcroForm)

Workflow: inspect → fill → verify by reading values back AND by rendering pages to images.

1. `scripts/inspect_form.py form.pdf` — JSON of every field: fully-qualified name, type (`text`/`checkbox`/`radio`/`combobox`/`listbox`/`signature`), current value, options (choice entries or button on-states), rectangle, required, read-only. Parent/child hierarchies are flattened; radio groups collapse to one record with their on-states listed as options.
2. `scripts/fill_form.py form.pdf "full_name=Ada Lovelace" priority=High -o out.pdf` (or `--json values.json`; checkboxes accept `true`/`false`). It reports a JSON summary of set vs missing fields and exits 1 when a requested field is missing. Signature fields are never filled.
3. Read values back with `PdfReader(out).get_fields()` and render: `pdftoppm -png -r 100 out.pdf check` — confirm the PNG is non-trivial in size and dimensions match `pdfinfo`.

Key behavior of `update_page_form_field_values` (verified against pypdf 6.x):

- It regenerates appearance streams for text (`/Tx`) and choice (`/Ch`) fields on every update, so filled values are visible in any viewer.
- Pass `auto_regenerate=False` to clear `/NeedAppearances` on the AcroForm. The default `True` sets the flag and asks the *viewer* to regenerate appearances — some viewers ignore that and show blank fields, so always clear it.
- There is no `PdfWriter.flatten()` method. Flattening means `update_page_form_field_values(..., flatten=True)`: the appearance is stamped into the page content stream, but the widget annotations remain. If a job truly needs annotation-free output, rebuild the page with a rasterized or re-drawn copy.
- Checkbox values must be the on-state name from `/AP /N` (usually `/Yes` or `/On`, reportlab uses `/Yes`) or `/Off`; a value that matches no on-state silently falls back to `/Off`.

## Create with reportlab

- Canvas (`reportlab.pdfgen.canvas`) for absolute control: `drawString`, `rect`, `line`, and `canvas.acroForm.textfield(...)` / `.choice(...)` / `.checkbox(...)` / `.radio(...)` for form widgets.
- Platypus (`SimpleDocTemplate` + flowables) for flowing documents with wrapped paragraphs, tables, and page breaks.
- Colors passed to acroForm widgets must be `Color` instances (`reportlab.lib.colors.black`, `Color(0.95,0.95,0.95)`); bare floats that worked in old reportlab now raise `AttributeError`.
- Draw at least one string on the canvas *before* adding form widgets; a page with widgets but no content can fail with a "forward reference to 'Page1'" error at save time.
- Base-14 fonts (Helvetica, Times, Courier) are single-byte encoded. Characters outside Latin-1/WinAnsi come out as wrong glyphs — `H₂SO₄` renders as `HnSOn` (a black box is the other common symptom). Superscript digits `²³¹` survive because they are Latin-1. For sub/superscripts use Paragraph markup `H<sub>2</sub>SO<sub>4</sub>`, `x<super>2</super>`, or draw the smaller font at a manual offset; never rely on Unicode sub/superscript codepoints with base-14 fonts.
- Non-Latin text (Cyrillic, Greek, CJK) needs a registered TrueType font: `pdfmetrics.registerFont(TTFont("Ar", "Arial.ttf"))` then `setFont("Ar", 14)`. The TTF embeds as a subset and text extracts correctly afterward.
- To build an editable form field for later filling: `canvas.acroForm.textfield(name="full_name", x=..., y=..., width=..., height=..., ...)`. Note reportlab's y origin is the page *bottom*.

## Watermarks

Create a stamp page (one page, same size as the target) with reportlab, then overlay it:

```python
from pypdf import PdfReader, PdfWriter
stamp = PdfReader("stamp.pdf").pages[0]
writer = PdfWriter(clone_from="base.pdf")
for page in writer.pages:
    page.merge_page(stamp)
writer.write("out.pdf")
```

`merge_page` pastes at 1:1 using the stamp's own coordinates; use `merge_transformed_page(stamp, Transformation().scale(...))` to scale or reposition. Set the stamp fill with alpha (`setFillColorRGB(0.7,0.7,0.7, alpha=0.5)`).

## OCR scanned PDFs

Rasterize with pdf2image, then OCR with pytesseract:

```python
from pdf2image import convert_from_path
import pytesseract
pages = convert_from_path("scan.pdf", dpi=300)
text = "\n".join(pytesseract.image_to_string(p) for p in pages)
```

Caveats:

- `pdf2image` shells out to poppler's `pdfinfo`/`pdftoppm` — they must be on PATH or you get `PDFInfoNotInstalledError: Unable to get page count`. Pass `poppler_path=` if poppler lives outside PATH.
- OCR quality tracks scan resolution: 300 dpi for body text, 400+ for small print; low-dpi scans misread digits and confusable glyphs. Check a rendered page image first — if a human can't read it, tesseract won't either.
- `pytesseract` needs the `tesseract` binary installed separately (it is not a Python dependency). If `tesseract` is missing from PATH, tell the user and stop rather than silently skipping OCR.

## Verify the output

Never ship a PDF you haven't opened. Loop:

1. `pdfinfo out.pdf` — page count, page size, encryption status; compare against expectation.
2. `pdftotext out.pdf -` (add `-layout` for forms/tables) — confirm the content that must be visible in plain readers is actually there.
3. `pdftoppm -png -r 100 out.pdf page` — rasterize; confirm each page renders, the file is a plausible size (a blank or broken page is a few KB), and dimensions match the page size at that dpi. Read the image back to check it isn't blank when content was expected.
4. For generated form output, re-read field values with pypdf and confirm appearance streams carry the values (a `Tj` with the filled text in `/AP /N`), or trust `pdftotext` showing the values.

Note pdftoppm may print a harmless `Fontconfig error` on minimal systems; the PNG is still written — check the file, not the exit banner.

## Dependencies

Check availability first, then install what's missing:

```sh
command -v pdftotext pdfinfo pdftoppm tesseract   # poppler + OCR binaries
python3 -c "import pypdf, pdfplumber, reportlab"  # python libraries
```

- Python: `pip install pypdf pdfplumber reportlab pdf2image pytesseract` (into a venv; all pure-Python except pdfplumber's optional PIL dependency, which pip resolves).
- Poppler CLI (`pdftotext`, `pdfinfo`, `pdftoppm`, `pdfimages`): system package `poppler-utils` (Debian/Ubuntu), `poppler` (macOS brew, nix `poppler-utils`).
- OCR: `tesseract` binary plus language packs (`tesseract-ocr-eng` on Debian); `pdfimages -png in.pdf prefix` extracts embedded scan images when OCR-ing a single page region is better than the full raster.
- Never assume anything is preinstalled — verify with the checks above and report what you installed.

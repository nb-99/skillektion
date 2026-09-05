---
name: xlsx
description: Create, edit, and verify Excel workbooks (.xlsx/.xlsm/.ods) with openpyxl, pandas, and a LibreOffice recalculation pass. Use when building or editing spreadsheets with formulas, formatting, or multiple sheets, or when a task mentions xlsx, Excel, workbook, spreadsheet, financial model, or openpyxl. Not for plain CSV/TSV files or Google Sheets — handle those as text or with their own tooling.
---

# Excel workbooks (.xlsx, .xlsm, .ods)

Build and edit workbooks with openpyxl, move bulk data with pandas, and make a
LibreOffice recalculation pass part of every delivery that contains formulas.
A workbook whose formulas have never been evaluated is not a finished
deliverable: openpyxl writes formulas as strings and leaves no computed values
behind, so the file looks empty to every reader until something recalculates
and saves it.

| Task | Approach |
|---|---|
| Create or edit cells, formulas, formatting | openpyxl — values are plain assignments, formulas are strings starting with `=` |
| Bulk data in/out (tables, exports) | pandas `read_excel` / `to_excel`, then openpyxl for formulas and formatting |
| Quick look at what is inside | `scripts/dump.py FILE` — per-sheet text dump |
| Read a model: formulas AND values | two `load_workbook` passes (see below) |
| Deliver anything with formulas | `scripts/recalc.py FILE`, then spot-check a few cells |

## Read before you write

Reading a workbook is two different files depending on how you load it, and
mixing them up destroys work:

```python
from openpyxl import load_workbook

wf = load_workbook(path)                  # formulas as stored: B2 = "=SUM(A1:A2)"
wv = load_workbook(path, data_only=True)  # cached values only:  B2 = 100
```

- `data_only=True` returns the cached result of each formula and **no
  formulas**; the default load returns **formulas and no values**. To
  understand a model you were handed — what it computes and what it currently
  shows — you need both passes.
- **Never save a workbook you loaded with `data_only=True`.** Saving writes the
  cached numbers as literal cell values and every formula in the file is gone.
  Load a fresh handle with defaults for anything you intend to write.
- A file written by openpyxl (or never opened and saved by a spreadsheet app)
  has no cached values at all: `data_only=True` reads `None` for every formula
  cell, and `pandas.read_excel` shows them as `NaN`. That is the normal state
  of your own work-in-progress, not a bug — it is why the recalc pass exists.
- `scripts/dump.py` gives a fast text view (`ADDR  formula ->  cached value`),
  marks formulas that have no cached value yet, and shows merged ranges and
  sheet dimensions. Use it instead of opening Excel when someone asks "what's
  in this file?". It needs openpyxl on `python3`:
  `python3 scripts/dump.py model.xlsx --sheet Assumptions`.
- pandas is the right tool for bulk rows (`read_excel` with `sheet_name`,
  `usecols`, `skiprows`; `to_excel` with `index=False`). openpyxl is the right
  tool for structure: formulas, number formats, merged cells, charts. Neither
  replaces the other.

## Writing workbooks that stay honest

- **Formulas, not hardcoded results.** A total must be `=SUM(...)` so it moves
  when its inputs move. If you compute a number in Python and write the
  literal, the workbook silently lies the first time someone edits an input.
  Compute in the sheet; use Python only for data prep and verification.
- **Follow the spec exactly.** Tab names, header wording, column order, the
  user's own formulas — reproduce them, even when you would have phrased it
  differently. If the user wrote `=B5*B6`, do not "improve" it into a named
  range.
- **Document assumptions next to where they are used.** Every hardcoded number
  (growth rate, tax band, conversion factor) gets a labeled cell of its own,
  referenced by formulas — never buried inside a formula body. Cite the real
  source in an adjacent note when one exists ("FY25 budget p.12"), and say so
  plainly when an assumption is yours.
- **A workbook built for someone to fill in needs a legend**: which cells are
  editable (and how they are marked), plus one example row showing a filled-in
  result. Add that example row only when you are creating the file or were
  asked for it — never add example data to a file you were merely asked to
  edit.
- **When editing an existing file, follow its conventions, not generic best
  practice.** Workbooks often mark designated input cells by fill or font
  color; find that scheme (read the file, ask for a screenshot of the "yellow
  cells" rule), write only into designated input areas, and leave every
  existing formula untouched unless the task says otherwise.

## openpyxl gotchas

- **Formula cells carry no cached value** until a real spreadsheet app
  recalculates and saves. Readers (pandas, `data_only=True`, Quick Look, most
  web previewers) see `None`/`NaN`. Fix at delivery time with
  `scripts/recalc.py`, not by writing values yourself.
- **Merged cells**: write the top-left anchor only. Every other cell in the
  merged range is a read-only `MergedCell` — assigning `ws["B2"].value` in a
  merged `A1:B2` raises `AttributeError`. Reading the range back, non-anchor
  cells are `None`.
- **`.xlsm` needs `keep_vba=True`**: `load_workbook(path, keep_vba=True)`.
  Re-saving without it drops the VBA project from the file.
- **Sheet names with spaces must be quoted in references**: write
  `='My Data'!A1`, never `=My Data!A1`. LibreOffice cannot parse the unquoted
  form — it rewrites the formula lowercased and the cell evaluates to
  `#VALUE!`. Quote defensively (single quotes are always legal, even when the
  name has no space).
- **External links do not survive an openpyxl re-save**, and a LibreOffice
  recalc of a file with dead external links replaces the linked cells with
  `#NAME?` and deletes the links. `recalc.py` refuses such files by default.
  If you must edit one, copy the linked cells' cached values into normal cells
  first (they are readable with `data_only=True` before you touch anything).
- Assigning a non-string to a cell writes a value; assigning a string starting
  with `=` writes a formula. `ws["A1"] = "=SUM(B1:B10)"` is a formula;
  `"=text"` as *text* needs a leading apostrophe or an explicit `data_type`.

## Recalculate before delivering

`scripts/recalc.py` (stdlib only) opens the file in headless LibreOffice,
recalculates everything, saves it in place — formulas now carry cached values
— and reports formula errors as JSON:

```
$ python3 scripts/recalc.py model.xlsx
{
  "status": "errors_found",        # or "success"
  "total_formulas": 7,
  "total_errors": 2,
  "error_summary": [{"error": "#NAME?", "cells": ["Report.B8"]}],
  "file": "model.xlsx",
  "engine": "uno"
}
```

- Exit codes: `0` when the file was recalculated (`errors_found` still exits 0
  — fixing errors is your job, the JSON names the cells), `2` when it refused
  (external links, unreadable file), `1` on failure or timeout (default 30 s,
  `--timeout` to override; a killed LibreOffice leaves no lock behind).
- It drives LibreOffice over a UNO socket, preferring the interpreter
  LibreOffice ships with (which can `import uno`); if none can, it falls back
  to a convert-to roundtrip with recalc-on-load forced on and a warning that
  error counts are unavailable — treat `"total_errors": null` as "not
  checked", and verify by reading values back yourself.
- It refuses workbooks containing external references (scan of the package's
  `externalLinks` parts and `'[N]`-style formulas) unless `--force`, because
  recalculation cannot resolve the missing file: the cells turn `#NAME?` and
  the links are deleted. Copy cached values out first, or pass `--force` with
  open eyes.
- A clean recalc proves the formulas **evaluate**, not that they are
  **right**: an off-by-one range reads back error-free with wrong numbers.
  Before building out a grid, spot-check two or three cells against values you
  computed by hand (or with pandas) — read back with `data_only=True` and
  compare. Trust `total_errors` over the summary's shape; both name exact
  cells.
- LibreOffice re-serializes the file when it saves. Day-to-day formatting,
  formulas, and charts survive; exotic features (pivot tables, some chart
  types, external links) may not. Keep the original until you have diffed what
  matters.
- On macOS, a LibreOffice install whose bundled Python refuses to launch
  (code-signing launch constraints) simply falls through to the convert-to
  fallback — the JSON tells you which engine ran.

## Formula compatibility

LibreOffice is the evaluator in your verification loop, and it implements a
smaller function set than Excel. One function it cannot evaluate becomes a
literal `#NAME?` **baked into the delivered file** — every future reader sees
the error, not just your LibreOffice.

- Prefer Excel-2007-era functions: `SUMIFS`, `COUNTIFS`, `AVERAGEIFS`,
  `INDEX`, `MATCH`, `IFERROR`, `SUMPRODUCT`, `TEXT`. They evaluate everywhere.
- Functions added after 2007 (`TEXTJOIN`, `CONCAT`, `IFS`, `SWITCH`,
  `MAXIFS`, `MINIFS`) must be written with the `_xlfn.` prefix:
  `=_xlfn.TEXTJOIN(",",TRUE,A1:A4)`. openpyxl stores the formula verbatim;
  Excel stores those names prefixed internally and hides the prefix in its UI,
  so the prefix is not lost on Excel users. LibreOffice maps the prefixed name
  and evaluates it; the bare name evaluates to `#NAME?`.
- Avoid `XLOOKUP`, `XMATCH`, `SORT`, `FILTER`, `UNIQUE`, `SEQUENCE` when
  LibreOffice is your evaluator. Support varies by version, and where they do
  evaluate they are spilling array functions — an openpyxl-written file
  carries no spill metadata, so at worst only the anchor cell of the intended
  range gets a value, and the error count stays at zero. Use `INDEX`/`MATCH`
  and do sorting, filtering, and deduplication in Python.
- Two useful tells in a recalculated file: a formula LibreOffice could not
  parse comes back **lowercased** (`=My Data!A1` → `=my Data!A1`), and a
  hand-written `#REF!` inside a formula text may import as `#NAME?` — a
  genuine `#REF!` (for example `=INDIRECT("NoSheet!A1")`) reports as `#REF!`.
  Either way the cell is an error; fix the formula, not the symptom.

## Financial modeling conventions

When a model is the deliverable, follow the conventions reviewers expect
(unless the file you are editing already does it differently):

- Color code: **blue** text for hardcoded inputs, **black** for same-sheet
  formulas, **green** for cross-sheet links, **red** for cross-file links.
  Reviewers will look for it.
- Currency formats with the unit named in the header (`Amount ($000)` — the
  format shows thousands, the header says so). Negatives in parentheses:
  `#,##0;(##,##0)`. Percentages are stored as fractions — `0.15` renders
  `15.0%`; storing `15` renders `1500%`.
- Every assumption in its own labeled cell (see above), projection periods
  share one consistent formula dragged across, and every division guards its
  denominator (`=IF(B5=0,0,B4/B5)` or `IFERROR`).
- Number-format strings go on cells (`cell.number_format = "#,##0.00"`), not
  on values.

## Verify the output

1. `python3 scripts/recalc.py FILE` — read `status` and `error_summary`; fix
   every named cell and rerun until `success`.
2. Spot-check: reload with `data_only=True` and compare two or three formulas
   against hand-computed values (or a pandas cross-total). A clean recalc is
   not a correctness proof.
3. Independent read-back: `pd.read_excel(FILE, sheet_name=...)` — if pandas
   sees `NaN` where a formula should be, the file was never recalculated.
4. When layout or formatting matters, render and look:
   ```
   soffice --headless --convert-to pdf --outdir /tmp/x FILE.xlsx
   pdftoppm -png -r 60 /tmp/x/FILE.pdf /tmp/x/page     # poppler-utils
   ```
   then read the PNGs. `qpdf --check` validates the PDF if you need a
   machine check.

## Dependencies

Check availability first (`command -v ...`, `python3 -c "import ..."`,
`soffice --version`), install only what is missing:

- **openpyxl, pandas**: `pip install openpyxl pandas` (any Python ≥3.9).
  `scripts/dump.py` needs openpyxl on the interpreter that runs it.
- **LibreOffice** (recalculation + PDF render): `soffice` must be on PATH or
  passed via `--soffice`. Get it from <https://www.libreoffice.org/download>
  (macOS/Windows) or the system package manager (`apt install libreoffice-calc
  libreoffice-script-provider-python` / `python3-uno` on Debian/Ubuntu,
  `dnf install libreoffice-calc`, `brew install --cask libreoffice` on macOS).
  The Linux distro packages often split the UNO Python bridge into a separate
  package — install it so recalc.py can count errors instead of falling back.
- **poppler-utils** (`pdftoppm`) and **qpdf** — optional, only for the
  visual-verification loop; any system package manager has them.

Scripts never make network calls. Keep scratch files outside the skill
directory.

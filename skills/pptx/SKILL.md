---
name: pptx
description: Create, edit, read, and visually verify PowerPoint .pptx decks. Use when the user asks for a PowerPoint, a slide deck, a presentation, a .pptx file, or to duplicate/delete/reorder slides or fill a deck template. Not for Word documents, PDFs, or spreadsheets (see the docx, pdf, xlsx skills).
---

# PowerPoint decks (.pptx)

Two toolchains, chosen by task. **Creating** a deck from scratch: write a
Node script with `pptxgenjs` — it is a small API that emits the whole
package, and nothing else is needed. **Editing** an existing deck or
template: unzip the package, patch the XML, rezip — a slide deck is a zip
of XML parts, and most edits are simpler as text surgery than as object
model round-trips. **Reading**: dump text with python-pptx.

| Task | Approach |
| --- | --- |
| Create a deck | Node script with `pptxgenjs` → `writeFile` |
| Edit a deck / fill a template | unzip → edit `ppt/slides/slideN.xml` → rezip |
| Duplicate / delete / reorder slides | `scripts/add_slide.py` / edit `sldIdLst` + `scripts/clean.py` |
| Read a deck | python-pptx text dump (markitdown if installed) |
| Verify | reopen with python-pptx, render with LibreOffice, eyeball every slide |

## Creating a deck with pptxgenjs

One `pptxgen` instance per output file, and set the layout before adding
slides. The default 16:9 layout is **10 x 5.625 in** (not 13.3 x 7.5 —
that is `LAYOUT_WIDE`). Position everything within the actual layout, or
shapes land off-slide.

Hard-won API facts (all verified against pptxgenjs 4.x):

- **Colors are six hex digits, no `#`.** pptxgenjs rejects `'#1B2A41'` and
  8-digit hex (`'1B2A41CC'`) with a console warning and **silently falls
  back to black** — alpha never reaches the file. Want see-through fills?
  Use the `transparency` option (0-100) on `fill`/`line`/images; it emits
  `<a:alpha>` correctly.
- **Never share one options object between two add calls.** pptxgenjs
  mutates the object you pass: `addTable` rewrites `x/y/w` to EMU in place,
  `addText` injects defaults (`_bodyProp` with `anchor: 'ctr'`,
  `objectName`, …), `addChart` injects chart defaults (`barDir`,
  `legendPos`, `chartColors`). Positions usually survive (values > 100 EMU
  are passed through), but the leaked defaults do not — a second chart
  inherits the first chart's `barDir`, a second text box inherits vertical
  centering. Build a fresh object per call (a small helper function is the
  cheap fix).
- **Shadow `offset` must be >= 0.** Negative offsets are written verbatim
  as `dist="-25400"`, which the schema forbids — PowerPoint prompts to
  repair. To cast a shadow upward, keep the offset positive and set
  `angle: 270`.
- **Letterspacing is `charSpacing`** (in points; written as
  `spc="charSpacing*100"` with kerning disabled).
- **Bullets:** set `bullet: true` on each item's own options; putting a
  literal `•` in the text as well double-renders. `breakLine: true` on
  every item except the last — without it, items merge into a single
  paragraph (and a single bullet).
- **Text boxes that must align with shapes: `margin: 0`.** Default insets
  (~7.2pt left/right) shift text noticeably inside a box drawn at the same
  x/y/w/h.
- **`rectRadius` only affects rounded-rectangle shapes** (and similar
  rounded presets); on a plain rectangle it is written into the geometry
  but draws nothing.
- **No gradient fills.** Fake them with a pre-rendered gradient image
  (`addImage`).
- **Speaker notes go through `addNotes`** — never as an invisible text box
  off the slide edge.

## Charts: native, not images

Prefer `addChart` over screenshots of charts: decks stay editable, themes
apply, text stays crisp.

Charts come out bare. The defaults you almost always want:

```js
slide.addChart(pptx.charts.BAR, data, {
  x: 0.6, y: 0.8, w: 8.8, h: 4.2,
  showTitle: true, title: 'Revenue by region ($M)',
  showValue: true, dataLabelPosition: 'outEnd',
  chartColors: ['1B2A41', '3E92CC', 'D78A76'],
  catAxisLabelColor: '5A6B7B', valAxisLabelColor: '5A6B7B',
  showLegend: false,               // single series needs no legend
});
```

- `chartColors` colors series; on single-series bar/pie charts it colors
  per data point.
- **Stacked bar/column:** `dataLabelPosition` must be `ctr`, `inEnd`, or
  `inBase`. pptxgenjs happily writes `outEnd` for stacked charts, and that
  value is not valid there — PowerPoint refuses the file while other
  viewers render it. Never leave `outEnd` on a stacked chart.
- **Combo charts with a secondary axis** (`secondaryValAxis: true`) need
  BOTH `valAxes` and `catAxes` arrays with two entries each. Without them
  pptxgenjs still writes a chart, but the second series has no axis pair
  to bind to (the XML ends up with one `valAx`/`catAx` for two series) and
  PowerPoint can drop the chart silently — other tools open the file fine,
  so you will not notice until someone opens it in PowerPoint.
- **After `writeFile`, always re-validate a deck that contains charts:**
  unzip it, confirm `ppt/charts/chartN.xml` parses, and render it
  (below). A chart that PowerPoint rejects is invisible to every other
  tool you might check with.

## Editing existing decks and templates

Never regenerate a deck you were given to edit. Unpack it, patch, rezip:

```sh
mkdir unpacked && unzip -o deck.pptx -d unpacked
# ...edit ppt/slides/*.xml ...
cd unpacked && zip -qr ../deck-fixed.pptx .    # zip FROM INSIDE the dir
```

Zip from inside the directory so `[Content_Types].xml` lands at the root,
not under a folder. A deck unzipped one level too deep opens as garbage.

**Structural edits (duplicate / delete / reorder slides) are package
surgery, not file surgery.** A slide is registered in four places:
the part `ppt/slides/slideN.xml`, its rels
`ppt/slides/_rels/slideN.xml.rels`, a content-type Override in
`[Content_Types].xml`, and a `<p:sldId r:id="...">` entry in
`p:sldIdLst` backed by a relationship in `ppt/_rels/presentation.xml.rels`.

- **Duplicate slides with `scripts/add_slide.py`** — it does all four
  steps, in order, with fresh ids:

  ```sh
  python3 scripts/add_slide.py unpacked/ \
      --source ppt/slides/slide2.xml --after ppt/slides/slide1.xml
  python3 scripts/add_slide.py deck.pptx -o deck-v2.pptx
  ```

  Never hand-copy a slide file: a slide with no rels/content-type/sldIdLst
  entry either disappears or corrupts the deck. The duplicate shares the
  source's chart/media parts (documented in the script header).
- **Reorder or delete slides by editing `p:sldIdLst` only** — move or
  remove the `<p:sldId>` entry; leave the parts for now.
- **Then run `scripts/clean.py`** to garbage-collect parts that are no
  longer reachable (deleted slides, their notes, charts, media,
  embeddings, plus stale content-type overrides):

  ```sh
  python3 scripts/clean.py unpacked/ [--dry-run]
  ```

  It prints everything it removes. Skipping it leaves dead parts in the
  package — legal, but it bloats the file and confuses later edits.
- **XML transforms must preserve namespaces.** Parsing a slide with
  ElementTree and re-serializing can rewrite namespace prefixes
  (`p:` → `ns0:`) and corrupt the deck; PowerPoint is strict about the
  prefixes it expects. Use `defusedxml`/`lxml` (they preserve prefixes on
  round-trip), or patch surgically with regex/string edits the way the
  bundled scripts do, and always reopen the result.
- **Template slots that stay empty must be deleted as whole groups.**
  A template "slot" is usually an image placeholder plus text boxes; if
  you only blank the text, the empty frames still render. Delete the
  whole `<p:sp>`/`<p:pic>` blocks (and check the slide's rels for
  now-orphaned media).
- **Legacy formats first:** convert `.ppt`/`.pot` to `.pptx` with
  `soffice --headless --convert-to pptx file.ppt` before editing. Same for
  applying a `.potx` template to a modern deck.

## Reading a deck

```python
from pptx import Presentation
prs = Presentation('deck.pptx')
for i, slide in enumerate(prs.slides, 1):
    print(f'--- slide {i} ---')
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.text.strip():
            print(shape.text_frame.text)
        if shape.has_chart:
            print('[chart]', shape.chart.chart_type)
    if slide.has_notes_slide:
        print('[notes]', slide.notes_slide.notes_text_frame.text)
```

One block per slide. This is also your content-QA tool: it reads the file
the way a picky consumer would. If markitdown is installed,
`markitdown deck.pptx` gives a quick Markdown dump, but python-pptx sees
charts and notes that markitdown drops.

## Design guidance

- **Palette:** pick colors specific to the topic — not defaults. One
  dominant color, one accent, near-black body text on white. Two hues
  plus neutrals beat a six-color theme every time.
- **Every slide gets a visual element** — a chart, an image, a shape
  grouping, or a large number. A slide that is only text is a slide the
  audience reads instead of listening.
- **Vary layouts.** Ten slides of title-plus-bullets reads as a
  template, not a deck. Alternate: full-bleed statement, two-column,
  chart-dominant, big-number slides.
- **Fonts Office actually ships:** Arial, Calibri, Cambria, Times New
  Roman, Courier New, Bookman Old Style, Century Schoolbook. Anything
  else silently falls back on machines without it.
- **Scale:** titles 36pt+, body 14-16pt. If body text shrinks below 12pt
  to fit, the slide has too much content — cut it.
- **Avoid the generated-deck tells:** accent lines under every title,
  decorative color bars along edges, cream/parchment backgrounds,
  centered body paragraphs, text-only slides, and text boxes overflowing
  their shapes. Each of these is a fingerprint.

## Verify the output

Three passes, in order. Fix, re-render only what changed, stop.

1. **Content QA** — dump the text (python-pptx, above). Grep the dump for
   placeholder leftovers: `TODO`, `Lorem`, `XX%`, `[insert`, triple
   spaces, your own scratch markers.
2. **File QA** — reopen the file with python-pptx (it parses
   presentation.xml, rels, and content types strictly enough to catch
   broken bookkeeping). For scripted XML edits, also unzip and confirm
   `[Content_Types].xml` and every slide's rels parse.
3. **Visual QA** — render and look at every slide:

   ```sh
   soffice --headless --convert-to pdf deck.pptx --outdir render/
   pdftoppm -png -r 60 render/deck.pdf render/slide
   ```

   Then read the PNGs. LibreOffice is not PowerPoint — it will not catch
   the chart-level repair cases — but it catches off-slide shapes,
   overflowing text, missing images, broken fonts, and empty template
   slots. If a render is impossible in your environment, say so and rely
   on passes 1-2.

## Dependencies

Check availability first, then install only what is missing:

- **python-pptx** (read/QA): `python3 -m venv .venv &&
  .venv/bin/pip install python-pptx`.
- **pptxgenjs** (create): `npm install pptxgenjs` in a scratch dir.
- **LibreOffice** (render): `command -v soffice || brew install --cask
  libreoffice` (macOS), `apt install libreoffice` (Debian/Ubuntu), or
  `nix-shell -p libreoffice`.
- **pdftoppm** (rasterize): ships with poppler — `nix-shell -p
  poppler-utils` (note the plural attr name), `apt install poppler-utils`,
  or `brew install poppler`.
- All of these are offline tools; none of the above needs network access
  at run time.

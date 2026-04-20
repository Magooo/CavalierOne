# CavalierOne AI Image Studio — Full Technical Reference

> **Last updated:** 2026-04-20  
> **Route:** `https://cavalier-one.vercel.app/image-studio`  
> **Template:** `templates/image_generator.html` (~2670 lines)  
> **Backend:** `app.py` — route `/api/generate-from-plans`, `/api/enhance-image`

---

## 1. Architecture Overview

The studio has **4 operating modes** (tabs in the left panel):

| Tab | ID | Purpose |
|---|---|---|
| Generate | `panel-generate` | Text-to-image from a brand prompt |
| Enhance Photo | `panel-enhance` | Recolour an existing photo (brick, roof, render) |
| From Plans | `panel-plans` | **Main pipeline** — elevation drawing → photorealistic render |
| Add to Design | `panel-design` | Inject a photo into a Cavalier document template |

The **From Plans** mode is the primary focus and has the most complex pipeline.

---

## 2. Plans-to-Render Pipeline — Step by Step

```
User uploads elevation drawing
        │
        ▼
[Canvas Editor]  ← User erases annotations, paints zone colours
        │
        ▼   canvas.toBlob() exports cleaned PNG
[POST /api/generate-from-plans]
        │
        ├── painted_zones (Roof, Brick, Render…) → injected into Vision prompt
        ├── material_prompt (brick: [...]; cladding: [...]; roof: [...])
        ├── style (Modern Australian Contemporary etc.)
        └── notes (extra text)
        │
        ▼
[Step 1: GPT-4 Vision]  (LLMClient provider="openai", image_path=file_path)
        │  Reads the elevation, describes the BUILT house in one paragraph.
        │  Zone context injected: "dark charcoal zones = Roof area" etc.
        │
        ▼
[Step 2: Build gen_prompt]
        │  Combines: "Photorealistic Australian residential house..." 
        │            + vision_analysis paragraph
        │            + material_section (spatially-mapped zone → product)
        │
        ▼
[Step 3a: Replicate Canny ControlNet]  ← PRIMARY (if REPLICATE_API_TOKEN set)
        │  utils/replicate_client.py → generate_image_controlnet()
        │  Elevation uploaded to Supabase storage → public URL → Replicate
        │  Model: flux-canny-controlnet (preserves structure exactly)
        │
        ▼  (if Replicate fails)
[Step 3b: KIE text-to-image]  ← FALLBACK
        │  utils/kie_client.py → generate_image()
        │  model: 'flux-2/flex-text-to-image', aspect_ratio: '16:9', 2K
        │
        ▼
[Result → Compare panel: Before/After side-by-side]
        │
        ▼
[Refine Render button]  ← Optional: KIE img2img at strength 0.52
        │  Adds photorealistic textures/lighting, reads current swatch selections
        │
        ▼
[Fine-Tune This Render panel]  ← Optional: KIE img2img at strength 0.48
        Façade tab: Window colour, door colour, garage door
        Landscaping tab: Garden style, lawn, driveway
        Atmosphere tab: Time of day
```

---

## 3. Key Files

| File | Role |
|---|---|
| `templates/image_generator.html` | All UI — HTML, CSS, JS in one file (~2670 lines) |
| `app.py` | Flask routes — lines ~780–960 = generate-from-plans |
| `resources/swatches.json` | Product catalogue (roof, brick, cladding, render, trim, garage) |
| `utils/replicate_client.py` | Flux Canny ControlNet wrapper |
| `utils/kie_client.py` | KIE.ai img2img and text-to-image wrapper |
| `marketing/llm_client.py` | GPT-4 Vision wrapper |

---

## 4. Canvas Editor — Eraser + Product Painter

**Location in HTML:** Lines ~733–800 (HTML), Lines ~1285–1470 (JS)

### HTML Structure
```
div#eraser-wrap.eraser-wrap          ← hidden until image loaded
  div#eraser-cursor                  ← floating cursor div (position:fixed)
  div#eraser-scroller.eraser-scroller ← overflow:auto; max-height:340px
    canvas#eraser-canvas             ← the actual drawing canvas
  div.eraser-toolbar                 ← mode toggle + size slider + zoom
    button#mode-btn-erase            ← 🧹 Erase (default active)
    button#mode-btn-paint            ← 🎨 Paint Product
    input#eraser-size (range 4–80)   ← brush size
    button canvasZoom(1.4)           ← zoom in
    button canvasZoom(0.7)           ← zoom out
    button canvasZoomFit()           ← reset to fit
    button eraserUndo()              ← step back (max 30 snapshots)
    button eraserReset()             ← restore original image
  div#eraser-palette.eraser-palette  ← shown in Paint mode only
    paint-swatch[data-colour][data-label]  ← 6 zone swatches
  div#eraser-hint                    ← contextual hint text
```

### JS State Variables
```javascript
let eraserCtx         = null;          // canvas 2D context
let eraserDrawing     = false;         // mouse/touch down state
let eraserSnapshots   = [];            // undo stack of ImageData (max 30)
let eraserOriginalSrc = null;          // data-URL of the raw uploaded file
let canvasMode        = 'erase';       // 'erase' | 'paint'
let paintColour       = 'rgba(60,60,60,0.55)'; // active paint swatch colour
let canvasZoomLevel   = 1.0;           // CSS width multiplier
let paintedZones      = [];            // labels painted (sent to server)
```

### Paint Zone Colour Map
| Zone Label | Paint colour | Server colour hint for Vision |
|---|---|---|
| Roof | `rgba(60,60,60,0.55)` dark charcoal | "dark charcoal/grey zones" |
| Brick | `rgba(160,80,40,0.55)` red-brown | "red-brown/terracotta zones" |
| Render | `rgba(200,185,155,0.6)` cream | "warm cream/beige zones" |
| Feature | `rgba(50,80,120,0.55)` steel blue | "steel blue zones" |
| Windows | `rgba(30,30,30,0.7)` near-black | "near-black zones" |
| Garage | `rgba(210,200,180,0.65)` sand | "sandy beige zones" |

### How Zoom Works
- Canvas CSS `width` is set to `canvasZoomLevel * 100%`
- The scroller div (`overflow:auto`) scrolls the enlarged canvas
- `eraserGetPos(e)` uses `canvas.width / rect.width` ratio — automatically correct at any zoom level
- Fit button resets to `width: 100%`

### How Undo Works
- Before each mouse/touch `startDraw`, `eraserSaveSnapshot()` stores `getImageData()`
- `eraserUndo()` calls `putImageData(eraserSnapshots.pop())`

### How Export Works (in generateFromPlans)
```javascript
const getImageBlob = () => new Promise(resolve => {
  const canvas = document.getElementById('eraser-canvas');
  if (eraserCtx && canvas.width > 0) {
    canvas.toBlob(resolve, 'image/png');   // cleaned version
  } else {
    resolve(fileInput.files[0]);            // raw file fallback
  }
});
```
The cleaned PNG blob is appended to `FormData` as `elevation_image`.

---

## 5. Materials Catalogue (swatches.json)

**Location:** `resources/swatches.json`  
**Loaded in:** `app.py` `/image-studio` route → passed as `swatches_json` Jinja var  
**Used in JS as:** `const SWATCHES = {{ swatches_json | safe }};`

### Categories
| Key | Contents | Count |
|---|---|---|
| `roof` | Colorbond colours (20 shades) | 20 |
| `brick` | PGH Urban, Austral Bricks, Daniel Robertson, Brickworks | 20 |
| `cladding` | James Hardie (Axon, Linea, Stria, Fine, Oblique, Matrix, Brushed Concrete) + Lysaght (Custom Orb, Trimdeck, Shadowline, Nailstrip) | 22 |
| `render` | Dulux AcraTex, Haymes Paint, Dulux, Rockcote | 16 |
| `trim` | Colorbond, Dulux, Haymes Paint | 9 |
| `garage` | Colorbond, B&D Doors | 7 |

### Swatch Object Schema
```json
{
  "id": "ly-nailstrip-monument",
  "name": "Nailstrip Monument",
  "supplier": "Lysaght",
  "hex": "#2F2F2D",
  "image": null,           // or URL string — loaded as background-image
  "prompt": "Lysaght Nailstrip concealed-fix steel wall cladding in Colorbond Monument — narrow horizontal steel planks with concealed fixings for a clean uninterrupted look, bold dark charcoal"
}
```

### Plans Tab Swatch Sections
Four swatch grids exist in the Plans panel:
- `#plans-swatches-brick` — Brick / Masonry
- `#plans-swatches-cladding` — Sheet Cladding (Hardie / Nailstrip / Lysaght)  ← **NEW**
- `#plans-swatches-roof` — Roof Iron (Colorbond)
- `#plans-swatches-render` — Render / Paint

All four populated by `initPlansSwatches()` which runs on first switch to Plans mode.

### Selection State
```javascript
const plansSelections = { brick: null, cladding: null, roof: null, render: null };
// Each value: null | { colour: "Product Name", prompt: "full AI prompt text" }
```

---

## 6. Material Zone Prompting (app.py)

**Critical logic — lines ~838–880 in app.py**

The frontend sends `material_prompt` as: `"brick: [full prompt]; cladding: [full prompt]; roof: [full prompt]"`

The backend parses this and maps each zone to an explicit surface label:

```python
zone_label = {
    'brick':    'lower wall / primary facade surface',
    'cladding': 'upper wall, feature panel, or secondary facade surface',
    'roof':     'roof cladding (steel sheet, NOT roof tiles)',
    'render':   'rendered or painted wall surface',
}.get(zone, zone)
```

Final prompt fragment: `"CRITICAL — render these exact materials on each surface zone: lower wall / primary facade surface: [product prompt]; roof cladding (steel sheet, NOT roof tiles): [product prompt]..."`

**Default fallback (no selections):**
`"COLORBOND STEEL SHEET METAL ROOF (absolutely NOT roof tiles — it must be flat Colorbond sheeting)"`

---

## 7. Painted Zones → GPT-4 Vision

When the user paints zones, `paintedZones` array collects labels (e.g. `["Roof","Brick"]`).  
At generate time: `formData.append('painted_zones', 'Roof,Brick')`.

In `app.py`, this becomes a zone_context block injected into the Vision prompt:
```
IMPORTANT — the user has colour-coded specific zones on this elevation drawing:
- dark charcoal/grey zones on the drawing = Roof surface area
- red-brown/terracotta zones on the drawing = Brick surface area
Use these coloured zones to understand WHICH PART of the facade each material should be applied to.
```

---

## 8. Fine-Tune This Render Panel

**Location in HTML:** Lines ~1030–1135 (HTML), `applyStyleChanges()` JS (~line 2229)

### Structure
```
div#finetune-panel.finetune-panel.hidden
  div.finetune-panel__header  ← click to toggle open/close
  div#ft-body.finetune-panel__body
    tabs: Façade | Landscaping | Atmosphere
    
    FAÇADE:
      ft-colours#ft-window-colours  (window frame: 6 colour dots)
      ft-colours#ft-door-colours    (front door: 7 colour dots)
      ft-pills#ft-garage-pills      (garage: 5 options)
    
    LANDSCAPING:
      ft-pills#ft-garden-pills   (garden style: 6 options)
      ft-pills#ft-lawn-pills     (lawn: 4 options)
      ft-pills#ft-driveway-pills (driveway: 5 options)
    
    ATMOSPHERE:
      ft-pills#ft-time-pills  (time of day: 5 options)
    
    button#ft-apply-btn → applyStyleChanges()
```

### How Selection Works (FIXED)
Click delegation on `document` handles both element types:
```javascript
document.addEventListener('click', e => {
  const dot = e.target.closest('.ft-colour');
  if (dot) {
    document.querySelectorAll(`.ft-colour[data-group="${dot.dataset.group}"]`)
      .forEach(d => d.classList.remove('selected'));
    dot.classList.add('selected');
    return;
  }
  const pill = e.target.closest('.ft-pill');
  if (pill) {
    document.querySelectorAll(`.ft-pill[data-group="${pill.dataset.group}"]`)
      .forEach(p => p.classList.remove('selected'));
    pill.classList.add('selected');
  }
});
```

### Selected State CSS
- `.ft-pill.selected` → filled brand-dark red background, white text
- `.ft-colour.selected` → brand-dark outline + `::after` checkmark (✓) with white text-shadow — visible on both dark and white swatches

### applyStyleChanges()
Reads `getFtSelection(group)` → `querySelector('.ft-colour[data-group="X"].selected, .ft-pill[data-group="X"].selected')`  
Posts to `/api/enhance-image` with `img2img` strength `0.48`, returns new image URL.

---

## 9. Refine Render

**Button:** `#btn-refine-render`  
**Function:** `refineRender()` in JS  
**Endpoint:** `/api/enhance-image` with strength `0.52`

The refine prompt reads current `plansSelections` swatches dynamically:
```javascript
let mats = '';
if (plansSelections.brick)    mats += `brick: ${plansSelections.brick.prompt}. `;
if (plansSelections.cladding) mats += `cladding: ${plansSelections.cladding.prompt}. `;
if (plansSelections.roof)     mats += `roof: ${plansSelections.roof.prompt}. `;
if (plansSelections.render)   mats += `render: ${plansSelections.render.prompt}. `;
```

---

## 10. Environment Variables (Vercel)

| Variable | Purpose |
|---|---|
| `REPLICATE_API_TOKEN` | Enables Flux Canny ControlNet (primary engine) |
| `KIE_API_KEY` | KIE.ai text-to-image and img2img (fallback + refine + fine-tune) |
| `OPENAI_API_KEY` | GPT-4 Vision for elevation analysis |
| `SUPABASE_URL` | Image storage (control image must be public URL for Replicate) |
| `SUPABASE_KEY` | Supabase auth |

**Important:** File uploads go to `tempfile.gettempdir()` (= `/tmp` on Vercel) not `resources/uploads/` which is read-only on Vercel serverless.

---

## 11. Known Issues & Limitations

| Issue | Status | Notes |
|---|---|---|
| Roof tiles instead of Colorbond | ✅ Fixed | Prompt now explicitly says "NOT roof tiles" |
| Fine-Tune selections not visually responding | ✅ Fixed | Added click delegation JS |
| No James Hardie / Nailstrip products | ✅ Fixed | 22 cladding products added |
| Textures not applied to correct surface | ✅ Fixed | Spatial zone-to-product mapping |
| Painted zones not sent to AI | ✅ Fixed | `painted_zones` sent in FormData, injected into Vision prompt |
| ControlNet "Vision failed" error | Known | Falls back to KIE text-to-image automatically |
| PDF elevation support | ❌ Not implemented | Would need `pdf2image` |

---

## 12. Next Steps / Backlog

| Priority | Feature | Notes |
|---|---|---|
| High | **Custom Colorbond swatch colours for paint zones** | Let user pick actual Colorbond from catalogue for each paint zone swatch colour, so the painter and swatches are linked |
| High | **Improve ControlNet output quality** | Test `guidance_scale`, `control_guidance_start` params in replicate_client |
| Medium | **PDF upload support** | `pdf2image` → extract first page as PNG, then run existing pipeline |
| Medium | **Save render to design library** | Currently only adds to current session history |
| Medium | **Product-linked paint swatches** | When user selects Axon Monument swatch, the Feature painter auto-picks matching dark grey |
| Low | **Multi-elevation batch** | Front + side + rear elevations generating all at once |
| Low | **Perspective generation** | 3/4 angle render from two elevation drawings |

---

## 13. UI JS Key Functions Reference

| Function | Purpose |
|---|---|
| `handlePlansFile(input)` | Loads file → stores `eraserOriginalSrc` → `initEraserCanvas()` |
| `initEraserCanvas(src)` | Draws image onto canvas, resets zoom/undo/zones |
| `setCanvasMode(mode)` | Toggle erase/paint; show/hide palette; update cursor class |
| `selectPaintSwatch(el)` | Sets `paintColour` from clicked swatch `data-colour` |
| `canvasZoom(factor)` | Multiplies `canvasZoomLevel`, updates CSS width |
| `eraserUndo()` | Pops snapshot from stack, restores to canvas |
| `eraserReset()` | Reloads `eraserOriginalSrc` onto canvas |
| `generateFromPlans()` | Main pipeline trigger — exports canvas, builds FormData, calls API |
| `initPlansSwatches()` | Populates brick/cladding/roof/render grids from SWATCHES object |
| `selectPlansSwatch(el, mat)` | Sets `plansSelections[mat]` = { colour, prompt } |
| `refineRender()` | Posts current render to /api/enhance-image at strength 0.52 |
| `applyStyleChanges()` | Fine-Tune apply — reads all ft selections, posts to /api/enhance-image |
| `getFtSelection(group)` | Returns selected `.ft-colour` or `.ft-pill` `data-value` for a group |
| `toggleFinetunePanel()` | Open/close the Fine-Tune panel |
| `switchFtTab(tab, btn)` | Switch between Façade / Landscaping / Atmosphere |

# CavalierOne — Image Studio Pipeline Fixes

> Changelog of diagnosed issues, fixes, and known limitations in the AI Architectural Visualisation pipeline.

---

## 2026-05-04 — Image Studio Rendering Pipeline Overhaul

### 🔧 Fixes Applied

#### 1. Rendering Engine Swap
**Problem:** `black-forest-labs/flux-canny-pro` does NOT expose a `control_strength` parameter. The AI treats canny edges as loose suggestions — adds phantom windows, merges posts, ignores gable angles.

**Fix:** Switched primary engine to **`xlabs-ai/flux-dev-controlnet`** which exposes:
- `control_strength` (0–3) — set to **0.85** normal, **0.95** for corrections
- `control_type: "canny"` — explicit canny edge mode
- `guidance_scale` (1–10) — set to **3.5** normal, **5.0** for corrections

**Fallback:** If xlabs model fails, auto-falls back to `flux-canny-pro` (guidance=25).

**Files:** `utils/replicate_client.py`, `app.py` (lines ~1128-1141)

---

#### 2. Guidance Scale Was Broken (3.5 on a 1–100 Scale)
**Problem:** `flux-canny-pro` guidance range is 1–100 (default **30**). We were sending **3.5** — effectively telling the AI to ignore the prompt entirely.

**Fix:** Now using xlabs dev model (guidance range 1–10, default 3.5). The old pro fallback uses guidance=25.

---

#### 3. GPT-4 Vision Prompt — Too Vague
**Problem:** Vision prompt asked for a "coherent paragraph" but didn't demonstrate the precision level required. GPT-4 was producing generic descriptions like "a modern home with a garage and entry" instead of counting posts, describing cladding panels, noting where gables meet fascia.

**Fix:** Added a **few-shot example** showing GPT-4 exactly what we expect:
```
"Single-storey contemporary home. From the left: a solid brick wall with no openings
leads into a double garage under a low hip roof. The roofline steps up into a prominent
central gable rising to a sharp point above the entry. Under the gable is a continuous
vertical cladding feature panel running from the gable apex down to porch level. Below
the cladding, two thin square posts stand side-by-side with an even gap..."
```

Added rules:
- Count elements EXACTLY (TWO posts, ONE window, ZERO openings)
- Feature walls = continuous surfaces, NOT separate piers
- If a wall is blank, say "solid wall with no openings"
- Traverse left-to-right

**File:** `app.py` (lines ~1024-1055)

---

#### 4. Generation Prompt — Structural Description Was Buried
**Problem:** The gen_prompt put "Professional architectural exterior photograph, photorealistic..." BEFORE the structural description. In Flux, text at the START of the prompt has the most weight — so the AI was prioritising "sunny day, blue sky" over "two posts with a gap".

**Fix:** Structural description now goes FIRST:
```python
gen_prompt = f"{vision_analysis} {material_section} Photorealistic exterior photograph..."
```

Also in `replicate_client.py`, the prompt wrapper puts `{prompt}` first, style keywords after.

**Files:** `app.py` (lines ~1087-1093), `utils/replicate_client.py`

---

#### 5. Anti-Window-Hallucination
**Problem:** Flux generates phantom windows from any line in the canny edge map that resembles a window frame.

**Fix:** 
- Gen prompt includes: "Render ONLY the elements described — no extra windows or openings"
- Replicate prompt wrapper adds: "no extra windows" to tail
- Negative prompt includes "extra windows" when corrections are active

**File:** `app.py`, `utils/replicate_client.py`

---

#### 6. Correction Flow Was Broken
**Problem:** `submitCorrection()` was calling `generateFromPlans()` WITHOUT a vision override — so GPT-4 Vision re-ran from scratch, ignored the user's corrections entirely, and produced a fresh (wrong) analysis.

**Fix:** Corrections now:
1. Take the current vision text from the textarea
2. Prepend `CRITICAL CORRECTIONS — the following MUST be applied: {user notes}`
3. Call `generateFromPlans(correctedVision)` — uses the vision override path
4. Backend skips GPT-4 Vision entirely, uses corrected text as-is
5. Guidance and control_strength are boosted for correction renders

**Files:** `templates/image_generator.html` (~line 2323), `app.py`

---

#### 7. Fullscreen Correction Modal
**Problem:** The correction paint UI was crammed into the side-by-side compare panel — images were tiny, impossible to paint accurately.

**Fix:** Replaced with a **fullscreen dark modal** (`#correction-modal`):
- Fixed overlay covers entire viewport
- Render image shown at full width (max 1200px)
- Canvas overlay sized exactly to image for pixel-accurate painting
- Frosted glass toolbar at bottom: brush size, undo, clear, description, re-generate
- Close button top-right
- Body scroll locked while modal is open

**File:** `templates/image_generator.html` (~lines 1228-1260)

---

#### 8. Custom Zones Now Have Product Assignment
**Problem:** The ＋ Add Zone button only asked for a name (via `prompt()`). No way to assign a product/material, so the AI didn't know what to render on custom zones.

**Fix:** Replaced `prompt()` with a proper modal dialog:
- **Zone Name** input (e.g. "Feature Wall", "Fascia")
- **Product / Material** input (e.g. "James Hardie Scyon Axon 133mm in Dulux Monument")
- Product stored in `plansSelections[zoneKey]` and included in material prompt
- Zone swatch shows product tag (🏷) with tooltip
- Backend formats custom zones as `"Feature Wall zone: James Hardie Scyon Axon..."` in the AI prompt

**Files:** `templates/image_generator.html` (~lines 1810-1875), `app.py` (~line 1069)

---

#### 9. Editable Vision Analysis + Re-generate
**Problem:** The AI's architectural interpretation was read-only — users couldn't fix misinterpretations.

**Fix:** 
- Vision output displayed in editable `<textarea>` (id: `vision-insight-text`)
- "Re-generate with edits" button appears after render
- Calls `generateFromPlans(editedText)` with the user's corrected text
- Backend skips GPT-4 Vision when `vision_override` is provided

**Files:** `templates/image_generator.html`, `app.py`

---

### ⚠️ Known Limitations / Still Needs Work

1. **Structural fidelity still imperfect** — Even with `control_strength: 0.85`, the xlabs model may still merge closely-spaced elements (e.g. two thin posts rendered as one). May need to test higher values (0.9-1.0) or pre-process the elevation to thicken key structural lines.

2. **Image quality trade-off** — `flux-dev-controlnet` may produce slightly lower quality than `flux-canny-pro`. If structure is now good but quality drops, consider a two-pass approach: structural render first, then quality upscale.

3. **GPT-4 Vision still guesses** — Even with the few-shot example, GPT-4 may miscount elements or add features. The editable textarea is the user's safety net for manual corrections.

4. **No true inpainting** — The "Correct This Render" flow re-generates the entire image with a modified prompt. A true inpainting model would only re-generate the masked area while keeping the rest identical. Could integrate `flux-fill-pro` or similar in future.

5. **Custom zones are session-only** — Zone names and product assignments are lost on page refresh. Could persist to `localStorage`.

6. **ControlNet + Canny edge detection** — Thin lines in elevation drawings (posts, fascia edges) produce weak canny signals. Pre-processing the elevation to enhance/thicken structural lines before sending to Replicate could significantly improve results.

---

### 📁 Files Modified This Session

| File | Changes |
|------|---------|
| `utils/replicate_client.py` | Full rewrite — xlabs engine primary, flux-canny-pro fallback, control_strength param |
| `app.py` | Vision prompt overhaul, gen prompt reorder, correction guidance boost, custom zone labels |
| `templates/image_generator.html` | Fullscreen correction modal, editable vision textarea, zone product dialog, correction override flow |

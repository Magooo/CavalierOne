# DESIGN.md — Cavalier Homes

> Drop this file in your project root. AI coding agents will read it to generate
> any UI that is automatically on-brand for Cavalier Homes.
>
> Source: Extracted from cavalierhomes.com.au + brand_config.json
> Format: Google Stitch DESIGN.md (https://stitch.withgoogle.com/docs/design-md/format/)

---

## Brand Identity

**Brand name:** Cavalier Homes  
**Tagline:** Building homes people love to live in  
**Brand monogram:** `ch` (lowercase, used as a standalone mark in footers and watermarks)  
**Aesthetic:** Sophisticated Lifestyle — balances traditional elegance with modern Australian residential design. Premium but approachable. Never corporate, always warm.  
**Tone of voice:** Warm, confident, aspirational. Family-first. Speaks to first home buyers and upgraders equally.

---

## Color Palette

### Primary Colors
| Token | Name | Hex | Usage |
|---|---|---|---|
| `--color-accent` | Terracotta | `#AD4B43` | Primary CTA buttons, active tabs, brand accent, hover states |
| `--color-black` | Black | `#000000` | Headings, primary text on light backgrounds |
| `--color-white` | White | `#FFFFFF` | Card backgrounds, reversed text on dark surfaces |

### Secondary Colors
| Token | Name | Hex | Usage |
|---|---|---|---|
| `--color-text` | Charcoal | `#212121` | Body copy, high-readability text |
| `--color-text-muted` | Dark Grey | `#54595F` | Labels, metadata, secondary UI text |
| `--color-mid` | Medium Grey | `#AEA299` | Borders, dividers, subtle decorative elements |
| `--color-bg-light` | Warm Light | `#EEEDEC` | Section backgrounds, page backgrounds, cards on dark |
| `--color-bg-muted` | Off-White | `#F7F7F7` | Alternating section backgrounds |
| `--color-footer` | Deep Charcoal | `#222222` | Footer background, dark sections |

### CSS Custom Properties (Root)
```css
:root {
  --color-accent:       #AD4B43;
  --color-black:        #000000;
  --color-white:        #FFFFFF;
  --color-text:         #212121;
  --color-text-muted:   #54595F;
  --color-mid:          #AEA299;
  --color-bg-light:     #EEEDEC;
  --color-bg-muted:     #F7F7F7;
  --color-footer:       #222222;
}
```

---

## Typography

### Font Families
| Role | Font | Fallback Stack |
|---|---|---|
| **Display / Headings** | Playfair Display | `'Playfair Display', Georgia, 'Times New Roman', serif` |
| **Body / UI** | ITC Avant Garde Gothic | `'Avant Garde Gothic', 'Century Gothic', 'Source Sans Pro', 'Open Sans', Arial, sans-serif` |

> **Note:** Playfair Display is loaded via Google Fonts. Avant Garde Gothic is the brand-specified primary UI font; Century Gothic is the approved Windows substitute.

### Type Scale
| Element | Font | Size | Weight | Letter Spacing | Line Height |
|---|---|---|---|---|---|
| H1 Hero | Playfair Display | `60px` | `500` | `-0.5px` | `1.1` |
| H1 Page | Playfair Display | `48px` | `500` | `-0.3px` | `1.15` |
| H2 Section | Playfair Display | `36px` | `400` | `0` | `1.2` |
| H3 Card | Playfair Display | `24px` | `400` | `0.5px` | `1.3` |
| Body Large | Avant Garde / Century Gothic | `18px` | `400` | `0` | `1.6` |
| Body Base | Avant Garde / Century Gothic | `15px` | `400` | `0` | `1.55` |
| Small / Meta | Avant Garde / Century Gothic | `13px` | `400` | `0.2px` | `1.5` |
| Button | Avant Garde / Century Gothic | `14px` | `600` | `1px` | `1` |
| Nav Link | Avant Garde / Century Gothic | `15px` | `400` | `0.5px` | `1` |
| Card Label (e.g. "ALPINE") | Playfair Display | `28px` | `400` | `4px` | `1` |

### Typography Rules
- Headings in Playfair Display evoke prestige and craft
- UI labels (buttons, nav, specs) use Avant Garde/Century Gothic for clarity
- **Never mix two serif fonts** in the same component
- Card home names are often ALL CAPS with wide letter-spacing (`4px+`)
- Use `font-weight: 400` for Playfair Display — avoid bold weights (feels too heavy)

---

## Spacing & Layout

### Grid
```css
--container-max:     1200px;
--container-padding: 0 24px;
--grid-gap:          24px;
```

### Spacing Scale
```css
--space-xs:   4px;
--space-sm:   8px;
--space-md:   16px;
--space-lg:   32px;
--space-xl:   60px;
--space-2xl:  100px;
```

- **Section vertical padding:** `60px–100px` for spacious, premium feel
- **Card padding:** `24px` internal, `16px` gap between cards
- **Hero sections:** Full-width, 100vh or large fixed heights with image fills

---

## UI Components

### Buttons

#### Primary CTA (Terracotta)
```css
.btn-primary {
  background-color: #AD4B43;
  color: #FFFFFF;
  border: none;
  border-radius: 3px;
  padding: 14px 32px;
  font-family: 'Century Gothic', 'Avant Garde Gothic', sans-serif;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.btn-primary:hover {
  background-color: #8e3c35;
}
```

#### Secondary (Outlined)
```css
.btn-secondary {
  background-color: transparent;
  color: #AD4B43;
  border: 2px solid #AD4B43;
  border-radius: 3px;
  padding: 12px 28px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
}
.btn-secondary:hover {
  background-color: #AD4B43;
  color: #FFFFFF;
}
```

#### Ghost (Dark surfaces)
```css
.btn-ghost {
  background-color: transparent;
  color: #FFFFFF;
  border: 2px solid #FFFFFF;
  border-radius: 3px;
  padding: 12px 28px;
}
```

### Cards — Home Design Listing Card

A horizontal or vertical card showing a house design. Contains:
- **Hero image** (facade render or lifestyle photo) with a FACADES / FLOORPLANS tab toggle
- **Active tab** uses `--color-accent` (#AD4B43) as background
- **Home name** — ALL CAPS, Playfair Display, letter-spacing 4px
- **Spec row** — Bed / Bath / Garage icons (thin line, dark charcoal), with count
- **CTA** — "View More" or "Enquire" button

```css
.home-card {
  background: #FFFFFF;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.home-card__tab-active {
  background-color: #AD4B43;
  color: #FFFFFF;
}
.home-card__name {
  font-family: 'Playfair Display', serif;
  font-size: 26px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: #212121;
}
.home-card__specs {
  display: flex;
  gap: 16px;
  color: #54595F;
  font-size: 14px;
}
```

### Navigation

- **Background:** White (`#FFFFFF`)
- **Logo:** Left or centred
- **Links:** 15px, Avant Garde, no transform, hover → `#AD4B43`
- **Mobile:** Hamburger menu, full-screen overlay
- **Sticky:** Yes — fixed top with subtle drop shadow on scroll

```css
.navbar {
  background: #FFFFFF;
  padding: 20px 40px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
}
.navbar__link {
  font-family: 'Century Gothic', sans-serif;
  font-size: 15px;
  color: #212121;
  text-decoration: none;
  letter-spacing: 0.5px;
}
.navbar__link:hover,
.navbar__link.active {
  color: #AD4B43;
}
```

### Footer
```css
.footer {
  background-color: #222222;
  color: #EEEDEC;
  padding: 60px 40px 32px;
  font-family: 'Century Gothic', sans-serif;
  font-size: 14px;
}
.footer__heading {
  font-family: 'Playfair Display', serif;
  color: #FFFFFF;
  font-size: 18px;
  margin-bottom: 16px;
}
.footer__link {
  color: #AEA299;
  text-decoration: none;
}
.footer__link:hover { color: #FFFFFF; }
.footer__monogram {
  font-family: 'Playfair Display', serif;
  font-size: 32px;
  color: #AEA299;
  letter-spacing: 2px;
}
/* The 'ch' monogram lives in the footer bottom-right */
```

### Section Dividers / Backgrounds

- **Light section:** Background `#EEEDEC`, text `#212121`
- **White section:** Background `#FFFFFF`, text `#212121`
- **Dark section:** Background `#222222`, text `#EEEDEC`
- **Accent band:** Background `#AD4B43`, text `#FFFFFF` (use sparingly for CTAs)

---

## Imagery Rules

> All images must match these rules to be considered on-brand.

1. **Style:** Fresh, modern, bright and well-lit. No dark, moody, or high-contrast edits.
2. **Content:** Combination of detail shots (fixtures, materials) and interior/exterior lifestyle shots.
3. **Renders:** Must use a consistent front-on elevation angle. No dramatic drone angles.
4. **Lifestyle:** Aspirational but family-friendly. Warm natural light. No people required.
5. **Colour temperature:** Warm-neutral. Avoid cool/blue-toned whites.
6. **Format:** Landscape (16:9) for hero images. Square (1:1) for social. Portrait (4:5) for social stories.

---

## Logo Usage

- **Primary logo:** `static/brand_assets/logo_primary_page5.png`
- **Logo reversed (on dark):** White version for use on `#222222` or `#AD4B43` backgrounds
- **Monogram:** `ch` in Playfair Display, used as a compact brand mark in footers and watermarks
- **Clear space:** Minimum clear space = 1× the height of the `h` in the monogram
- **Never:** Stretch, recolour (other than white reverse), or place on a busy background

---

## Tone & Copy Style

- **Headlines:** Short, confident, aspirational. E.g. "Your dream home. Built right."
- **Body:** Warm, informative, never pushy. Use "you" and "your" to speak directly.
- **CTAs:** Action-first. "Explore Home Designs" > "Click Here". "Book a Consultation" > "Contact Us".
- **Avoid:** Corporate jargon, passive voice, all-caps body text.
- **Disclaimers:** Always include: *"Cavalier Homes are independently owned and operated. Room sizes shown are approximate only."*

---

## Google Fonts Import

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500&display=swap" rel="stylesheet">
```

---

## Quick Reference Cheatsheet

```
ACCENT:      #AD4B43   ← buttons, active states, brand pops
TEXT:        #212121   ← all body copy
TEXT-MUTED:  #54595F   ← labels, metadata
BG-LIGHT:    #EEEDEC   ← page/section backgrounds
FOOTER:      #222222   ← dark sections

DISPLAY FONT: Playfair Display (headings, home names)
BODY FONT:    Century Gothic / Avant Garde Gothic (all UI)

BORDER-RADIUS: 3px (buttons), 4px (cards)
MAX-WIDTH: 1200px
```

---
name: interior-vibing
description: >
  Generate professional, purposeful interior design renderings that solve specific user problems.
  Use this skill when a user uploads a room photo and wants design recommendations, staging plans,
  or visual concepts for any interior space. This skill ensures every rendering is specific to the
  room's architecture, the user's goal (sell, rent, host, refresh), and real purchasable items —
  never generic "modern living room" output. Trigger on: room photos, interior design requests,
  staging advice, rental optimization, Airbnb improvement, home sale prep, or any "how should I
  design this room" question.
---

# Interior Vibing

A self-executing skill. User uploads a room photo + writes what they want. The skill
analyzes the room, generates a redesign rendering via Gemini, and produces a polished
click-through presentation deck — all automatically.

---

## Execution Flow

When a user uploads a room photo (with or without a text prompt):

```
STEP 1: Setup
  → Run: pip install google-genai Pillow --break-system-packages -q
  → Ensure GEMINI_API_KEY is set (check .env file, then env var)
  → Create temp folder: .stilo-output/ in the working directory
  → Copy uploaded photo to .stilo-output/before.jpg

STEP 2: Analyze the Room (gemini-2.5-flash)
  → Run: python scripts/render.py analyze --image .stilo-output/before.jpg
  → Read the structured analysis output
  → Identify: room type, fixed elements, biggest asset, biggest problem

STEP 3: Determine Purpose
  → If user stated a goal → use it
  → If ambiguous → ask: "What's the goal — Airbnb, rental, selling, or personal refresh?"
  → Map to archetype: STR_HERO | LTR_APPEAL | SELL_READY | REFRESH

STEP 4: Write a Purposeful Prompt (NOT generic — see Prompt Rules below)
  → Incorporate room analysis (fixed elements, dimensions, light)
  → Incorporate purpose (what viewer needs to feel)
  → Incorporate specific items with materials, colors, dimensions
  → Minimum 80 words — if shorter, it's not specific enough

STEP 5: Generate the Rendering (gemini-3-pro-image-preview / Nano Banana Pro)
  → Run: python scripts/render.py render \
      --image .stilo-output/before.jpg \
      --prompt "your detailed prompt" \
      --purpose "archetype" \
      --style "style direction" \
      --aspect-ratio "4:3" \
      --resolution "2K" \
      --output .stilo-output/after.png
  → Supports: 1K, 2K, 4K resolution
  → Aspect ratios: 1:1, 3:2, 4:3, 16:9, etc.

STEP 6: Build the Presentation Deck
  → Generate an HTML artifact (click-through deck, NOT a scroll page)
  → Embed before photo and after rendering as base64 images
  → Follow the Deck Structure and Frontend Design Guidelines below
  → Present to user
```

---

## Room Analysis (Step 2)

When the analyze script returns, supplement with your own observations. Extract:

- **Room type + estimated dimensions** (use furniture as scale: sofa ≈ 84", door ≈ 80"×32")
- **Floor:** material, color tone, condition (1-5)
- **Walls:** color, condition, features (molding, brick, texture)
- **Light:** window count, orientation (from shadow direction), quality
- **Fixed elements:** counters, cabinets, tile, built-ins — these are CONSTRAINTS
- **Architectural style + era**
- **Best asset:** the single best design feature
- **Worst problem:** the single biggest issue to solve
- **Missing essentials:** what the room clearly needs but doesn't have

Be precise:
- ❌ "hardwood floors"
- ✅ "medium-warm white oak, ~5-inch planks, satin finish, minor wear near entry"

---

## Purpose Archetypes (Step 3)

| Goal | Design For | Key Psychology |
|------|-----------|---------------|
| **STR_HERO** (Airbnb listing photos) | Stop the scroll. One hero moment per room. | Viewer sees 20+ listings in 5 min. 1.5 seconds to decide. |
| **STR_FUNCTIONAL** (Airbnb guest experience) | Comfort + durability + review triggers. | "Exactly as pictured" + "so comfortable" = 5 stars. |
| **LTR_APPEAL** (Long-term rental) | "I can see myself living here." 80% neutral, 20% personality. | Tenant projects their OWN life into the space. |
| **SELL_READY** (Home sale) | Eliminate doubt. Every surface says "cared for." | Buyer is simultaneously emotional and calculating. |
| **REFRESH** (Personal) | Solve what bothers them. Design for how they live. | No ROI — pure satisfaction. |

---

## Prompt Writing Rules (Step 4)

### Formula
```
PROMPT = ROOM_CONTEXT + DESIGN_INTENT + SPECIFIC_ITEMS + STYLE + PHOTO_QUALITY
```

### BAD vs GOOD

❌ **BAD (generic, will fail):**
```
"Modern bedroom design with nice furniture and good lighting"
```

✅ **GOOD (specific, purposeful):**
```
"Professional interior photograph of a redesigned bedroom for Airbnb listing.
Keep the existing medium-warm oak hardwood floors and two north-facing windows.
Add: king bed with white textured linen duvet, layered with an oatmeal knit
throw and 5 pillows (2 euro shams in cream, 2 sleeping pillows, 1 lumbar in
sage green). Two round oak nightstands with warm brass table lamps with linen
shades. 9×12 hand-loomed wool rug in warm ivory under the bed. Large abstract
art (40×30) in terracotta, sand, and sage above the headboard. Fiddle leaf fig
in ceramic pot by the window. Warm afternoon light through sheer linen curtains.
Style: warm Scandinavian, organic textures, matte brass.
Shot from doorway toward bed and windows. Magazine editorial quality."
```

### Prompt Checklist
- □ References the room's FIXED elements (floors, walls, windows)
- □ Names specific items with materials and colors
- □ Includes color descriptions (hex or detailed name)
- □ Specifies dimensions or scale
- □ States the purpose
- □ Describes lighting
- □ Specifies camera angle
- □ 80+ words minimum

### Banned Words (produce generic output)
"nice" / "lovely" / "modern" alone / "cozy" alone / "pop of color" / "statement piece" / "declutter" without specifics

---

## Presentation Deck Structure (Step 6)

The output is a click-through HTML presentation deck. NOT a scrolling page.
Click or arrow keys to advance. Each slide = one clear point.

### Slide Sequence (8 slides)

**SLIDE 1 — TITLE**
Full-bleed before photo as background with dark overlay (rgba(0,0,0,0.55)).
Large serif headline centered: room type + purpose (e.g., "Living Room · Airbnb Staging").
Subtitle below: "Interior Vibing Design Report".
Small date at bottom.

**SLIDE 2 — BEFORE**
The uploaded photo displayed large and clean. No filter.
Label above: "BEFORE" in small caps, muted color.
Caption below: room type, estimated size, condition score.

**SLIDE 3 — ROOM ANALYSIS**
Key stats as compact elegant cards in a row:
```
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ 14×12  │ │ South  │ │ Oak    │ │ 3/5    │
│ feet   │ │ light  │ │ floors │ │ cond.  │
└────────┘ └────────┘ └────────┘ └────────┘
```
Below the stats, two callout cards side by side:
- ✦ Best Asset: specific finding
- ✦ Biggest Problem: specific finding

**SLIDE 4 — DESIGN CONCEPT**
Style direction name as large serif headline.
Color palette: 5 swatches in a row with hex labels below each.
One paragraph design narrative (3-4 sentences, specific to this room).
Purpose badge: pill-shaped, accent color, "Optimized for: Airbnb Listing Photos".

**SLIDE 5 — AFTER**
The Gemini-generated rendering displayed large.
Label above: "AFTER" in small caps.
Caption below: style name + total investment range.

**SLIDE 6 — BEFORE → AFTER**
Side by side (desktop) or stacked (mobile).
Thin labels: "BEFORE" / "AFTER" above each.
Numbered annotation callouts on the After image pointing to key changes:
① ② ③ ④ with a legend below listing what each number refers to.

**SLIDE 7 — SHOPPING LIST**
Items ranked by impact. Each as a compact card:
```
#1 · 9×12 Wool-Blend Rug · Warm Ivory
WHY: bridges oak floors and grey sofa
Budget $79-149 · Mid $199-350 · Premium $400-800
Impact ●●●●●●●●○○ 7.8
```
Show 5-7 items. Cards should fit on one slide without scrolling.
If more than 5 items, use two columns or split across two slides.

**SLIDE 8 — INVESTMENT SUMMARY**
Three-column budget comparison:
```
Budget        Recommended ★    Premium
$450-700      $1,200-1,800     $2,500-4,000
+5-7%         +10-14%          +15-20%
4.2mo payback 2.3mo payback    2.8mo payback
```
★ badge on lowest payback period column.
Closing statement: "Estimated impact: +X% booking rate / -Y vacant days".
Footer: "Generated by Interior Vibing · [date]"

---

## Navigation & Interaction

```
CLICK/TAP:
  - Click right half of screen → next slide
  - Click left half of screen → previous slide

KEYBOARD:
  - → or Space or Enter → next slide
  - ← or Backspace → previous slide

PROGRESS INDICATOR:
  - Small dots centered at bottom, 24px from edge
  - Active dot: filled, accent color (#C65D3E)
  - Inactive dots: border only, muted (#E5E0D8)
  - 8px diameter, 12px gap between dots

SLIDE COUNTER:
  - Bottom-right corner: "3 / 8" in mono font, muted color

TRANSITIONS:
  - Crossfade between slides: opacity 0→1, 0.4s ease-out
  - Content within slide: staggered fade-in (0.1s intervals)
    Title appears first → stats → body → details
  - NO horizontal sliding
  - NO 3D transforms
  - NO auto-advance
```

---

## Frontend Design Guidelines

### Philosophy: "Architectural Editorial"
Like a high-end architecture magazine — generous space, precise typography,
warm materials palette, confident restraint.

### Colors
```css
:root {
  --bg-primary: #F7F5F0;       /* Warm parchment — NEVER pure white */
  --bg-secondary: #EFECE5;
  --bg-card: #FFFFFF;
  --bg-dark: #1A1A1A;           /* Title slide, dark overlays */

  --text-primary: #1A1A1A;
  --text-secondary: #6B6560;
  --text-muted: #9B9590;
  --text-on-dark: #F7F5F0;

  --accent: #C65D3E;            /* Terracotta — the ONE accent */
  --accent-light: #E8A08C;
  --secondary: #8B9D83;         /* Sage — supporting only */
  --data: #5B7B9A;              /* Slate blue for numbers */

  --border: #E5E0D8;
  --shadow: rgba(26, 26, 26, 0.06);
}
```

### Typography
```css
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

--font-display: 'DM Serif Display', Georgia, serif;  /* Slide titles */
--font-body: 'DM Sans', sans-serif;                   /* Body text */
--font-mono: 'JetBrains Mono', monospace;             /* Prices, data */
```

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Slide title | display | 2.5rem | normal | primary or on-dark |
| Section label | body | 0.75rem | 600 | accent, uppercase, 0.1em tracking |
| Body text | body | 0.9375rem | 400 | primary, line-height 1.6 |
| Stat value | mono | 1.25rem | 500 | primary |
| Stat label | body | 0.75rem | 400 | muted |
| Price | mono | 0.8125rem | 400 | secondary |
| Caption | body | 0.8125rem | 400 | muted |
| Slide counter | mono | 0.75rem | 400 | muted |

### Layout Rules

**Every slide:**
- Full viewport: 100vw × 100vh, overflow hidden
- Content max-width: 900px, centered
- Padding: 48px minimum (64px on desktop)
- No scrolling within slides — if content doesn't fit, split into two slides

**Photo slides (Before, After):**
- Photo: 80% of slide height max, centered
- Rounded corners: 8px
- Shadow: 0 8px 32px rgba(26,26,26,0.12)
- Label above: small caps, muted, 0.75rem

**Stat cards:**
- White bg, 1px border, 12px radius, 20px padding
- Shadow: 0 2px 8px var(--shadow)
- Value above in mono, label below in muted

**Shopping list cards:**
- Rank badge: 28px circle, accent bg, white number
- Item name: body font, 600 weight
- Why: body font, regular, secondary color
- Prices in mono, three columns
- Impact dots: 8px, accent filled / border empty, 4px gap

**Color palette swatches:**
- 40×40px squares, 4px border-radius
- 8px gap between swatches
- Hex label below in mono, muted color

### Image Handling
- Embed as base64 directly in HTML (self-contained, no external files)
- Before photo: no filter, as-is
- After rendering: no additional filter
- Title slide: before photo as background with `background-size: cover` + dark overlay

### What NOT to Do
- ❌ Scrolling page (this is a DECK)
- ❌ Horizontal slide transitions
- ❌ Auto-advancing
- ❌ Purple gradients or neon
- ❌ Inter, Roboto, Arial, system fonts
- ❌ Heavy drop shadows (>12% opacity)
- ❌ Product grid layouts
- ❌ More than one accent color
- ❌ Content that requires scrolling within a slide
- ❌ Background music

---

## Anti-Generic Guardrails

**NEVER recommend without specificity:**
- ❌ "Pop of color" → ✅ "Terracotta (#C65D3E) through linen lumbar pillow and ceramic vase"
- ❌ "Statement piece" → ✅ "40×30 abstract art in earth tones, centered 57" from floor"
- ❌ "Cozy textiles" → ✅ "Oatmeal knit cotton throw (50×60) draped at foot of bed"
- ❌ "Gallery wall" → ✅ one large piece (photographs better)

**EVERY recommendation answers:**
- Why THIS item? (references analysis)
- Why THIS room? (solves a spatial problem)
- Why THIS purpose? (serves the viewer)
- How much? (real prices, real retailers)
- How impactful? (scored with reasoning)

---

## ROI Data

**Benchmarks:**
- Pro photos vs phone: +20-40% booking rate
- Staged bedroom (STR): +$8-20/night, 1-3mo payback
- Fresh paint (rental): $150-500, -5-15 vacancy days
- Staged homes: +1-5% price, -33-50% time on market

**Budget calibration:**
- <$200K property → $500-2,000 staging
- $200-500K → $1,500-5,000
- STR → 2-3 months revenue · LTR → 1-2 months rent

**High-ROI items:**
- STR: bedding → lighting → large art → rug → pillows
- Rental: paint → lighting → hardware → window treatments → entry
- Sale: declutter → counters → paint → furniture layout → bathroom

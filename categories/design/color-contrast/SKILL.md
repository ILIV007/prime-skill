---
name: color-contrast
description: Measure, audit, and repair color contrast for accessibility. Use when checking whether colors meet WCAG AA/AAA, auditing a codebase or stylesheet for contrast failures, fixing unreadable text, picking accessible colors for a palette or design system, reviewing dark mode legibility, or answering questions about contrast ratios and APCA. Triggers on "contrast", "WCAG", "AA/AAA", "a11y color", "accessible palette", "is this readable", "color blind", "dark mode contrast".
license: MIT
metadata:
  version: "1.0"
---

# Color Contrast

Measure contrast with two metrics, audit real source trees for failures, and repair them with the smallest color change that works.

Paths below are relative to this skill's own directory — resolve them against wherever this `SKILL.md` lives, not the user's working directory. The scripts need no install and no dependencies; run them with `python3` in place.

**Never estimate a contrast ratio by eye or from memory.** The math is not intuitive — mid-greys that look fine routinely fail, and dark-mode pairs that measure well are often unreadable. Run the scripts.

## The two metrics, and when each one governs

| | WCAG 2.x ratio | APCA Lc |
|---|---|---|
| Range | 1:1 – 21:1 | −108 – +106 |
| Answers | "Is this legally compliant?" | "Can a person actually read this?" |
| Status | Normative in EN 301 549, Section 508, ADA Title II | WCAG 3 candidate, not yet normative |
| Direction | Symmetric | Signed: + is dark-on-light, − is light-on-dark |
| Known failure | Overstates contrast on dark backgrounds; ignores font size and weight | Not accepted by any regulator |

**Decision rule.** Compliance is a floor, not a goal.

1. WCAG 2.x decides pass/fail. It is what audits and lawsuits use.
2. APCA decides how much better than the floor you should aim. When they disagree, report both and say which one governs the decision at hand.
3. Never present APCA as a compliance result, and never tell someone a WCAG pass means the text is readable.

The disagreement is real and worth surfacing. `#989898` on black scores **7.28:1 — WCAG AAA** — while APCA rates it **Lc −46.7**, barely a third of the Lc 75 floor for body text. Dark mode is where this bites hardest.

## Thresholds

**WCAG 2.x** — body text 4.5:1 (AA) / 7:1 (AAA). Large text 3:1 (AA) / 4.5:1 (AAA), where large means ≥24px, or ≥18.66px bold. UI components and meaningful graphics need 3:1 (SC 1.4.11). Logos and disabled controls are exempt.

**APCA** — Lc 90 preferred for body text, Lc 75 minimum for body text, Lc 60 for other content text, Lc 45 for headlines, Lc 30 absolute floor for any text, Lc 15 for non-text. Treat anything under Lc 15 as invisible.

## Checking a pair

```bash
python3 scripts/contrast.py check "#767676" white
python3 scripts/contrast.py check "#aaa" "#222" --large --json
```

Reports both metrics, every WCAG threshold, polarity, and the smallest font the Lc value supports. Exit code 1 if it fails AA.

## Auditing a codebase

This is the main workflow when someone points at a project.

```bash
python3 scripts/audit.py scan  src/            # inventory every color, with themes
python3 scripts/audit.py check src/            # failures, worst first
python3 scripts/audit.py check src/ --target AAA --json
python3 scripts/audit.py check src/ --fix      # rewrite literal values in place
```

Handles CSS, SCSS, LESS, inline `style` attributes, and JS/TS style objects. Resolves `var()`, `$var`, `@var`, `hsl()`, and `oklch()`. **Audits light and dark themes separately**, because a flat variable map would let one theme's definition mask the other's bug.

Each finding carries a confidence level. Respect it:

- `same-block` — one rule declares both colors. Certain.
- `ancestor` — a parent block declares the background. Near-certain.
- `page` — a bare foreground assumed to sit on the detected `body` background. Usually right, occasionally not. Default includes these; pass `--confidence same-block` to see only certainties.

### Before running `--fix`

`--fix` only rewrites **literal** values, and it verifies each replacement still passes once rounded to 8-bit hex. It deliberately refuses to touch values that come from a variable, because one token feeds many surfaces and changing it silently shifts all of them. Those findings are reported with the token's location for a human decision.

Three rules:

1. **Show the findings first.** Get agreement before writing.
2. **Never auto-fix brand colors** — a logo blue or a primary button is a business decision. Surface it and ask.
3. **For design tokens, fix the definition, not the usage.** Then re-audit every theme, because a token that fixes light mode can break dark.

Run the audit again after fixing. It should converge, and the survivors should all be the ones that need a human.

## Repairing a single pair

```bash
python3 scripts/contrast.py fix "#777777" white --target AAA
python3 scripts/contrast.py fix "#59f" "#111" --metric apca --target 75 --mode both
```

Search runs in OKLab lightness, so hue and chroma survive — a gold stays gold instead of sliding olive, which is what HSL-based adjustment does. Both directions are tried and the smaller perceptual change wins. `--mode both` splits the movement across text and background, which shifts each one less when neither is fixed by brand.

If it reports failure, the target is unreachable by lightness alone. Say so and offer the real options: change the hue, change the other color, or increase font size and weight to lower the requirement.

## Using it as a library

```python
from contrast import contrast_ratio, apca_contrast, evaluate_wcag, adjust

contrast_ratio("#767676", "white")            # 4.54
apca_contrast("#767676", "white")             # 71.6
evaluate_wcag("#767676", "white").passes_aa   # True
adjust("#777", "white", target="AAA").foreground.hex
```

Accepts hex, `rgb()`, `hsl()`, `oklch()`, `oklab()`, and CSS color names. Translucent foregrounds are composited over the background automatically, in linear light. A translucent *background* raises an error rather than guessing — composite it yourself first.

## Honest limits — state these, don't paper over them

- **Static pairing misses things.** Contrast created by the runtime cascade, JS-computed styles, framework utility classes, or text over images or gradients is invisible to the scanner. A clean report means "nothing I can see", not "nothing". Say this when reporting a clean result.
- **Text over an image or gradient has no single ratio.** Recommend a scrim, a solid backing, or a text shadow instead of a number.
- **Contrast is not all of color accessibility.** It says nothing about using color as the sole carrier of meaning (SC 1.4.1), which no ratio can detect.
- **Both metrics assume sRGB on a self-illuminated display.** They do not model print, ambient light, or wide-gamut displays.
- **APCA is unversioned in law.** Its constants are frozen (0.98G-4g, unchanged since 2021) but the conformance table is still a draft.

## Reference files

- `references/wcag2.md` — success criteria, exact thresholds, exceptions, the formula and why 0.05 is in it
- `references/apca.md` — the algorithm, its constants, Lc levels, the font lookup table
- `references/research.md` — the evidence base: where 4.5:1 came from, the documented failures of WCAG 2.x, why APCA exists, and what is still contested

## Tests

```bash
python3 scripts/test_contrast.py && python3 scripts/test_audit.py
```

Covers parsing, both metrics against reference anchors, alpha compositing, quantization survival, a 2,904-combination adjustment sweep, and end-to-end audit and repair on a fixture tree.

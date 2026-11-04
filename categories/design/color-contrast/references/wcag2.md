# WCAG 2.x contrast

The normative standard. Every accessibility regulation currently in force points here, so this is what decides pass or fail.

## Success criteria

### SC 1.4.3 Contrast (Minimum) — Level AA

> The visual presentation of text and images of text has a contrast ratio of at least 4.5:1

Exceptions:

- **Large text** — 3:1 is enough. Large means at least 18 point, or 14 point bold. WCAG gives the conversion as `1pt = 1.333px`, so **24px, or 18.66px bold**. For CJK fonts, whatever size is equivalent.
- **Incidental** — text in an inactive UI component, pure decoration, invisible to everyone, or part of a picture with significant other visual content. No requirement.
- **Logotypes** — text that is part of a logo or brand name. No requirement.

### SC 1.4.6 Contrast (Enhanced) — Level AAA

7:1 for body text, 4.5:1 for large text. Same three exceptions.

### SC 1.4.11 Non-text Contrast — Level AA

3:1 against adjacent colors for:

- **UI components** — the visual information needed to identify a control and its state. Focus indicators, checkbox borders, input outlines, toggle tracks.
- **Graphical objects** — the parts of a graphic required to understand the content. A chart's data series, a meaningful icon.

Decorative graphics and disabled controls are exempt. Note the phrase *adjacent colors*: a button border must contrast with what is on **both** sides of it, not just the button fill.

## The formula

Relative luminance, per channel, from gamma-encoded sRGB in [0, 1]:

```
C_lin = C / 12.92                    if C <= 0.04045
C_lin = ((C + 0.055) / 1.055) ^ 2.4  otherwise

L = 0.2126 * R_lin + 0.7152 * G_lin + 0.0722 * B_lin
```

Contrast ratio, with L1 the lighter of the two:

```
ratio = (L1 + 0.05) / (L2 + 0.05)
```

Three details that matter in implementation:

1. **The coefficients are the rounded BT.709 values.** WCAG specifies 0.2126 / 0.7152 / 0.0722 exactly. APCA uses more precise ones. Do not mix them.
2. **The transfer function is the piecewise sRGB EOTF**, not a plain 2.4 power curve. APCA uses the plain curve. Again, do not mix.
3. **The 0.05 is a flare term** — it models ambient light reflecting off the screen, standing in for a 5% reflectance assumption. It is also the single reason the metric compresses so badly at the dark end: as both luminances approach zero, the ratio approaches 1 regardless of how different the colors look. This is the mathematical root of the dark-mode failure described in `research.md`.

## Where 4.5:1 comes from

WCAG's own rationale: 3:1 is the minimum recommended by ISO 9241-3 and ANSI-HFES-100-1988 for normal vision. The standard then multiplies by 1.5 to compensate for the contrast sensitivity loss that accompanies roughly 20/40 visual acuity — typical of a person around 80 years old.

```
3 (baseline for normal vision) × 1.5 (moderate acuity loss) = 4.5
```

7:1 for AAA compensates for roughly 20/80 acuity, the point at which most jurisdictions consider someone to have low vision.

Two things follow. First, the value is a policy judgement built on a 1980s ergonomics baseline, not a measurement. Second, it is calibrated for acuity loss, not for the many other causes of reduced contrast sensitivity — cataracts, glare, low-quality displays, sunlight.

## Reference values worth remembering

| Pair | Ratio | Verdict |
|---|---|---|
| `#000000` on `#ffffff` | 21.00:1 | The sRGB maximum |
| `#767676` on `#ffffff` | 4.54:1 | The lightest grey that clears AA on white |
| `#949494` on `#ffffff` | 3.03:1 | The lightest grey that clears 3:1 on white |
| `#595959` on `#ffffff` | 7.00:1 | The lightest grey that clears AAA on white |
| `#ffffff` on `#0073e6` | 4.57:1 | A typical brand blue, barely passing |

On white, `#767676` is the practical cutoff for placeholder and secondary text. Anything lighter fails AA.

## Common implementation mistakes

- **Comparing gamma-encoded values directly.** The transfer function is not optional; skipping it inflates dark-color ratios.
- **Blending alpha in gamma space.** Compositing translucent text must happen in linear light, as a GPU does. Naive blending darkens the result and reports a ratio the user never sees.
- **Assuming order matters.** The ratio is symmetric. `contrast(a, b) == contrast(b, a)`. APCA is *not*, which trips people who use both.
- **Testing only the light theme.** Most contrast bugs in modern codebases are in dark mode.
- **Rounding after the check.** A color that passes at float precision can fail once written as `#rrggbb`. Verify the rounded value.

## Sources

- [WCAG 2.2 — SC 1.4.3, 1.4.6, 1.4.11](https://www.w3.org/TR/WCAG22/#contrast-minimum)
- [Understanding SC 1.4.3 — rationale and pixel equivalents](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [Relative luminance definition](https://www.w3.org/TR/WCAG22/#dfn-relative-luminance)

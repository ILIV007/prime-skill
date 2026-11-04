# APCA

The Accessible Perceptual Contrast Algorithm, by Andrew Somers (Myndex). Developed for WCAG 3 / Silver as the successor to the WCAG 2.x ratio.

**Status.** Not normative anywhere. It is a candidate method in a draft standard. Use it to make better design decisions, never to claim compliance.

## What it changes

APCA is a perceptual model rather than a photometric ratio. Three differences drive everything else:

1. **It is polarity-aware.** Dark-on-light and light-on-dark use different exponents, because the eye does not treat them symmetrically. Consequently `Lc(a, b) != -Lc(b, a)`. Argument order is meaningful: text first, background second.
2. **It models spatial frequency.** Thin and small glyphs carry less perceived contrast than thick, large ones. APCA outputs a value you look up against font size and weight, instead of one number for all text.
3. **It does not collapse at the dark end.** WCAG 2.x's `+0.05` flare term drives the ratio toward 1 as both colors approach black. APCA uses a soft clamp near black instead, which keeps dark-mode values meaningful.

## The algorithm

Version 0.1.9, exponent set `0.98G-4g-sRGB`. These constants have not changed since 2021-02-15.

```
mainTRC = 2.4                    blkThrs = 0.022      scaleBoW = 1.14
sRco = 0.2126729                 blkClmp = 1.414      scaleWoB = 1.14
sGco = 0.7151522                 deltaYmin = 0.0005   loBoWoffset = 0.027
sBco = 0.0721750                 loClip = 0.1         loWoBoffset = 0.027
normBG = 0.56   normTXT = 0.57   revTXT = 0.62        revBG = 0.65
```

**Step 1 — screen luminance.** Note the plain 2.4 power curve, *not* the sRGB piecewise function, and the unrounded coefficients. Both differ from WCAG 2.x.

```
Ys = sRco*(R/255)^2.4 + sGco*(G/255)^2.4 + sBco*(B/255)^2.4
```

**Step 2 — soft clamp near black.** Models display flare and scatter in the eye.

```
Y' = Y                              if Y > 0.022
Y' = Y + (0.022 - Y) ^ 1.414        otherwise
```

**Step 3 — polarity.** Return 0 if `|Ybg - Ytxt| < 0.0005`.

```
BoW (dark text on light):  S = (Ybg^0.56 - Ytxt^0.57) * 1.14
WoB (light text on dark):  S = (Ybg^0.65 - Ytxt^0.62) * 1.14
```

**Step 4 — clip, offset, scale.**

```
BoW:  Lc = 0 if S <  0.1, else (S - 0.027) * 100
WoB:  Lc = 0 if S > -0.1, else (S + 0.027) * 100
```

The low clip is deliberate: rather than reporting a tiny contrast value, APCA reports zero, because below that threshold the difference is not usable.

### Two implementation traps

- **Inputs are validated against 1.1, not 1.0.** The coefficients sum to 1.0000001, so pure white's Y lands just above 1. A validator that clamps at 1.0 rejects white.
- **Reusing WCAG's luminance function gives wrong answers.** Different transfer function, different coefficients. They must be computed separately.

## Lc levels

| Lc | Use |
|---|---|
| 90 | Preferred for fluent body text and long-form reading |
| 75 | Minimum for columns of body text |
| 60 | Minimum for content text that is not body text |
| 45 | Minimum for large or heavy text — headlines, fine pictograms |
| 30 | Absolute minimum for any other text: placeholder, disabled |
| 15 | Absolute minimum for non-semantic non-text elements |
| <15 | Treat as invisible |

Judge on `abs(Lc)`. The sign tells you polarity, not quality.

## Font lookup

Lc is not a pass/fail line; it buys you a range of font sizes and weights. Smallest body-text combinations per tier:

| Lc | Smallest body text |
|---|---|
| 90 | 14px/400, or 18px/300 |
| 75 | 14px/700, 16px/500, 18px/400, or 24px/300 |
| 60 | 16px/700, 24px/500, 32px/400, or 48px/200 |
| 45 | 24px/700 or 36px/400 — headlines only, not body |
| ≤30 | Not sufficient for body text at any size |

This is the published summary. The full lookup is a two-dimensional table; consult the APCA Readability Criterion for exact per-size weights.

The practical consequence: **failing Lc is fixable with typography, not only with color.** Bumping 14px/400 to 16px/600 can resolve a finding without touching the palette — an option WCAG 2.x cannot express, since it has one threshold for everything under 24px.

## Rough WCAG equivalences

The APCA docs give these for orientation and explicitly warn against using them as conformance levels:

| APCA | Roughly | At |
|---|---|---|
| Lc 60 | exceeds 3:1 | 24px+ |
| Lc 75 | exceeds 4.5:1 | 18px+ |
| Lc 90 | exceeds 7:1 | 16px+ |

These hold only on **light** backgrounds. On dark backgrounds the two metrics diverge sharply — that divergence is the whole point of APCA, and the reason the table stops being useful there.

## Limits

- sRGB only, with presets for Display P3 and Adobe98. Not for print.
- Self-illuminated displays only.
- The license explicitly excludes medical, clinical, safety, aerospace, transport, and military use.
- The conformance table is a beta draft and may still move.

## Sources

- [apca-w3 reference implementation](https://github.com/Myndex/apca-w3) — `src/apca-w3.js`, the `SA98G` constants block
- [APCA documentation](https://git.apcacontrast.com/documentation/README.html)
- [APCA in a Nutshell — Lc levels](https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html)
- [APCA Readability Criterion (ARC)](https://readtech.org/ARC/) — Bronze / Silver / Gold conformance
- [bridge-pca](https://github.com/Myndex/bridge-pca) — APCA math constrained to be backward-compatible with WCAG 2, for teams that need both

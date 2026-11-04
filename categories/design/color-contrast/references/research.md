# The evidence base

Why there are two metrics, what each one is grounded in, and what is still genuinely contested.

## The scale of the problem

**WebAIM Million, February 2026** — automated analysis of 1,000,000 home pages. Low-contrast text below WCAG 2 AA appeared on **83.9%**, up from 79.1% in 2025. It is the single most common accessibility failure, at an average of **34 distinct instances per page**.

**Vaughan & Ortiz Suarez, February 2026** — a reproducible audit of static CSS from 240 homepages among Common Crawl's 500 most-crawled domains. Of 4,327 unique foreground/background pairs, **1,771 (40.9%) failed 4.5:1**. Median per-site pass rate was 62.7%, and only **20.4% of sites** passed on every detected pair.

Two readings of that, and both are partly right. Contrast is genuinely neglected. It is also the failure automated tools detect most easily, so it is over-represented relative to problems a scanner cannot see. The second study's method — static CSS pairs — is close to what `audit.py` does, and its 40.9% figure is a reasonable expectation for an unaudited codebase.

## Where 4.5:1 came from

WCAG's own rationale, not a reconstruction:

- 3:1 is the minimum for normal vision recommended by **ISO 9241-3** and **ANSI-HFES-100-1988**.
- Multiply by 1.5 to compensate for the contrast sensitivity loss accompanying roughly 20/40 acuity — typical around age 80.
- 3 × 1.5 = **4.5:1**. AAA's 7:1 targets roughly 20/80.

So the threshold is a policy judgement layered on a 1980s CRT-era ergonomics baseline. It is calibrated for *acuity* loss specifically, not for cataracts, glare, poor displays, or sunlight — all of which reduce effective contrast without being modelled.

## What is demonstrably wrong with the WCAG 2.x math

These are arithmetic facts about the formula, verifiable with the scripts in this skill.

**1. The dark end collapses.** The `+0.05` flare term dominates when both luminances are small, driving the ratio toward 1 regardless of how different the colors look. The practical result is that the metric badly overstates contrast on dark backgrounds:

| Pair | WCAG | APCA | Reality |
|---|---|---|---|
| `#989898` on `#000000` | 7.28:1 — **AAA** | Lc −46.7 | Below even the Lc 60 content-text floor |
| `#767676` on `#ffffff` | 4.54:1 — AA | Lc +71.6 | Marginal on both |

Same nominal AAA grade, wildly different readability. Dark mode is where this does the most damage, and dark mode is now the default for a large share of users.

**2. Font size and weight are invisible to it.** One threshold covers everything under 24px. A 12px/300 label and a 23px/700 heading face the identical 4.5:1 bar, though their perceived contrast differs substantially. This follows from the contrast sensitivity function, which is spatial-frequency dependent — well-established vision science that the metric simply does not encode.

**3. It is not perceptually uniform.** The ratio is linear in light, not in perception. Accuracy is best against white and degrades as the lighter color darkens. Equal ratio steps do not correspond to equal perceived steps.

Somers' argument, and the reason APCA was commissioned for WCAG 3, is that these produce both **false passes** (compliant but unreadable, especially dark mode) and **false fails** (readable pairs the math rejects). The false-pass direction is the serious one: it means conformance can be achieved without delivering readability.

## What APCA is grounded in

APCA derives from SAPC, a color appearance model for self-illuminated displays, and encodes readability research rather than a photometric ratio. The APCA documentation cites **Bailey & Lovie-Kitchin** and **Legge** on fluent readability requiring contrast roughly ten times the contrast sensitivity threshold — a criterion the WCAG 2 ratio does not attempt to express.

Its structural improvements are real: polarity-aware exponents, a soft clamp near black instead of a flare constant, and output designed to be read against a font lookup rather than a single line.

## What is contested

Present this fairly. APCA is not a settled replacement.

- **It is not normative anywhere.** WCAG 3 is a years-out draft. Every regulation in force — EN 301 549, Section 508, ADA Title II — points at WCAG 2.x. An APCA pass has no legal standing.
- **Its conformance table is still beta.** The algorithm constants are frozen (unchanged since 2021-02-15), but the Bronze/Silver/Gold levels in the Readability Criterion are draft.
- **Its licensing and its author's engagement style** have both drawn criticism within the accessibility community, independent of the math.
- **Migration is genuinely hard.** A codebase tuned to 4.5:1 does not map cleanly onto Lc thresholds. This is why **Bridge-PCA** exists: APCA-derived math constrained so that anything passing it also passes WCAG 2, letting teams improve without losing compliance.
- **Neither metric addresses color-vision deficiency.** Both are luminance-based. A red/green pair can score perfectly and still be indistinguishable to a protanope. That is SC 1.4.1 Use of Color, and no ratio detects it.

The honest position: WCAG 2.x is a flawed instrument that is nonetheless the law, and APCA is a better model of perception that is not yet anyone's standard. Report both. Let compliance be the floor and perception set the aim.

## Practical implications

1. **Audit dark mode separately and expect it to be worse.** This is where WCAG 2.x's failure mode concentrates, and where a passing audit is least trustworthy.
2. **Do not design to exactly 4.5:1.** It is a floor calibrated for one specific acuity loss, and rounding to 8-bit hex can push a borderline pass under. Leave headroom.
3. **Typography is a lever.** APCA makes explicit what WCAG 2 hides: a contrast finding can often be resolved by increasing size or weight rather than changing the palette.
4. **A clean automated report proves little.** Both this tool and the studies above see only statically-paired colors. Text over images, gradients, video, and runtime-computed styles are outside the method entirely.

## Sources

- [WebAIM Million 2026](https://webaim.org/projects/million/) — 1M home pages, 83.9% with low-contrast text
- Vaughan, T. & Ortiz Suarez, P. (2026). [*Colour Contrast on the Web: A WCAG 2.1 Level AA Compliance Audit of Common Crawl's Top 500 Domains*](https://arxiv.org/abs/2602.24067). arXiv:2602.24067
- [Understanding SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — the 3 × 1.5 rationale
- [Why APCA](https://git.apcacontrast.com/documentation/WhyAPCA.html) — Somers' critique of the WCAG 2 math
- [SAPC-APCA](https://github.com/Myndex/SAPC-APCA) — algorithm derivation and documentation
- [Bridge-PCA](https://github.com/Myndex/bridge-pca) — WCAG 2 backward-compatible variant
- [WCAG 3 Working Draft](https://www.w3.org/TR/wcag-3.0/) — where APCA is headed, eventually

#!/usr/bin/env python3
"""Color contrast measurement and repair for WCAG 2.x and APCA.

Zero dependencies — standard library only.

Two metrics, because they answer different questions:

* ``contrast_ratio`` implements the WCAG 2.x ratio (1:1 to 21:1). It is what
  every accessibility law currently in force actually requires: EN 301 549,
  Section 508, and the ADA Title II rule all normatively reference WCAG 2.x.
  Use it for compliance.
* ``apca_contrast`` implements APCA (Lc -108 to +106), the WCAG 3 candidate
  algorithm. It models spatial frequency and polarity, so it tracks what a
  reader actually perceives — especially in dark mode, where WCAG 2.x is
  known to overstate contrast badly. Use it for design judgement.

They disagree, and the disagreement is informative rather than a bug. See
``references/research.md`` in this skill for the evidence on why.

CLI::

    contrast.py check "#767676" white
    contrast.py check "#aaa" "#222" --json
    contrast.py fix "#777777" white --target AAA
    contrast.py fix "#5599ff" "#111111" --metric apca --target 75 --mode both

Library::

    >>> from contrast import contrast_ratio, apca_contrast, adjust
    >>> round(contrast_ratio("#767676", "white"), 2)
    4.54
    >>> round(apca_contrast("#767676", "white"), 1)
    71.6
    >>> adjust("#777777", "white", target="AAA").foreground.hex
    '#595959'
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Callable, NamedTuple, Optional, Sequence, Union

__version__ = "1.0.0"

__all__ = [
    "Color",
    "ColorLike",
    "parse_color",
    "composite",
    "relative_luminance",
    "contrast_ratio",
    "WCAGLevel",
    "WCAGReport",
    "evaluate_wcag",
    "apca_luminance",
    "apca_contrast",
    "APCAReport",
    "evaluate_apca",
    "apca_use_case",
    "apca_font_minimums",
    "Metric",
    "Mode",
    "Adjustment",
    "adjust",
    "ContrastError",
]


class ContrastError(ValueError):
    """Raised for unparseable colors and impossible requests."""


# ---------------------------------------------------------------------------
# Color
# ---------------------------------------------------------------------------


class Color(NamedTuple):
    """An sRGB color. Channels and alpha are floats in ``[0, 1]``."""

    r: float
    g: float
    b: float
    a: float = 1.0

    @property
    def rgb255(self) -> tuple[int, int, int]:
        return tuple(round(c * 255) for c in (self.r, self.g, self.b))  # type: ignore[return-value]

    @property
    def hex(self) -> str:
        """Lowercase ``#rrggbb``, or ``#rrggbbaa`` when translucent."""
        out = "#%02x%02x%02x" % self.rgb255
        if self.a < 1.0:
            out += "%02x" % round(self.a * 255)
        return out

    @property
    def opaque(self) -> bool:
        return self.a >= 1.0

    def over(self, background: "ColorLike") -> "Color":
        """Alpha-composite this color over ``background`` (Porter-Duff source-over)."""
        return composite(self, background)

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.hex


ColorLike = Union[str, Color, Sequence[float]]


# CSS Color Module Level 4 named colors.
CSS_NAMED_COLORS: dict[str, str] = {
    "aliceblue": "f0f8ff", "antiquewhite": "faebd7", "aqua": "00ffff",
    "aquamarine": "7fffd4", "azure": "f0ffff", "beige": "f5f5dc",
    "bisque": "ffe4c4", "black": "000000", "blanchedalmond": "ffebcd",
    "blue": "0000ff", "blueviolet": "8a2be2", "brown": "a52a2a",
    "burlywood": "deb887", "cadetblue": "5f9ea0", "chartreuse": "7fff00",
    "chocolate": "d2691e", "coral": "ff7f50", "cornflowerblue": "6495ed",
    "cornsilk": "fff8dc", "crimson": "dc143c", "cyan": "00ffff",
    "darkblue": "00008b", "darkcyan": "008b8b", "darkgoldenrod": "b8860b",
    "darkgray": "a9a9a9", "darkgreen": "006400", "darkgrey": "a9a9a9",
    "darkkhaki": "bdb76b", "darkmagenta": "8b008b", "darkolivegreen": "556b2f",
    "darkorange": "ff8c00", "darkorchid": "9932cc", "darkred": "8b0000",
    "darksalmon": "e9967a", "darkseagreen": "8fbc8f", "darkslateblue": "483d8b",
    "darkslategray": "2f4f4f", "darkslategrey": "2f4f4f",
    "darkturquoise": "00ced1", "darkviolet": "9400d3", "deeppink": "ff1493",
    "deepskyblue": "00bfff", "dimgray": "696969", "dimgrey": "696969",
    "dodgerblue": "1e90ff", "firebrick": "b22222", "floralwhite": "fffaf0",
    "forestgreen": "228b22", "fuchsia": "ff00ff", "gainsboro": "dcdcdc",
    "ghostwhite": "f8f8ff", "gold": "ffd700", "goldenrod": "daa520",
    "gray": "808080", "green": "008000", "greenyellow": "adff2f",
    "grey": "808080", "honeydew": "f0fff0", "hotpink": "ff69b4",
    "indianred": "cd5c5c", "indigo": "4b0082", "ivory": "fffff0",
    "khaki": "f0e68c", "lavender": "e6e6fa", "lavenderblush": "fff0f5",
    "lawngreen": "7cfc00", "lemonchiffon": "fffacd", "lightblue": "add8e6",
    "lightcoral": "f08080", "lightcyan": "e0ffff",
    "lightgoldenrodyellow": "fafad2", "lightgray": "d3d3d3",
    "lightgreen": "90ee90", "lightgrey": "d3d3d3", "lightpink": "ffb6c1",
    "lightsalmon": "ffa07a", "lightseagreen": "20b2aa", "lightskyblue": "87cefa",
    "lightslategray": "778899", "lightslategrey": "778899",
    "lightsteelblue": "b0c4de", "lightyellow": "ffffe0", "lime": "00ff00",
    "limegreen": "32cd32", "linen": "faf0e6", "magenta": "ff00ff",
    "maroon": "800000", "mediumaquamarine": "66cdaa", "mediumblue": "0000cd",
    "mediumorchid": "ba55d3", "mediumpurple": "9370db",
    "mediumseagreen": "3cb371", "mediumslateblue": "7b68ee",
    "mediumspringgreen": "00fa9a", "mediumturquoise": "48d1cc",
    "mediumvioletred": "c71585", "midnightblue": "191970",
    "mintcream": "f5fffa", "mistyrose": "ffe4e1", "moccasin": "ffe4b5",
    "navajowhite": "ffdead", "navy": "000080", "oldlace": "fdf5e6",
    "olive": "808000", "olivedrab": "6b8e23", "orange": "ffa500",
    "orangered": "ff4500", "orchid": "da70d6", "palegoldenrod": "eee8aa",
    "palegreen": "98fb98", "paleturquoise": "afeeee", "palevioletred": "db7093",
    "papayawhip": "ffefd5", "peachpuff": "ffdab9", "peru": "cd853f",
    "pink": "ffc0cb", "plum": "dda0dd", "powderblue": "b0e0e6",
    "purple": "800080", "rebeccapurple": "663399", "red": "ff0000",
    "rosybrown": "bc8f8f", "royalblue": "4169e1", "saddlebrown": "8b4513",
    "salmon": "fa8072", "sandybrown": "f4a460", "seagreen": "2e8b57",
    "seashell": "fff5ee", "sienna": "a0522d", "silver": "c0c0c0",
    "skyblue": "87ceeb", "slateblue": "6a5acd", "slategray": "708090",
    "slategrey": "708090", "snow": "fffafa", "springgreen": "00ff7f",
    "steelblue": "4682b4", "tan": "d2b48c", "teal": "008080",
    "thistle": "d8bfd8", "tomato": "ff6347", "transparent": "00000000",
    "turquoise": "40e0d0", "violet": "ee82ee", "wheat": "f5deb3",
    "white": "ffffff", "whitesmoke": "f5f5f5", "yellow": "ffff00",
    "yellowgreen": "9acd32",
}

_HEX_RE = re.compile(r"^#?([0-9a-f]{3,8})$")
_FUNC_RE = re.compile(r"^(rgba?|hsla?|oklch|oklab)\((.*)\)$", re.DOTALL)

#: Angle units CSS accepts for a hue component, as multiples of a degree.
_ANGLE_UNITS = {"deg": 1.0, "grad": 0.9, "rad": 180.0 / math.pi, "turn": 360.0}


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _parse_channel(token: str, scale: float = 255.0) -> float:
    token = token.strip()
    if token.endswith("%"):
        return _clamp01(float(token[:-1]) / 100.0)
    return _clamp01(float(token) / scale)


def _parse_number(token: str, percent_scale: float = 1.0) -> float:
    """A CSS number that may carry a ``%`` suffix scaled to ``percent_scale``."""
    token = token.strip()
    if token.endswith("%"):
        return float(token[:-1]) / 100.0 * percent_scale
    return float(token)


def _parse_angle(token: str) -> float:
    """A CSS angle in degrees. Bare numbers are degrees, per CSS Color 4."""
    token = token.strip().lower()
    for unit, factor in _ANGLE_UNITS.items():
        if token.endswith(unit):
            return float(token[: -len(unit)]) * factor
    return float(token)


def _hsl_to_rgb(hue_deg: float, sat: float, light: float) -> "tuple[float, float, float]":
    """HSL to sRGB, per the CSS Color 4 reference algorithm."""
    hue = hue_deg % 360.0 / 30.0
    sat = _clamp01(sat)
    light = _clamp01(light)
    alpha = sat * min(light, 1.0 - light)

    def channel(n: float) -> float:
        k = (n + hue) % 12.0
        return light - alpha * max(-1.0, min(k - 3.0, 9.0 - k, 1.0))

    return channel(0.0), channel(8.0), channel(4.0)


def parse_color(value: ColorLike) -> Color:
    """Parse a color from CSS syntax, a name, a ``Color``, or an RGB sequence.

    Accepted forms:

    * ``Color`` instances (returned unchanged).
    * Hex: ``#rgb``, ``#rgba``, ``#rrggbb``, ``#rrggbbaa``; ``#`` optional.
    * CSS functions: ``rgb(0 128 255)``, ``rgb(0, 128, 255)``,
      ``rgba(0, 128, 255, 0.5)``, ``rgb(0% 50% 100%)``.
    * CSS Color 4 names, case-insensitive, including ``transparent``.
    * Sequences of 3 or 4 numbers, **always interpreted as 0-255** for the
      channels and 0-1 for a 4th alpha element: ``(0, 128, 255)``.

    :raises ContrastError: if the value cannot be parsed.
    """
    if isinstance(value, Color):
        return value

    if isinstance(value, (list, tuple)):
        nums = list(value)
        if len(nums) not in (3, 4):
            raise ContrastError(
                f"RGB sequences need 3 or 4 elements, got {len(nums)}: {value!r}"
            )
        r, g, b = (_clamp01(float(c) / 255.0) for c in nums[:3])
        alpha = _clamp01(float(nums[3])) if len(nums) == 4 else 1.0
        return Color(r, g, b, alpha)

    if not isinstance(value, str):
        raise ContrastError(f"Cannot parse color from {type(value).__name__}: {value!r}")

    text = value.strip().lower()
    if not text:
        raise ContrastError("Cannot parse an empty string as a color")

    text = CSS_NAMED_COLORS.get(text, text)

    match = _HEX_RE.match(text)
    if match:
        digits = match.group(1)
        if len(digits) in (3, 4):
            digits = "".join(c * 2 for c in digits)
        if len(digits) not in (6, 8):
            raise ContrastError(f"Hex colors need 3, 4, 6, or 8 digits: {value!r}")
        parts = [int(digits[i : i + 2], 16) / 255.0 for i in range(0, len(digits), 2)]
        return Color(parts[0], parts[1], parts[2], parts[3] if len(parts) == 4 else 1.0)

    match = _FUNC_RE.match(text)
    if match:
        func = match.group(1).rstrip("a") if match.group(1).startswith(("rgb", "hsl")) else match.group(1)
        tokens = match.group(2).replace("/", " ").replace(",", " ").split()
        if len(tokens) not in (3, 4):
            raise ContrastError(f"{func}() needs 3 or 4 components: {value!r}")
        try:
            alpha = _parse_channel(tokens[3], scale=1.0) if len(tokens) == 4 else 1.0
            if func == "rgb":
                r, g, b = (_parse_channel(t) for t in tokens[:3])
                return Color(r, g, b, alpha)
            if func == "hsl":
                r, g, b = _hsl_to_rgb(
                    _parse_angle(tokens[0]),
                    _parse_number(tokens[1]),
                    _parse_number(tokens[2]),
                )
                return Color(_clamp01(r), _clamp01(g), _clamp01(b), alpha)
            if func == "oklch":
                return _from_oklch(
                    _clamp01(_parse_number(tokens[0])),
                    max(0.0, _parse_number(tokens[1], percent_scale=0.4)),
                    math.radians(_parse_angle(tokens[2])),
                    alpha,
                )
            # oklab: L is 0-1 or a percentage; a and b are absolute or ±0.4 at 100%.
            rgb = _from_oklab(
                (
                    _clamp01(_parse_number(tokens[0])),
                    _parse_number(tokens[1], percent_scale=0.4),
                    _parse_number(tokens[2], percent_scale=0.4),
                )
            )
            return Color(*(_clamp01(c) for c in rgb), alpha)
        except ValueError as exc:
            raise ContrastError(f"Bad number in {value!r}: {exc}") from exc

    raise ContrastError(
        f"Unrecognized color {value!r}. Expected hex, rgb()/hsl()/oklch()/oklab(), "
        "or a CSS color name."
    )


def composite(foreground: ColorLike, background: ColorLike) -> Color:
    """Alpha-composite ``foreground`` over ``background`` (source-over).

    Compositing happens in linear-light sRGB, which is what a GPU actually
    does. Blending gamma-encoded values — the naive approach — darkens
    midtone edges and would skew the resulting contrast figure.

    The result carries the background's alpha, so compositing onto an opaque
    background yields an opaque color.
    """
    fg = parse_color(foreground)
    bg = parse_color(background)
    if fg.a >= 1.0:
        return fg

    out_a = fg.a + bg.a * (1.0 - fg.a)
    if out_a <= 0.0:
        return Color(0.0, 0.0, 0.0, 0.0)

    out = []
    for fc, bc in ((fg.r, bg.r), (fg.g, bg.g), (fg.b, bg.b)):
        lin = (
            _srgb_to_linear(fc) * fg.a + _srgb_to_linear(bc) * bg.a * (1.0 - fg.a)
        ) / out_a
        out.append(_clamp01(_linear_to_srgb(lin)))
    return Color(out[0], out[1], out[2], out_a)


def _resolve_pair(foreground: ColorLike, background: ColorLike) -> tuple[Color, Color]:
    """Parse a pair, flattening a translucent foreground onto the background."""
    fg = parse_color(foreground)
    bg = parse_color(background)
    if not bg.opaque:
        raise ContrastError(
            f"Background {bg.hex} is translucent; contrast against it is undefined. "
            "Composite it onto an opaque color first: composite(bg, page_color)."
        )
    return (fg.over(bg) if not fg.opaque else fg), bg


# ---------------------------------------------------------------------------
# sRGB transfer function
# ---------------------------------------------------------------------------


def _srgb_to_linear(channel: float) -> float:
    """sRGB electro-optical transfer function (IEC 61966-2-1)."""
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(channel: float) -> float:
    if channel <= 0.0031308:
        return channel * 12.92
    return 1.055 * (abs(channel) ** (1 / 2.4)) * (1 if channel >= 0 else -1) - 0.055


# ---------------------------------------------------------------------------
# WCAG 2.x
# ---------------------------------------------------------------------------

_LUMA_COEFFS = (0.2126, 0.7152, 0.0722)


def relative_luminance(color: ColorLike) -> float:
    """Relative luminance per WCAG 2.x, in ``[0, 1]``.

    https://www.w3.org/TR/WCAG22/#dfn-relative-luminance

    Note the rounded BT.709 coefficients (0.2126 / 0.7152 / 0.0722). WCAG
    specifies these exact values, so this deliberately does not use the more
    precise ones APCA uses.
    """
    c = parse_color(color)
    if not c.opaque:
        raise ContrastError(
            f"Luminance of translucent {c.hex} is undefined. Composite it first."
        )
    r, g, b = (_srgb_to_linear(x) for x in (c.r, c.g, c.b))
    kr, kg, kb = _LUMA_COEFFS
    return kr * r + kg * g + kb * b


def contrast_ratio(foreground: ColorLike, background: ColorLike) -> float:
    """WCAG 2.x contrast ratio, from 1.0 (identical) to 21.0 (black on white).

    ``(L1 + 0.05) / (L2 + 0.05)`` where L1 is the lighter luminance. The 0.05
    term models ambient light reflecting off the screen; it is also the reason
    the metric compresses badly at the dark end. See ``references/research.md``.

    The ratio is symmetric, so argument order does not change the result. A
    translucent foreground is composited over the background first.
    """
    fg, bg = _resolve_pair(foreground, background)
    l1, l2 = relative_luminance(fg), relative_luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


class WCAGLevel(Enum):
    """WCAG 2.x conformance thresholds, as contrast ratios."""

    AA_LARGE = 3.0  #: SC 1.4.3, large text. Same threshold as SC 1.4.11.
    AA = 4.5  #: SC 1.4.3, body text. The common compliance target.
    AAA = 7.0  #: SC 1.4.6, body text.

    @classmethod
    def parse(cls, value: "str | float | WCAGLevel") -> float:
        """Coerce ``"AA"``, ``"aaa-large"``, ``4.5``, or a member to a ratio."""
        if isinstance(value, cls):
            return float(value.value)
        if isinstance(value, (int, float)):
            return float(value)
        key = str(value).strip().upper().replace("-", "_").replace(" ", "_")
        if key in cls.__members__:
            return float(cls[key].value)
        if key in _LEVEL_ALIASES:
            return _LEVEL_ALIASES[key]
        try:
            return float(value)
        except ValueError as exc:
            raise ContrastError(
                f"Unknown WCAG level {value!r}. Use AA, AAA, AA_LARGE, AAA_LARGE, "
                "NON_TEXT, or a numeric ratio."
            ) from exc


#: Names that map onto an existing threshold. AAA large text and non-text
#: contrast share numeric values with AA members, so they cannot be distinct
#: enum members without becoming aliases.
_LEVEL_ALIASES: dict[str, float] = {
    "AAA_LARGE": 4.5,  # SC 1.4.6, large text
    "NON_TEXT": 3.0,  # SC 1.4.11
}


@dataclass(frozen=True)
class WCAGReport:
    """The full WCAG 2.x verdict for one color pair."""

    foreground: Color
    background: Color
    ratio: float
    large_text: bool

    @property
    def passes_aa(self) -> bool:
        """SC 1.4.3 Contrast (Minimum), Level AA."""
        return self.ratio >= (3.0 if self.large_text else 4.5)

    @property
    def passes_aaa(self) -> bool:
        """SC 1.4.6 Contrast (Enhanced), Level AAA."""
        return self.ratio >= (4.5 if self.large_text else 7.0)

    @property
    def passes_non_text(self) -> bool:
        """SC 1.4.11 Non-text Contrast: UI components and graphical objects."""
        return self.ratio >= 3.0

    @property
    def highest_level(self) -> str:
        if self.passes_aaa:
            return "AAA"
        if self.passes_aa:
            return "AA"
        if self.passes_non_text:
            return "AA large / non-text only"
        return "fail"

    def as_dict(self) -> dict:
        return {
            "foreground": self.foreground.hex,
            "background": self.background.hex,
            "ratio": round(self.ratio, 3),
            "large_text": self.large_text,
            "passes_aa": self.passes_aa,
            "passes_aaa": self.passes_aaa,
            "passes_non_text": self.passes_non_text,
            "highest_level": self.highest_level,
        }


def evaluate_wcag(
    foreground: ColorLike, background: ColorLike, *, large_text: bool = False
) -> WCAGReport:
    """Measure a pair and report every WCAG 2.x threshold it meets.

    :param large_text: True for text at or above 24px, or 18.66px bold. This
        relaxes AA to 3:1 and AAA to 4.5:1 per SC 1.4.3.
    """
    fg, bg = _resolve_pair(foreground, background)
    return WCAGReport(fg, bg, contrast_ratio(fg, bg), large_text)


# ---------------------------------------------------------------------------
# APCA (Accessible Perceptual Contrast Algorithm)
# ---------------------------------------------------------------------------

# Constants from APCA-W3 0.1.9, exponent set 0.98G-4g-sRGB. Unchanged since
# 2021-02-15. Source: github.com/Myndex/apca-w3 (src/apca-w3.js, SA98G).
_APCA = {
    "main_trc": 2.4,
    "s_rco": 0.2126729,
    "s_gco": 0.7151522,
    "s_bco": 0.0721750,
    "norm_bg": 0.56,
    "norm_txt": 0.57,
    "rev_txt": 0.62,
    "rev_bg": 0.65,
    "blk_thrs": 0.022,
    "blk_clmp": 1.414,
    "scale_bow": 1.14,
    "scale_wob": 1.14,
    "lo_bow_offset": 0.027,
    "lo_wob_offset": 0.027,
    "delta_y_min": 0.0005,
    "lo_clip": 0.1,
}


def apca_luminance(color: ColorLike) -> float:
    """Screen luminance ``Ys`` as APCA defines it.

    This is **not** WCAG relative luminance. APCA uses a simple 2.4 power
    curve rather than the sRGB piecewise function, and the unrounded BT.709
    coefficients. Mixing the two produces wrong Lc values.
    """
    c = parse_color(color)
    if not c.opaque:
        raise ContrastError(
            f"APCA luminance of translucent {c.hex} is undefined. Composite it first."
        )
    trc = _APCA["main_trc"]
    return (
        _APCA["s_rco"] * c.r**trc
        + _APCA["s_gco"] * c.g**trc
        + _APCA["s_bco"] * c.b**trc
    )


def _apca_soft_clamp(y: float) -> float:
    """Soft-clamp luminance near black, modelling display flare and eye scatter."""
    thrs, clmp = _APCA["blk_thrs"], _APCA["blk_clmp"]
    return y if y > thrs else y + (thrs - y) ** clmp


def apca_contrast(text: ColorLike, background: ColorLike) -> float:
    """APCA lightness contrast ``Lc``, roughly -108 to +106.

    Unlike the WCAG ratio this is **directional**: swapping the arguments does
    not give the same magnitude. Positive Lc means dark text on a light
    background (BoW); negative means light text on dark (WoB).

    Judge readability on ``abs(lc)``. Lc 75 is the practical floor for body
    text, Lc 90 the preferred level. See :func:`apca_use_case`.

    Returns 0.0 for inputs outside the valid luminance domain or below the
    minimum discriminable difference, matching the reference implementation.
    """
    txt, bg = _resolve_pair(text, background)
    txt_y = apca_luminance(txt)
    bg_y = apca_luminance(bg)

    if min(txt_y, bg_y) < 0.0 or max(txt_y, bg_y) > 1.1:
        return 0.0

    txt_y = _apca_soft_clamp(txt_y)
    bg_y = _apca_soft_clamp(bg_y)

    if abs(bg_y - txt_y) < _APCA["delta_y_min"]:
        return 0.0

    if bg_y > txt_y:  # BoW: dark text on light background
        sapc = (bg_y ** _APCA["norm_bg"] - txt_y ** _APCA["norm_txt"]) * _APCA[
            "scale_bow"
        ]
        output = 0.0 if sapc < _APCA["lo_clip"] else sapc - _APCA["lo_bow_offset"]
    else:  # WoB: light text on dark background
        sapc = (bg_y ** _APCA["rev_bg"] - txt_y ** _APCA["rev_txt"]) * _APCA[
            "scale_wob"
        ]
        output = 0.0 if sapc > -_APCA["lo_clip"] else sapc + _APCA["lo_wob_offset"]

    return output * 100.0


#: Lc thresholds and what each one licenses, from the APCA "in a nutshell"
#: guidance. Ordered high to low. The full conformance table lives in the
#: APCA Readability Criterion; this is the practical subset.
APCA_USE_CASES: tuple[tuple[float, str], ...] = (
    (90.0, "Preferred for fluent body text and long-form reading."),
    (75.0, "Minimum for columns of body text."),
    (60.0, "Minimum for content text that is not body text."),
    (45.0, "Minimum for large or heavy text such as headlines, and fine pictograms."),
    (30.0, "Absolute minimum for any other text, including placeholder and disabled."),
    (15.0, "Absolute minimum for non-semantic non-text elements."),
    (0.0, "Invisible in practice. Do not use."),
)

#: Smallest ``(px, weight)`` combinations each Lc tier supports for body text.
APCA_FONT_MINIMUMS: dict[float, tuple[tuple[int, int], ...]] = {
    90.0: ((14, 400), (18, 300)),
    75.0: ((14, 700), (16, 500), (18, 400), (24, 300)),
    60.0: ((16, 700), (24, 500), (32, 400), (48, 200)),
    45.0: ((24, 700), (36, 400)),
    30.0: (),
    15.0: (),
    0.0: (),
}


def apca_use_case(lc: float) -> str:
    """Plain-English description of what an Lc value is good for."""
    magnitude = abs(lc)
    for threshold, description in APCA_USE_CASES:
        if magnitude >= threshold:
            return description
    return APCA_USE_CASES[-1][1]


def apca_font_minimums(lc: float) -> tuple[tuple[int, int], ...]:
    """Smallest ``(size_px, weight)`` pairs this Lc supports for body text.

    Empty when the Lc is too low to carry body text at any size. This is the
    published summary table, not the full 2-D lookup; for exact per-size
    weights consult the APCA font lookup table.
    """
    magnitude = abs(lc)
    for threshold, sizes in APCA_FONT_MINIMUMS.items():
        if magnitude >= threshold:
            return sizes
    return ()


@dataclass(frozen=True)
class APCAReport:
    """The APCA verdict for one text/background pair."""

    text: Color
    background: Color
    lc: float

    @property
    def polarity(self) -> str:
        """``"BoW"`` for dark-on-light, ``"WoB"`` for light-on-dark."""
        return "WoB" if self.lc < 0 else "BoW"

    @property
    def passes_body_text(self) -> bool:
        """Meets Lc 75, the practical floor for a column of body text."""
        return abs(self.lc) >= 75.0

    @property
    def passes_fluent_text(self) -> bool:
        """Meets Lc 90, the preferred level for long-form reading."""
        return abs(self.lc) >= 90.0

    @property
    def use_case(self) -> str:
        return apca_use_case(self.lc)

    @property
    def font_minimums(self) -> tuple[tuple[int, int], ...]:
        return apca_font_minimums(self.lc)

    def as_dict(self) -> dict:
        return {
            "text": self.text.hex,
            "background": self.background.hex,
            "lc": round(self.lc, 1),
            "polarity": self.polarity,
            "passes_body_text": self.passes_body_text,
            "passes_fluent_text": self.passes_fluent_text,
            "use_case": self.use_case,
            "font_minimums": [
                {"px": px, "weight": w} for px, w in self.font_minimums
            ],
        }


def evaluate_apca(text: ColorLike, background: ColorLike) -> APCAReport:
    """Measure a pair with APCA and report polarity plus font guidance."""
    txt, bg = _resolve_pair(text, background)
    return APCAReport(txt, bg, apca_contrast(txt, bg))


# ---------------------------------------------------------------------------
# OKLab / OKLCh — the space we adjust lightness in
# ---------------------------------------------------------------------------
#
# Adjusting in HSL, the obvious choice, shifts perceived hue: HSL lightness is
# a crude average of RGB extremes, so darkening a yellow swings it olive.
# OKLab (Bjorn Ottosson, 2020) is perceptually uniform, so moving L alone
# preserves hue and chroma about as well as anything can.


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def _to_oklab(color: Color) -> tuple[float, float, float]:
    r, g, b = (_srgb_to_linear(c) for c in (color.r, color.g, color.b))

    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l_, m_, s_ = _cbrt(l), _cbrt(m), _cbrt(s)

    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def _from_oklab(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    """OKLab to gamma-encoded sRGB. May return out-of-gamut values."""
    L, a, b = lab

    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l, m, s = l_**3, m_**3, s_**3

    return (
        _linear_to_srgb(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
        _linear_to_srgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
        _linear_to_srgb(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s),
    )


def _to_oklch(color: Color) -> tuple[float, float, float]:
    L, a, b = _to_oklab(color)
    return L, math.hypot(a, b), math.atan2(b, a)


def _in_gamut(rgb: tuple[float, float, float], epsilon: float = 1e-6) -> bool:
    return all(-epsilon <= c <= 1.0 + epsilon for c in rgb)


def _from_oklch(lightness: float, chroma: float, hue: float, alpha: float) -> Color:
    """OKLCh to sRGB, reducing chroma until the result fits the gamut.

    Chroma reduction is the CSS Color 4 approach: it keeps hue and lightness
    intact and gives up saturation, which is far less visible than the channel
    clipping you get from a naive clamp.
    """

    def render(c: float) -> tuple[float, float, float]:
        return _from_oklab((lightness, c * math.cos(hue), c * math.sin(hue)))

    rgb = render(chroma)
    if not _in_gamut(rgb):
        lo, hi = 0.0, chroma
        for _ in range(24):
            mid = (lo + hi) / 2.0
            if _in_gamut(render(mid)):
                lo = mid
            else:
                hi = mid
        rgb = render(lo)

    return Color(_clamp01(rgb[0]), _clamp01(rgb[1]), _clamp01(rgb[2]), alpha)


def _with_lightness(color: Color, lightness: float) -> Color:
    """Return ``color`` at a new OKLab lightness, preserving hue and chroma."""
    _, chroma, hue = _to_oklch(color)
    return _from_oklch(_clamp01(lightness), chroma, hue, color.a)


def _quantize(color: Color) -> Color:
    """Snap channels to 8 bits — the precision a CSS hex value actually carries.

    Adjustment searches continuous lightness, but the answer ships as ``#rrggbb``.
    Rounding at the end can drop a result back under its target by a hundredth
    of a ratio point, so the search evaluates quantized colors throughout and
    the number it reports is the one the emitted hex really scores.
    """
    r, g, b = color.rgb255
    return Color(r / 255.0, g / 255.0, b / 255.0, color.a)


# ---------------------------------------------------------------------------
# Adjustment
# ---------------------------------------------------------------------------


class Metric(Enum):
    """Which contrast metric an adjustment should satisfy."""

    WCAG = "wcag"
    APCA = "apca"


class Mode(Enum):
    """Which color an adjustment is allowed to move."""

    FOREGROUND = "fg"
    BACKGROUND = "bg"
    BOTH = "both"


@dataclass(frozen=True)
class Adjustment:
    """The outcome of an :func:`adjust` call."""

    foreground: Color
    background: Color
    original_foreground: Color
    original_background: Color
    achieved: float
    target: float
    metric: Metric
    mode: Mode
    success: bool

    @property
    def changed(self) -> bool:
        return (
            self.foreground != self.original_foreground
            or self.background != self.original_background
        )

    @property
    def perceptual_shift(self) -> float:
        """Total OKLab lightness moved, in ``[0, 2]``. Lower is a gentler fix."""
        return abs(
            _to_oklab(self.foreground)[0] - _to_oklab(self.original_foreground)[0]
        ) + abs(
            _to_oklab(self.background)[0] - _to_oklab(self.original_background)[0]
        )

    def as_dict(self) -> dict:
        return {
            "foreground": self.foreground.hex,
            "background": self.background.hex,
            "original_foreground": self.original_foreground.hex,
            "original_background": self.original_background.hex,
            "achieved": round(self.achieved, 3),
            "target": self.target,
            "metric": self.metric.value,
            "mode": self.mode.value,
            "success": self.success,
            "changed": self.changed,
            "perceptual_shift": round(self.perceptual_shift, 4),
        }


def _score(fg: Color, bg: Color, metric: Metric) -> float:
    if metric is Metric.WCAG:
        return contrast_ratio(fg, bg)
    return abs(apca_contrast(fg, bg))


# Bisection to ~1/10000 of the lightness range: finer than an 8-bit channel
# step, so the result is exact once quantized to hex.
_BISECT_STEPS = 20


def _bisect(
    make: Callable[[float], "tuple[Color, Color]"],
    target: float,
    metric: Metric,
) -> "tuple[float, Color, Color, float]":
    """Find the smallest ``t`` in [0, 1] whose colors reach ``target``.

    ``make(0)`` must be the original pair and ``make(1)`` a pair that meets
    the target. Returns ``(t, fg, bg, achieved)``.
    """
    lo, hi = 0.0, 1.0
    best = make(1.0)
    best_score = _score(*best, metric)
    best_t = 1.0

    for _ in range(_BISECT_STEPS):
        mid = (lo + hi) / 2.0
        pair = make(mid)
        score = _score(*pair, metric)
        if score >= target:
            hi, best, best_score, best_t = mid, pair, score, mid
        else:
            lo = mid

    return best_t, best[0], best[1], best_score


def adjust(
    foreground: ColorLike,
    background: ColorLike,
    *,
    target: "str | float | WCAGLevel" = WCAGLevel.AA,
    metric: "Metric | str" = Metric.WCAG,
    mode: "Mode | str" = Mode.FOREGROUND,
) -> Adjustment:
    """Nudge one or both colors until they meet ``target``, changing as little as possible.

    The search runs in OKLab lightness, so hue and chroma survive. Both
    directions (lighter and darker) are tried; the one that reaches the target
    with the smaller perceptual shift wins. This matters — for a mid-grey on
    white, darkening is a much smaller change than lightening, and a
    fixed-direction algorithm gets it wrong half the time.

    :param target: ``"AA"``, ``"AAA"``, ``"AA_LARGE"``, ``"AAA_LARGE"``, or a
        number. For ``Metric.APCA`` the number is an absolute Lc, e.g. ``75``.
    :param metric: ``Metric.WCAG`` (compliance) or ``Metric.APCA`` (perception).
    :param mode: which color may move.
    :returns: an :class:`Adjustment`. Check ``.success`` — some pairs cannot
        reach the target at all, and then the closest attempt is returned with
        ``success=False``.
    """
    metric = Metric(metric) if not isinstance(metric, Metric) else metric
    mode = Mode(mode) if not isinstance(mode, Mode) else mode
    threshold = (
        float(target)
        if metric is Metric.APCA and isinstance(target, (int, float))
        else WCAGLevel.parse(target)
    )

    fg0, bg0 = _resolve_pair(foreground, background)
    current = _score(fg0, bg0, metric)
    if current >= threshold:
        return Adjustment(
            fg0, bg0, fg0, bg0, current, threshold, metric, mode, success=True
        )

    fg_l = _to_oklab(fg0)[0]
    bg_l = _to_oklab(bg0)[0]

    # Each candidate is a direction pair: where fg and bg lightness head when
    # t reaches 1. None means "this color does not move".
    if mode is Mode.FOREGROUND:
        candidates = [(0.0, None), (1.0, None)]
    elif mode is Mode.BACKGROUND:
        candidates = [(None, 0.0), (None, 1.0)]
    else:
        candidates = [(0.0, 1.0), (1.0, 0.0)]

    best: Optional[Adjustment] = None
    best_shift = math.inf
    fallback: Optional[Adjustment] = None
    fallback_score = -math.inf

    for fg_end, bg_end in candidates:

        def make(t: float, fg_end=fg_end, bg_end=bg_end) -> tuple[Color, Color]:
            fg = fg0 if fg_end is None else _with_lightness(fg0, fg_l + t * (fg_end - fg_l))
            bg = bg0 if bg_end is None else _with_lightness(bg0, bg_l + t * (bg_end - bg_l))
            return _quantize(fg), _quantize(bg)

        extreme_fg, extreme_bg = make(1.0)
        extreme_score = _score(extreme_fg, extreme_bg, metric)

        if extreme_score < threshold:
            # This direction tops out short of the target. Remember it in case
            # every direction fails, so we can still return the best effort.
            if extreme_score > fallback_score:
                fallback_score = extreme_score
                fallback = Adjustment(
                    extreme_fg, extreme_bg, fg0, bg0, extreme_score,
                    threshold, metric, mode, success=False,
                )
            continue

        _, fg, bg, achieved = _bisect(make, threshold, metric)
        result = Adjustment(
            fg, bg, fg0, bg0, achieved, threshold, metric, mode, success=True
        )
        if result.perceptual_shift < best_shift:
            best, best_shift = result, result.perceptual_shift

    if best is not None:
        return best
    if fallback is not None:
        return fallback
    return Adjustment(
        fg0, bg0, fg0, bg0, current, threshold, metric, mode, success=False
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _check_command(args: argparse.Namespace) -> int:
    wcag = evaluate_wcag(args.foreground, args.background, large_text=args.large)
    apca = evaluate_apca(args.foreground, args.background)

    if args.json:
        print(json.dumps({"wcag": wcag.as_dict(), "apca": apca.as_dict()}, indent=2))
        return 0 if wcag.passes_aa else 1

    def mark(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    print(f"{wcag.foreground.hex} on {wcag.background.hex}")
    if wcag.foreground != parse_color(args.foreground):
        print(f"  (foreground composited from {parse_color(args.foreground).hex})")
    print()
    print(f"  WCAG 2.x   {wcag.ratio:.2f}:1")
    size = "large text" if args.large else "body text"
    print(f"    AA  ({size})       {mark(wcag.passes_aa)}")
    print(f"    AAA ({size})       {mark(wcag.passes_aaa)}")
    print(f"    Non-text (1.4.11)  {mark(wcag.passes_non_text)}")
    print()
    print(f"  APCA       Lc {apca.lc:+.1f}  ({apca.polarity})")
    print(f"    {apca.use_case}")
    if apca.font_minimums:
        sizes = ", ".join(f"{px}px/{w}" for px, w in apca.font_minimums)
        print(f"    Smallest body text: {sizes}")
    else:
        print("    Not sufficient for body text at any size.")

    if wcag.passes_aa and not apca.passes_body_text:
        print()
        print("  Note: passes WCAG 2.x but APCA rates it below the body-text floor.")
        if apca.polarity == "WoB":
            print("  Expected on dark backgrounds, where WCAG 2.x overstates contrast.")
        else:
            print("  Compliant, but consider more contrast for small or light text.")

    return 0 if wcag.passes_aa else 1


def _fix_command(args: argparse.Namespace) -> int:
    result = adjust(
        args.foreground,
        args.background,
        target=args.target,
        metric=args.metric,
        mode=args.mode,
    )

    if args.json:
        print(json.dumps(result.as_dict(), indent=2))
        return 0 if result.success else 1

    def fmt(value: float) -> str:
        return f"Lc {value:.1f}" if result.metric is Metric.APCA else f"{value:.2f}:1"

    before = _score(
        result.original_foreground, result.original_background, result.metric
    )

    print(
        f"  before  {result.original_foreground.hex} on "
        f"{result.original_background.hex}   {fmt(before)}"
    )
    print(
        f"  after   {result.foreground.hex} on "
        f"{result.background.hex}   {fmt(result.achieved)}"
    )
    print(f"  target  {fmt(result.target)}")
    if not result.success:
        print()
        print("  Could not reach the target. Shown above is the closest possible")
        print(f"  result in {result.mode.value} mode. Try --mode both, or pick a")
        print("  different hue — some colors cannot reach high contrast by")
        print("  lightness alone.")
    return 0 if result.success else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contrast",
        description="Measure and repair color contrast (WCAG 2.x and APCA).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="measure a foreground/background pair")
    check.add_argument("foreground")
    check.add_argument("background")
    check.add_argument(
        "--large",
        action="store_true",
        help="text is 24px+, or 18.66px+ bold (relaxes WCAG thresholds)",
    )
    check.add_argument("--json", action="store_true", help="machine-readable output")
    check.set_defaults(func=_check_command)

    fix = sub.add_parser("fix", help="adjust colors until they meet a target")
    fix.add_argument("foreground")
    fix.add_argument("background")
    fix.add_argument(
        "--target",
        default="AA",
        help="AA, AAA, AA_LARGE, AAA_LARGE, a ratio like 4.5, or an Lc like 75",
    )
    fix.add_argument(
        "--metric", choices=[m.value for m in Metric], default=Metric.WCAG.value
    )
    fix.add_argument(
        "--mode",
        choices=[m.value for m in Mode],
        default=Mode.FOREGROUND.value,
        help="which color may move (default: fg)",
    )
    fix.add_argument("--json", action="store_true", help="machine-readable output")
    fix.set_defaults(func=_fix_command)

    return parser


def main(argv: "Sequence[str] | None" = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ContrastError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Tests for contrast.py. Run with `python3 -m pytest` or `python3 test_contrast.py`."""

from __future__ import annotations

import math
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

from contrast import (  # noqa: E402
    Color,
    ContrastError,
    Metric,
    Mode,
    WCAGLevel,
    adjust,
    apca_contrast,
    apca_font_minimums,
    apca_luminance,
    composite,
    contrast_ratio,
    evaluate_apca,
    evaluate_wcag,
    main,
    parse_color,
    relative_luminance,
)

FAILURES: list[str] = []


def check(label: str, actual, expected, tol: float | None = None) -> None:
    if tol is not None:
        ok = actual is not None and math.isclose(actual, expected, abs_tol=tol)
    else:
        ok = actual == expected
    if not ok:
        FAILURES.append(f"{label}: expected {expected!r}, got {actual!r}")


def check_true(label: str, value) -> None:
    if not value:
        FAILURES.append(f"{label}: expected truthy, got {value!r}")


def check_raises(label: str, exc, fn, *args, **kwargs) -> None:
    try:
        fn(*args, **kwargs)
    except exc:
        return
    except Exception as other:  # noqa: BLE001
        FAILURES.append(f"{label}: raised {type(other).__name__}, expected {exc.__name__}")
        return
    FAILURES.append(f"{label}: did not raise {exc.__name__}")


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def test_parsing() -> None:
    check("hex long", parse_color("#ff8800"), Color(1.0, 136 / 255, 0.0, 1.0))
    check("hex short", parse_color("#f80"), parse_color("#ff8800"))
    check("hex no hash", parse_color("ff8800"), parse_color("#ff8800"))
    check("hex 8 digit alpha", parse_color("#ff880080").a, 128 / 255, tol=1e-9)
    check("hex 4 digit alpha", parse_color("#f808"), parse_color("#ff880088"))
    check("named", parse_color("rebeccapurple"), parse_color("#663399"))
    check("named case", parse_color("ReBeCcApUrPlE"), parse_color("#663399"))
    check("named grey alias", parse_color("grey"), parse_color("gray"))
    check("transparent", parse_color("transparent").a, 0.0, tol=1e-9)
    check("rgb commas", parse_color("rgb(255, 136, 0)"), parse_color("#ff8800"))
    check("rgb spaces", parse_color("rgb(255 136 0)"), parse_color("#ff8800"))
    check("rgba", parse_color("rgba(255, 136, 0, 0.5)").a, 0.5, tol=1e-9)
    check("rgb slash alpha", parse_color("rgb(255 136 0 / 0.5)").a, 0.5, tol=1e-9)
    check("rgb percent", parse_color("rgb(100% 0% 0%)"), parse_color("#ff0000"))
    check("sequence is 0-255", parse_color((255, 136, 0)), parse_color("#ff8800"))
    check("sequence with alpha", parse_color((255, 136, 0, 0.5)).a, 0.5, tol=1e-9)
    check("Color passthrough", parse_color(Color(0.5, 0.5, 0.5)), Color(0.5, 0.5, 0.5))
    check("hex roundtrip", parse_color("#1a2b3c").hex, "#1a2b3c")
    check("hex roundtrip alpha", parse_color("#1a2b3c80").hex, "#1a2b3c80")

    check_raises("empty string", ContrastError, parse_color, "")
    check_raises("nonsense", ContrastError, parse_color, "notacolor")
    check_raises("bad hex length", ContrastError, parse_color, "#12345")
    check_raises("wrong tuple size", ContrastError, parse_color, (1, 2))
    check_raises("wrong type", ContrastError, parse_color, 42)


# ---------------------------------------------------------------------------
# WCAG 2.x — anchors from the spec and widely published values
# ---------------------------------------------------------------------------

def test_wcag() -> None:
    check("luminance black", relative_luminance("#000000"), 0.0, tol=1e-12)
    check("luminance white", relative_luminance("#ffffff"), 1.0, tol=1e-12)
    # Pure primaries reproduce the BT.709 coefficients exactly.
    check("luminance red", relative_luminance("#ff0000"), 0.2126, tol=1e-9)
    check("luminance green", relative_luminance("#00ff00"), 0.7152, tol=1e-9)
    check("luminance blue", relative_luminance("#0000ff"), 0.0722, tol=1e-9)

    check("black on white", contrast_ratio("black", "white"), 21.0, tol=1e-9)
    check("white on white", contrast_ratio("white", "white"), 1.0, tol=1e-9)
    # #767676 on white is the canonical "just barely AA" grey.
    check("767676 on white", contrast_ratio("#767676", "white"), 4.54, tol=0.01)
    # #949494 on white is the canonical "just barely 3:1" grey.
    check("949494 on white", contrast_ratio("#949494", "white"), 3.03, tol=0.01)
    check("symmetric", contrast_ratio("#123456", "#abcdef"),
          contrast_ratio("#abcdef", "#123456"), tol=1e-12)

    report = evaluate_wcag("#767676", "white")
    check_true("767676 passes AA", report.passes_aa)
    check("767676 not AAA", report.passes_aaa, False)
    check_true("767676 passes non-text", report.passes_non_text)
    check("767676 highest", report.highest_level, "AA")

    large = evaluate_wcag("#949494", "white", large_text=True)
    check_true("949494 passes AA large", large.passes_aa)
    check("949494 fails AA body", evaluate_wcag("#949494", "white").passes_aa, False)

    check("level parse AA", WCAGLevel.parse("AA"), 4.5)
    check("level parse aaa-large", WCAGLevel.parse("aaa-large"), 4.5)
    check("level parse non_text", WCAGLevel.parse("NON_TEXT"), 3.0)
    check("level parse number", WCAGLevel.parse(4.5), 4.5)
    check("level parse numstr", WCAGLevel.parse("6.2"), 6.2)
    check("level parse member", WCAGLevel.parse(WCAGLevel.AAA), 7.0)
    check_raises("level parse bad", ContrastError, WCAGLevel.parse, "AAAA")


# ---------------------------------------------------------------------------
# APCA — against the reference implementation's constants
# ---------------------------------------------------------------------------

def test_apca() -> None:
    check("apca Y black", apca_luminance("#000000"), 0.0, tol=1e-12)
    # APCA's coefficients sum to 1.0000001, so white lands just over 1.0. This
    # is the reference implementation's behaviour, not a rounding slip here —
    # it is why APCAcontrast() validates inputs against 1.1 rather than 1.0.
    check("apca Y white", apca_luminance("#ffffff"), 1.0000001, tol=1e-12)

    # Anchors: maximum BoW and WoB contrast in sRGB.
    check("apca black on white", apca_contrast("black", "white"), 106.04, tol=0.05)
    check("apca white on black", apca_contrast("white", "black"), -107.88, tol=0.05)

    # The apca-w3 docs use fontLookupAPCA(-68.541) as their worked example,
    # which is white text on #888888.
    check("apca white on 888", apca_contrast("#ffffff", "#888888"), -68.541, tol=0.01)

    # Directional, unlike the WCAG ratio.
    check_true(
        "apca is directional",
        abs(apca_contrast("#888", "#fff")) != abs(apca_contrast("#fff", "#888")),
    )

    check("apca identical is zero", apca_contrast("#777", "#777"), 0.0, tol=1e-12)
    # Below deltaYmin the reference returns exactly 0.
    check("apca near-identical is zero", apca_contrast("#777777", "#777877"), 0.0)
    # Below loClip the reference returns exactly 0 rather than a small number.
    check("apca low clip", apca_contrast("#777777", "#7a7a7a"), 0.0)

    report = evaluate_apca("#000", "#fff")
    check("polarity BoW", report.polarity, "BoW")
    check_true("black on white is fluent", report.passes_fluent_text)
    check("polarity WoB", evaluate_apca("#fff", "#000").polarity, "WoB")

    check_true("Lc 90 supports 14px/400", (14, 400) in apca_font_minimums(95))
    check("Lc 20 supports no body text", apca_font_minimums(20), ())
    check("font minimums use magnitude", apca_font_minimums(-95), apca_font_minimums(95))


def test_wcag_apca_disagree() -> None:
    """The documented failure mode: WCAG 2.x overstates contrast in dark mode.

    #989898 on black clears WCAG AAA at 7.28:1, yet APCA rates it Lc -46.7 —
    not even half the Lc 75 floor for body text. This gap is the single best
    argument for reporting both numbers.
    """
    ratio = contrast_ratio("#989898", "#000000")
    lc = apca_contrast("#989898", "#000000")
    check_true("dark pair passes WCAG AAA", ratio >= 7.0)
    check_true("dark pair fails APCA body text", abs(lc) < 75)
    check_true("dark pair fails APCA content text", abs(lc) < 60)


# ---------------------------------------------------------------------------
# Alpha compositing
# ---------------------------------------------------------------------------

def test_composite() -> None:
    check("opaque unchanged", composite("#ff0000", "#00ff00"), parse_color("#ff0000"))
    check("fully transparent", composite("#ff000000", "#00ff00").hex, "#00ff00")
    check("result opaque over opaque", composite("#ff000080", "#00ff00").a, 1.0, tol=1e-9)

    # Compositing happens in linear light, so 50% black over white lands well
    # above the 0x80 that naive gamma-space blending would give.
    grey = composite("#00000080", "#ffffff")
    check_true("linear-light blend is lighter than naive", grey.rgb255[0] > 0x80)

    # A translucent foreground is flattened automatically before measuring.
    check(
        "auto-composite in contrast_ratio",
        contrast_ratio("#00000080", "#ffffff"),
        contrast_ratio(composite("#00000080", "#ffffff"), "#ffffff"),
        tol=1e-12,
    )
    check_raises("translucent background rejected", ContrastError,
                 contrast_ratio, "#000", "#ffffff80")
    check_raises("translucent luminance rejected", ContrastError,
                 relative_luminance, "#00000080")


# ---------------------------------------------------------------------------
# Adjustment
# ---------------------------------------------------------------------------

def test_adjust_basics() -> None:
    already = adjust("black", "white", target="AAA")
    check_true("no-op when already passing", already.success)
    check("no-op does not change", already.changed, False)

    fixed = adjust("#777777", "white", target="AA")
    check_true("fix succeeds", fixed.success)
    check_true("fix meets target", contrast_ratio(fixed.foreground, "white") >= 4.5)
    check("fix leaves background alone", fixed.background, parse_color("white"))

    # Minimal change: one more step toward the original must fail the target.
    # A darkened result should be no darker than necessary.
    check_true("fix is minimal", contrast_ratio(fixed.foreground, "white") < 4.7)


def test_adjust_survives_quantization() -> None:
    """Regression: a result that only passes at float precision is not a fix.

    Bisecting continuous OKLab lightness and rounding to #rrggbb afterwards can
    land a hundredth of a point under the target. The reported hex must score
    at or above the target when re-measured from its own hex string.
    """
    cases = [
        ("#999999", "#f5f5f5", 4.5), ("#78a0c8", "#f5f5f5", 4.5),
        ("#557799", "#003366", 4.5), ("#6699cc", "#0073e6", 3.0),
        ("#8a8a8a", "#eeeeee", 4.5), ("#767676", "#808080", 4.5),
    ]
    for fg, bg, target in cases:
        result = adjust(fg, bg, target=target)
        if not result.success:
            FAILURES.append(f"quantize {fg}/{bg}: adjust failed outright")
            continue
        rendered = contrast_ratio(result.foreground.hex, result.background.hex)
        if rendered < target:
            FAILURES.append(
                f"quantize {fg}/{bg}: {result.foreground.hex} scores {rendered:.4f} "
                f"< {target} once rounded to hex"
            )
        if abs(rendered - result.achieved) > 1e-9:
            FAILURES.append(
                f"quantize {fg}/{bg}: reported {result.achieved:.4f} but hex "
                f"scores {rendered:.4f}"
            )

    # The whole grey axis, both metrics, must survive the round trip.
    for value in range(0, 256, 3):
        grey = f"#{value:02x}{value:02x}{value:02x}"
        result = adjust(grey, "#ffffff", target="AA")
        if result.success and contrast_ratio(result.foreground.hex, "#ffffff") < 4.5:
            FAILURES.append(f"quantize sweep {grey}: {result.foreground.hex} under 4.5")
        apca = adjust(grey, "#000000", target=60, metric=Metric.APCA)
        if apca.success and abs(apca_contrast(apca.foreground.hex, "#000000")) < 60:
            FAILURES.append(f"quantize sweep apca {grey}: {apca.foreground.hex} under Lc 60")


def test_adjust_direction() -> None:
    """The bug that motivated the rewrite: direction must be chosen, not assumed."""
    # Equal luminance. A naive `lighter ? up : down` heuristic dead-ends here.
    tie = adjust("#777777", "#777777", target="AA", mode=Mode.FOREGROUND)
    check_true("equal colors can be fixed", tie.success)
    check_true("equal colors meet target",
               contrast_ratio(tie.foreground, "#777777") >= 4.5)

    # Black on black: the only way out is to lighten the foreground.
    black = adjust("#000000", "#000000", target="AA")
    check_true("black on black succeeds", black.success)
    check_true("black on black lightens", black.foreground.rgb255[0] > 0)

    # Against a mid grey, darkening is the cheaper route to AAA than lightening.
    to_darker = adjust("#808080", "#a0a0a0", target="AAA")
    check_true("picks darker route", to_darker.foreground.rgb255[0] < 0x80)


def test_adjust_modes() -> None:
    bg_only = adjust("#777777", "#888888", target="AA", mode=Mode.BACKGROUND)
    check_true("bg mode succeeds", bg_only.success)
    check("bg mode leaves fg alone", bg_only.foreground, parse_color("#777777"))
    check_true("bg mode moves bg", bg_only.background != parse_color("#888888"))

    both = adjust("#777777", "#888888", target="AAA", mode=Mode.BOTH)
    check_true("both mode succeeds", both.success)
    check_true("both mode moves fg", both.foreground != parse_color("#777777"))
    check_true("both mode moves bg", both.background != parse_color("#888888"))
    check_true("both mode meets target",
               contrast_ratio(both.foreground, both.background) >= 7.0)

    # Splitting the work across two colors should shift each one less.
    fg_only = adjust("#777777", "#888888", target="AAA", mode=Mode.FOREGROUND)
    if fg_only.success:
        check_true("both mode is gentler per color",
                   both.perceptual_shift <= fg_only.perceptual_shift * 1.05)


def test_adjust_impossible() -> None:
    """Some targets cannot be reached; that must be reported, not looped forever."""
    # Nothing in sRGB reaches 21:1 against mid-grey.
    impossible = adjust("#808080", "#808080", target=21.0, mode=Mode.FOREGROUND)
    check("impossible target reports failure", impossible.success, False)
    check_true("impossible target still returns best effort",
               impossible.achieved > 1.0)

    # Foreground-only against white cannot exceed 21:1 either, but AAA is fine.
    ok = adjust("#eeeeee", "#ffffff", target="AAA")
    check_true("light on white still reachable", ok.success)


def test_adjust_hue_preservation() -> None:
    """Adjusting in OKLab should keep the hue recognisable."""
    from contrast import _to_oklch  # noqa: PLC0415

    original = parse_color("#c0a000")  # a saturated yellow-ish gold
    result = adjust(original, "white", target="AAA")
    check_true("gold fix succeeds", result.success)

    h0 = _to_oklch(original)[2]
    h1 = _to_oklch(result.foreground)[2]
    delta = abs(math.degrees(math.atan2(math.sin(h1 - h0), math.cos(h1 - h0))))
    check_true(f"hue preserved (drifted {delta:.1f} deg)", delta < 5.0)


def test_adjust_apca() -> None:
    result = adjust("#777777", "#ffffff", target=75, metric=Metric.APCA)
    check_true("apca fix succeeds", result.success)
    check_true("apca fix meets Lc 75",
               abs(apca_contrast(result.foreground, "#ffffff")) >= 75)

    dark = adjust("#606060", "#000000", target=75, metric=Metric.APCA)
    check_true("apca dark-mode fix succeeds", dark.success)
    check_true("apca dark-mode fix lightens", dark.foreground.rgb255[0] > 0x60)


def test_adjust_terminates_everywhere() -> None:
    """Sweep the grey axis and a few hues in every mode; nothing may hang or crash."""
    swatches = [f"#{v:02x}{v:02x}{v:02x}" for v in range(0, 256, 17)]
    swatches += ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#00ffff", "#ff00ff"]
    checked = 0
    for fg in swatches:
        for bg in swatches:
            for mode in Mode:
                for metric, target in ((Metric.WCAG, 4.5), (Metric.APCA, 60)):
                    result = adjust(fg, bg, target=target, metric=metric, mode=mode)
                    checked += 1
                    if result.success:
                        score = (
                            contrast_ratio(result.foreground, result.background)
                            if metric is Metric.WCAG
                            else abs(apca_contrast(result.foreground, result.background))
                        )
                        if score < target - 1e-6:
                            FAILURES.append(
                                f"sweep {fg}/{bg} {mode.value} {metric.value}: "
                                f"claimed success but scored {score:.3f} < {target}"
                            )
    check_true(f"swept {checked} combinations", checked > 2000)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_cli() -> None:
    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    def run_cli(argv: list[str]) -> int:
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            code = main(argv)
        if not sink.getvalue().strip():
            FAILURES.append(f"cli {' '.join(argv)}: produced no output")
        return code

    check("cli check passing exits 0", run_cli(["check", "#767676", "white"]), 0)
    check("cli check failing exits 1", run_cli(["check", "#999999", "white"]), 1)
    check("cli check json", run_cli(["check", "#767676", "white", "--json"]), 0)
    check("cli large text relaxes", run_cli(["check", "#949494", "white", "--large"]), 0)
    check("cli fix exits 0", run_cli(["fix", "#777777", "white", "--target", "AAA"]), 0)
    check("cli fix json", run_cli(["fix", "#777", "white", "--json"]), 0)
    check("cli apca fix", run_cli(
        ["fix", "#777", "#fff", "--metric", "apca", "--target", "75"]), 0)
    check("cli bad color exits 2", run_cli(["check", "notacolor", "white"]), 2)

    # JSON output must actually parse — the skill relies on it.
    import json as _json  # noqa: PLC0415

    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        main(["check", "#767676", "white", "--json"])
    try:
        payload = _json.loads(sink.getvalue())
        check_true("json has wcag block", "ratio" in payload["wcag"])
        check_true("json has apca block", "lc" in payload["apca"])
    except Exception as exc:  # noqa: BLE001
        FAILURES.append(f"cli json did not parse: {exc}")


def test_docstring_examples() -> None:
    """The module docstring's examples must actually produce what they claim."""
    import doctest  # noqa: PLC0415

    import contrast as module  # noqa: PLC0415

    results = doctest.testmod(module, verbose=False, report=False)
    if results.failed:
        FAILURES.append(
            f"{results.failed} of {results.attempted} docstring examples are wrong "
            "(run `python3 -m doctest contrast.py` for details)"
        )


def run() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        try:
            test()
        except Exception as exc:  # noqa: BLE001
            FAILURES.append(f"{test.__name__} raised {type(exc).__name__}: {exc}")

    if FAILURES:
        print(f"\n{len(FAILURES)} failure(s):\n")
        for failure in FAILURES:
            print(f"  FAIL  {failure}")
        return 1
    print(f"\nAll checks passed across {len(tests)} test groups.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

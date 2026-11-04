#!/usr/bin/env python3
"""Tests for audit.py. Run with `python3 test_audit.py`."""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit import (  # noqa: E402
    apply_fixes,
    audit,
    collect_themes,
    extract_color,
    main,
    normalize_prop,
    resolve_value,
    scan_files,
    scan_text,
)
from contrast import contrast_ratio, parse_color  # noqa: E402

FAILURES: list[str] = []


def check(label: str, actual, expected) -> None:
    if actual != expected:
        FAILURES.append(f"{label}: expected {expected!r}, got {actual!r}")


def check_true(label: str, value) -> None:
    if not value:
        FAILURES.append(f"{label}: expected truthy, got {value!r}")


FIXTURE = {
    "src/styles/theme.css": """\
:root {
  --bg: #ffffff;
  --text: #767676;
  --muted: #a0a0a0;
  --brand: hsl(210 100% 45%);
}

[data-theme="dark"] {
  --bg: #111111;
  --muted: #4a4a4a;
}

body { background-color: var(--bg); color: var(--text); }
.caption { color: var(--muted); }
.btn { background: var(--brand); color: #ffffff; border-color: #6699cc; }
""",
    "src/styles/legacy.scss": """\
// a comment with a url https://example.com/not-a-comment
.card {
  background: #f5f5f5;
  .title { color: #222222; }
  .meta  { color: #999999; }
}
""",
    "src/components/Badge.jsx": """\
export const styles = {
  badge: { backgroundColor: '#eeeeee', color: '#8a8a8a', fontSize: 12 },
};
""",
    "src/index.html": (
        '<div style="background: #003366; color: #557799">hi</div>\n'
    ),
    "src/ok.css": ".fine { background: #ffffff; color: #000000; }\n",
    "node_modules/pkg/bad.css": ".x { background: #fff; color: #eee; }\n",
    "dist/bundled.css": ".y { background: #fff; color: #eee; }\n",
}


def make_fixture() -> str:
    root = tempfile.mkdtemp(prefix="contrast-audit-")
    for relative, content in FIXTURE.items():
        path = os.path.join(root, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    return root


# ---------------------------------------------------------------------------


def test_normalize_prop() -> None:
    check("camelCase", normalize_prop("backgroundColor"), "background-color")
    check("quoted", normalize_prop("'background-color'"), "background-color")
    check("uppercase", normalize_prop("COLOR"), "color")
    check("custom prop kept", normalize_prop("--Brand-BG"), "--Brand-BG")
    check("scss var kept", normalize_prop("$brandColor"), "$brandColor")


def test_scan_text_basics() -> None:
    decls = scan_text(".a { color: #fff; background: #000; }", "x.css")
    check("two decls", len(decls), 2)
    check("prop", decls[0].prop, "color")
    check("value", decls[0].value, "#fff")
    check("selector", decls[0].selector, ".a")

    nested = scan_text(".card { background: #eee; .t { color: #111; } }", "x.scss")
    inner = [d for d in nested if d.prop == "color"][0]
    check("nested scope", inner.scope, ".card .t")

    js = scan_text("const s = { color: '#fff', backgroundColor: '#000' };", "x.js")
    props = sorted(d.prop for d in js)
    check("js props", props, ["background-color", "color"])
    check("js value unquoted", [d for d in js if d.prop == "color"][0].value, "#fff")


def test_scan_text_comments() -> None:
    css = ".a { /* color: #f00; */ color: #0f0; }"
    decls = [d for d in scan_text(css, "x.css") if d.prop == "color"]
    check("block comment ignored", len(decls), 1)
    check("live decl wins", decls[0].value, "#0f0")

    scss = ".a {\n  // color: #f00;\n  color: #0f0;\n}"
    decls = [d for d in scan_text(scss, "x.scss") if d.prop == "color"]
    check("line comment ignored", len(decls), 1)

    # A URL is not a line comment.
    url = '.a { background: url(https://e.com/i.png); color: #0f0; }'
    decls = [d for d in scan_text(url, "x.css") if d.prop == "color"]
    check("url survives", len(decls), 1)


def test_offsets_are_exact() -> None:
    """--fix depends on value spans pointing at exactly the color text."""
    for source, name in (
        (".a { color: #abcdef; }", "x.css"),
        ("const s = { color: '#abcdef' };", "x.js"),
        (".a { color:#abcdef }", "x.css"),
        (".a {\n  color:   #abcdef ;\n}", "x.css"),
    ):
        decl = [d for d in scan_text(source, name) if d.prop == "color"][0]
        span = source[decl.value_start : decl.value_end]
        check(f"span for {name} in {source!r}", span, "#abcdef")


def test_line_numbers() -> None:
    source = "\n\n.a {\n  color: #fff;\n}\n"
    decl = [d for d in scan_text(source, "x.css") if d.prop == "color"][0]
    check("line number", decl.line, 4)


def test_variable_resolution() -> None:
    variables = {"--a": "#ff0000", "--b": "var(--a)", "$s": "#00ff00", "@l": "#0000ff"}
    check("css var", resolve_value("var(--a)", variables), "#ff0000")
    check("chained var", resolve_value("var(--b)", variables), "#ff0000")
    check("var fallback", resolve_value("var(--missing, #123456)", variables), "#123456")
    check("scss var", resolve_value("$s", variables), "#00ff00")
    check("less var", resolve_value("@l", variables), "#0000ff")
    check("unknown var untouched", resolve_value("var(--nope)", variables), "var(--nope)")


def test_extract_color() -> None:
    check("plain hex", extract_color("#abc", {}), parse_color("#aabbcc"))
    check("shorthand picks color", extract_color("#fff url(x) no-repeat", {}),
          parse_color("#ffffff"))
    check("gradient skipped", extract_color("linear-gradient(#fff, #000)", {}), None)
    check("keyword skipped", extract_color("inherit", {}), None)
    check("currentcolor skipped", extract_color("currentColor", {}), None)
    check("named color", extract_color("rebeccapurple", {}), parse_color("#663399"))
    check("hsl", extract_color("hsl(0 100% 50%)", {}), parse_color("#ff0000"))


def test_themes() -> None:
    decls = scan_text(FIXTURE["src/styles/theme.css"], "theme.css")
    themes = collect_themes(decls)
    names = [t.name for t in themes]
    check("base theme first", names[0], "base")
    check_true("dark theme found", any("dark" in n for n in names))

    base = themes[0]
    check("base bg", base.variables["--bg"], "#ffffff")
    dark = [t for t in themes if "dark" in t.name][0]
    check("dark bg overrides", dark.variables["--bg"], "#111111")
    check("dark inherits unset var", dark.variables["--text"], "#767676")


def test_audit_end_to_end() -> None:
    root = make_fixture()
    try:
        findings, _, stats = audit([root], target="AA")

        check_true("skips node_modules and dist", stats["files_scanned"] == 5)
        check_true("finds failures", len(findings) >= 6)
        check_true("sorted worst first",
                   all(findings[i].deficit >= findings[i + 1].deficit
                       for i in range(len(findings) - 1)))

        located = {(os.path.relpath(f.pair.fg_decl.path, root), f.pair.fg_decl.line)
                   for f in findings}
        check_true("catches scss nested", ("src/styles/legacy.scss", 5) in located)
        check_true("catches jsx", ("src/components/Badge.jsx", 2) in located)
        check_true("catches inline html", ("src/index.html", 1) in located)

        # The passing file must not appear at all.
        check_true("no false positive on ok.css",
                   not any("ok.css" in f.pair.fg_decl.path for f in findings))
        # Nor should white-on-brand, which clears AA at 4.57:1.
        check_true("no false positive on btn text",
                   not any(f.pair.foreground == parse_color("#ffffff")
                           and f.pair.kind == "text" for f in findings))

        themes = {f.pair.theme for f in findings}
        check_true("audits dark theme separately", any("dark" in t for t in themes))

        # Every suggestion must actually work, measured from its own hex.
        for finding in findings:
            if finding.suggestion is None:
                continue
            achieved = contrast_ratio(finding.suggestion.hex, finding.pair.background.hex)
            if achieved < finding.target:
                FAILURES.append(
                    f"suggestion {finding.suggestion.hex} for {finding.pair.fg_decl.location} "
                    f"scores {achieved:.3f} < {finding.target}"
                )

        # Variable-sourced values must not be marked auto-fixable.
        for finding in findings:
            if "var(" in finding.pair.fg_decl.value and finding.fixable:
                FAILURES.append(
                    f"{finding.pair.fg_decl.location}: var() value marked fixable"
                )
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_fix_is_surgical_and_converges() -> None:
    root = make_fixture()
    try:
        before = {p: open(os.path.join(root, p), encoding="utf-8").read() for p in FIXTURE}

        findings, sources, _ = audit([root], target="AA")
        expected = sum(1 for f in findings if f.fixable)
        applied = apply_fixes(findings, sources)
        check("applied count matches fixable", sum(applied.values()), expected)

        after = {p: open(os.path.join(root, p), encoding="utf-8").read() for p in FIXTURE}

        check("untouched files stay identical", after["src/ok.css"], before["src/ok.css"])
        check("vendored files untouched",
              after["node_modules/pkg/bad.css"], before["node_modules/pkg/bad.css"])

        # Quotes, comments, and structure must survive.
        check_true("jsx quotes preserved", "color: '#" in after["src/components/Badge.jsx"])
        check_true("jsx sibling keys intact", "fontSize: 12" in after["src/components/Badge.jsx"])
        check_true("scss comment preserved", "https://example.com" in after["src/styles/legacy.scss"])
        check_true("line count unchanged",
                   all(after[p].count("\n") == before[p].count("\n") for p in FIXTURE))

        # A second pass must find strictly fewer failures, and the survivors
        # must all be the ones that need a human.
        again, _, _ = audit([root], target="AA")
        check_true("fixing reduced failures", len(again) < len(findings))
        check_true("survivors all need manual edits",
                   all(not f.fixable for f in again))

        # And a third pass must be stable — no oscillation.
        third, _, _ = audit([root], target="AA")
        check("audit is stable", len(third), len(again))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_cli() -> None:
    root = make_fixture()
    try:
        def run(argv: list[str]) -> "tuple[int, str]":
            sink = io.StringIO()
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                code = main(argv)
            return code, sink.getvalue()

        code, out = run(["scan", root])
        check("scan exits 0", code, 0)
        check_true("scan lists colors", "#767676" in out)

        code, out = run(["scan", root, "--json"])
        import json  # noqa: PLC0415
        payload = json.loads(out)
        check_true("scan json has colors", len(payload["colors"]) > 5)

        code, out = run(["check", root])
        check("check exits 1 on failures", code, 1)
        check_true("check reports suggestions", "suggest" in out)

        code, out = run(["check", root, "--json"])
        payload = json.loads(out)
        check_true("json findings", len(payload["findings"]) > 0)
        check_true("json stats", payload["stats"]["files_scanned"] == 5)

        code, out = run(["check", root, "--confidence", "same-block"])
        check_true("stricter confidence reports fewer", "failing pair" in out)

        code, out = run(["check", os.path.join(root, "src/ok.css")])
        check("clean file exits 0", code, 0)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_handles_junk_without_crashing() -> None:
    """Malformed input must degrade quietly, not raise."""
    junk = [
        "", "{", "}", "}{", ".a { color: ; }", ".a { : #fff }",
        ".a { color: #zzz; }", "color: #fff", ".a { color: rgb(); }",
        ".a { color: var(--x); }", "/*", "'", '.a { content: "}"; color: #fff }',
        ".a { color: #fff", "@media (min-width: 0) { .a { color: #fff; } }",
    ]
    for source in junk:
        try:
            scan_text(source, "junk.css")
        except Exception as exc:  # noqa: BLE001
            FAILURES.append(f"scan_text crashed on {source!r}: {type(exc).__name__}: {exc}")


def run() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        try:
            test()
        except Exception as exc:  # noqa: BLE001
            import traceback  # noqa: PLC0415
            FAILURES.append(
                f"{test.__name__} raised {type(exc).__name__}: {exc}\n"
                + "".join(traceback.format_tb(exc.__traceback__)[-2:])
            )

    if FAILURES:
        print(f"\n{len(FAILURES)} failure(s):\n")
        for failure in FAILURES:
            print(f"  FAIL  {failure}")
        return 1
    print(f"\nAll checks passed across {len(tests)} test groups.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

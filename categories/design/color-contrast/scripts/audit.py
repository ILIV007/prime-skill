#!/usr/bin/env python3
"""Find and repair color-contrast failures in a codebase.

Zero dependencies beyond ``contrast.py``, which must sit alongside this file.

What it does
------------
Scans source files for color declarations, works out which foreground goes
with which background, measures every pair with WCAG 2.x and APCA, and reports
the failures worst-first. ``--fix`` rewrites literal color values in place.

It understands CSS, SCSS, LESS, inline ``style`` attributes, and JS/TS style
objects (styled-components, Emotion, React Native ``StyleSheet``), including
``var()`` / ``$var`` / ``@var`` resolution and light-vs-dark theme blocks.

What it cannot do
-----------------
Pairing is static, so it only sees a pair when one block declares both colors,
or a block declares a foreground and an ancestor block declares the background.
Contrast that arises from the runtime cascade, JS-computed styles, images
behind text, or utility classes resolved by a framework at build time is
invisible here. A clean report means "no failures I can see", not "no
failures". Confirm against rendered pages.

Usage::

    audit.py scan  src/                 # every color found, with sources
    audit.py check src/                 # failures, worst first
    audit.py check src/ --target AAA --json
    audit.py check src/ --fix           # rewrite literal values in place
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Optional, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contrast import (  # noqa: E402
    Color,
    ContrastError,
    Metric,
    Mode,
    WCAGLevel,
    adjust,
    apca_contrast,
    contrast_ratio,
    parse_color,
)

__version__ = "1.0.0"

SOURCE_EXTENSIONS = {
    ".css", ".scss", ".sass", ".less", ".styl",
    ".html", ".htm", ".vue", ".svelte", ".astro",
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
}

SKIP_DIRECTORIES = {
    "node_modules", ".git", ".hg", ".svn", "dist", "build", "out",
    "vendor", "coverage", "__pycache__", ".venv", "venv", ".next",
    ".nuxt", ".svelte-kit", ".cache", "target", "bower_components",
}

#: Properties whose value paints text or an icon glyph.
FOREGROUND_PROPS = {"color", "fill", "stroke", "caret-color", "text-decoration-color"}

BACKGROUND_PROPS = {"background", "background-color"}

#: Properties covered by SC 1.4.11 Non-text Contrast, which needs only 3:1.
NON_TEXT_PROPS = {"border-color", "border-top-color", "border-right-color",
                  "border-bottom-color", "border-left-color", "outline-color"}

#: Selectors that mark a theme rather than base styling.
_THEME_RE = re.compile(
    r"(?:^|[\s.\[:#(])(?:dark|light)(?:[\s\]\-_.,)]|$)"
    r"|prefers-color-scheme"
    r"|data-theme"
    r"|\[theme",
    re.IGNORECASE,
)

#: A camelCase boundary needs a lowercase or digit before the capital, so that
#: an all-caps property such as COLOR is left alone rather than shredded.
_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")

#: Anything that could name or spell a color. Deliberately loose; values that
#: fail to parse are simply dropped.
_COLOR_TOKEN_RE = re.compile(
    r"#[0-9a-fA-F]{3,8}\b"
    r"|(?:rgba?|hsla?|oklch|oklab)\s*\([^()]*\)"
    r"|\b[a-zA-Z]{3,20}\b",
)

_VAR_RE = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*(?:\([^()]*\)[^()]*)*))?\)")
_SCSS_VAR_RE = re.compile(r"\$([\w-]+)")
_LESS_VAR_RE = re.compile(r"@([\w-]+)(?![\w\-(])")


# ---------------------------------------------------------------------------
# Source scanning
# ---------------------------------------------------------------------------


@dataclass
class Declaration:
    """One ``property: value`` pair found in a source file."""

    prop: str
    value: str
    path: str
    line: int
    value_start: int
    value_end: int
    depth: int
    selector: str
    scope: str  #: the selector chain, used to tell themes apart

    @property
    def location(self) -> str:
        return f"{self.path}:{self.line}"


def normalize_prop(raw: str) -> str:
    """``backgroundColor`` / ``'background-color'`` / ``BACKGROUND`` -> ``background-color``."""
    text = raw.strip().strip("'\"` \t\n").strip()
    if text.startswith(("--", "$", "@")):
        return text
    return _CAMEL_RE.sub("-", text).lower()


def _blank_comments(text: str) -> str:
    """Replace comment bodies with spaces, preserving every byte offset."""
    out = list(text)
    i, n = 0, len(text)
    quote: Optional[str] = None

    while i < n:
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'`":
            quote = ch
            i += 1
            continue
        if ch == "/" and i + 1 < n:
            nxt = text[i + 1]
            if nxt == "*":
                end = text.find("*/", i + 2)
                end = n if end == -1 else end + 2
                for j in range(i, end):
                    if out[j] != "\n":
                        out[j] = " "
                i = end
                continue
            if nxt == "/":
                # Not a comment when it follows a colon: that is a URL scheme.
                prev = text[:i].rstrip()
                if not prev.endswith(":"):
                    end = text.find("\n", i)
                    end = n if end == -1 else end
                    for j in range(i, end):
                        out[j] = " "
                    i = end
                    continue
        i += 1

    return "".join(out)


def scan_text(text: str, path: str) -> "list[Declaration]":
    """Extract declarations from CSS-like or JS-object-like source.

    Both dialects are ``{ key: value }`` with a separator, so one walk handles
    them. Blocks nest, which is what lets a SCSS rule inherit its parent's
    background.
    """
    source = _blank_comments(text)
    n = len(source)
    declarations: list[Declaration] = []
    stack: list[str] = []

    buf_start = 0
    paren_depth = 0
    quote: Optional[str] = None
    line = 1
    line_at: list[int] = []  # newline offsets, for offset -> line lookup
    for idx, ch in enumerate(source):
        if ch == "\n":
            line_at.append(idx)

    def line_of(offset: int) -> int:
        lo, hi = 0, len(line_at)
        while lo < hi:
            mid = (lo + hi) // 2
            if line_at[mid] < offset:
                lo = mid + 1
            else:
                hi = mid
        return lo + 1

    def flush(start: int, end: int) -> None:
        chunk = source[start:end]
        if ":" not in chunk:
            return
        depth = 0
        colon = -1
        for i, c in enumerate(chunk):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == ":" and depth == 0:
                colon = i
                break
        if colon <= 0:
            return
        prop = normalize_prop(chunk[:colon])
        if not prop or " " in prop or "{" in prop:
            return
        raw_value = chunk[colon + 1 :]
        lead = len(raw_value) - len(raw_value.lstrip())
        value = raw_value.strip().rstrip(",;").rstrip()
        if not value:
            return
        value_start = start + colon + 1 + lead
        value_end = value_start + len(value)
        # JS style objects quote their values. Narrow the span to the color
        # itself so --fix can replace it without eating the quotes.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'`":
            inner = value[1:-1]
            inner_lead = len(inner) - len(inner.lstrip())
            value = inner.strip()
            value_start += 1 + inner_lead
            value_end = value_start + len(value)
        if not value:
            return
        declarations.append(
            Declaration(
                prop=prop,
                value=value,
                path=path,
                line=line_of(value_start),
                value_start=value_start,
                depth=len(stack),
                selector=stack[-1] if stack else "",
                scope=" ".join(stack),
                value_end=value_end,
            )
        )

    i = 0
    while i < n:
        ch = source[i]

        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue

        if ch in "\"'`":
            quote = ch
            i += 1
            continue

        if ch == "(":
            paren_depth += 1
        elif ch == ")":
            paren_depth = max(0, paren_depth - 1)
        elif paren_depth == 0:
            if ch == "{":
                selector = source[buf_start:i].strip().strip(",")
                # JS object literals have no selector; keep the assignment name.
                stack.append(selector[-120:])
                buf_start = i + 1
            elif ch == "}":
                flush(buf_start, i)
                if stack:
                    stack.pop()
                buf_start = i + 1
            elif ch == ";":
                flush(buf_start, i)
                buf_start = i + 1
            elif ch == ",":
                # A comma only ends a declaration in JS-style objects, where the
                # buffer already holds a `key: value`. In CSS it separates
                # selectors or function arguments, which must stay intact.
                chunk = source[buf_start:i]
                if ":" in chunk and "{" not in chunk:
                    flush(buf_start, i)
                    buf_start = i + 1
        i += 1

    flush(buf_start, n)
    return declarations


def scan_html_inline(text: str, path: str) -> "list[Declaration]":
    """Pull declarations out of ``style="..."`` attributes."""
    declarations: list[Declaration] = []
    for match in re.finditer(r"""style\s*=\s*(["'])(.*?)\1""", text, re.DOTALL):
        body = match.group(2)
        offset = match.start(2)
        line = text.count("\n", 0, offset) + 1
        cursor = 0
        for part in body.split(";"):
            if ":" in part:
                prop_raw, _, value_raw = part.partition(":")
                value = value_raw.strip()
                if value:
                    start = offset + cursor + len(prop_raw) + 1
                    start += len(value_raw) - len(value_raw.lstrip())
                    declarations.append(
                        Declaration(
                            prop=normalize_prop(prop_raw),
                            value=value,
                            path=path,
                            line=line,
                            value_start=start,
                            value_end=start + len(value),
                            depth=1,
                            selector="[inline style]",
                            scope="[inline style]",
                        )
                    )
            cursor += len(part) + 1
    return declarations


def iter_source_files(paths: "Sequence[str]") -> "Iterator[str]":
    for target in paths:
        if os.path.isfile(target):
            yield target
            continue
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRECTORIES and not d.startswith(".")]
            for name in sorted(files):
                if os.path.splitext(name)[1].lower() in SOURCE_EXTENSIONS:
                    yield os.path.join(root, name)


def scan_files(paths: "Sequence[str]") -> "tuple[list[Declaration], dict[str, str]]":
    """Return every declaration found, plus the raw text of each file read."""
    declarations: list[Declaration] = []
    sources: dict[str, str] = {}
    for path in iter_source_files(paths):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            continue
        sources[path] = text
        declarations.extend(scan_text(text, path))
        if os.path.splitext(path)[1].lower() in {".html", ".htm", ".vue", ".svelte", ".astro"}:
            declarations.extend(scan_html_inline(text, path))
    return declarations, sources


# ---------------------------------------------------------------------------
# Variables and themes
# ---------------------------------------------------------------------------


@dataclass
class Theme:
    """A named set of variable bindings — usually base, light, and dark."""

    name: str
    variables: "dict[str, str]" = field(default_factory=dict)
    definitions: "dict[str, Declaration]" = field(default_factory=dict)


def collect_themes(declarations: "Iterable[Declaration]") -> "list[Theme]":
    """Split variable definitions into a base theme plus any theme overrides.

    Most real contrast bugs live in dark mode, and a flat variable map would
    silently let the last-parsed definition win. Keeping themes apart means
    each one gets audited on its own terms.
    """
    base = Theme("base")
    themes: "dict[str, Theme]" = {}

    for decl in declarations:
        if not decl.prop.startswith(("--", "$", "@")):
            continue
        key = decl.prop
        if _THEME_RE.search(decl.scope):
            label = _theme_label(decl.scope)
            theme = themes.setdefault(label, Theme(label))
            theme.variables[key] = decl.value
            theme.definitions[key] = decl
        else:
            base.variables[key] = decl.value
            base.definitions[key] = decl

    result = [base]
    for theme in themes.values():
        merged = Theme(theme.name, dict(base.variables), dict(base.definitions))
        merged.variables.update(theme.variables)
        merged.definitions.update(theme.definitions)
        result.append(merged)
    return result


def _theme_label(scope: str) -> str:
    if "prefers-color-scheme" in scope:
        match = re.search(r"prefers-color-scheme\s*:\s*(\w+)", scope)
        return f"@media {match.group(1)}" if match else "@media color-scheme"
    match = re.search(r"[.\[][\w\-\[\]=\"']*(?:dark|light)[\w\-\[\]=\"']*", scope, re.IGNORECASE)
    return match.group(0) if match else scope[-40:]


def resolve_value(value: str, variables: "dict[str, str]", depth: int = 0) -> str:
    """Substitute ``var(--x)``, ``$x``, and ``@x`` references, following chains."""
    if depth > 10:
        return value

    def replace_css(match: "re.Match[str]") -> str:
        name, fallback = match.group(1), match.group(2)
        if name in variables:
            return variables[name]
        return fallback.strip() if fallback else match.group(0)

    resolved = _VAR_RE.sub(replace_css, value)
    resolved = _SCSS_VAR_RE.sub(
        lambda m: variables.get(f"${m.group(1)}", m.group(0)), resolved
    )
    resolved = _LESS_VAR_RE.sub(
        lambda m: variables.get(f"@{m.group(1)}", m.group(0)), resolved
    )
    return resolve_value(resolved, variables, depth + 1) if resolved != value else value


def extract_color(value: str, variables: "dict[str, str]") -> "Optional[Color]":
    """Best-effort single color from a declaration value.

    Shorthand like ``background: #fff url(x) no-repeat`` carries a color plus
    other tokens, so this takes the first token that parses as a color. Values
    naming several colors — gradients — return ``None``, because contrast
    against a gradient is not a single number.
    """
    text = resolve_value(value.strip(), variables)
    lowered = text.lower()
    if "gradient" in lowered or "image" in lowered:
        return None
    if lowered in {"inherit", "initial", "unset", "revert", "currentcolor", "none", "auto"}:
        return None

    try:
        return parse_color(text)
    except ContrastError:
        pass

    for match in _COLOR_TOKEN_RE.finditer(text):
        token = match.group(0)
        try:
            return parse_color(token)
        except ContrastError:
            continue
    return None


# ---------------------------------------------------------------------------
# Pairing
# ---------------------------------------------------------------------------


@dataclass
class Pair:
    """A foreground and the background it is measured against."""

    foreground: Color
    background: Color
    fg_decl: Declaration
    bg_decl: "Optional[Declaration]"
    theme: str
    confidence: str  #: same-block | ancestor | page
    kind: str  #: text | non-text

    @property
    def target(self) -> float:
        return 3.0 if self.kind == "non-text" else 4.5

    @property
    def ratio(self) -> float:
        return contrast_ratio(self.foreground, self.background)

    @property
    def lc(self) -> float:
        return apca_contrast(self.foreground, self.background)


def _page_background(
    declarations: "Sequence[Declaration]", variables: "dict[str, str]"
) -> "Optional[tuple[Color, Declaration]]":
    """The background a bare foreground most likely sits on."""
    candidates = []
    for decl in declarations:
        if decl.prop in BACKGROUND_PROPS:
            selector = decl.selector.lower()
            if any(k in selector for k in ("body", "html", ":root", "*")):
                candidates.append(decl)
    for decl in reversed(candidates):
        color = extract_color(decl.value, variables)
        if color is not None and color.opaque:
            return color, decl
    for name in ("--background", "--bg", "--color-background", "--surface", "--body-bg"):
        if name in variables:
            color = extract_color(variables[name], variables)
            if color is not None and color.opaque:
                return color, None  # type: ignore[return-value]
    return None


def build_pairs(
    declarations: "Sequence[Declaration]",
    theme: Theme,
    *,
    assumed_background: "Optional[Color]" = None,
) -> "list[Pair]":
    """Match every foreground declaration to the background behind it."""
    by_scope: "dict[str, list[Declaration]]" = defaultdict(list)
    for decl in declarations:
        by_scope[decl.scope].append(decl)

    # A background declared in a scope applies to that scope and its descendants.
    scope_backgrounds: "dict[str, tuple[Color, Declaration]]" = {}
    for scope, decls in by_scope.items():
        for decl in decls:
            if decl.prop in BACKGROUND_PROPS:
                color = extract_color(decl.value, theme.variables)
                if color is not None and color.opaque:
                    scope_backgrounds[scope] = (color, decl)

    page = _page_background(declarations, theme.variables)
    if page is None and assumed_background is not None:
        page = (assumed_background, None)  # type: ignore[assignment]

    pairs: "list[Pair]" = []
    for decl in declarations:
        kind = (
            "text" if decl.prop in FOREGROUND_PROPS
            else "non-text" if decl.prop in NON_TEXT_PROPS
            else None
        )
        if kind is None:
            continue
        foreground = extract_color(decl.value, theme.variables)
        if foreground is None:
            continue

        found = scope_backgrounds.get(decl.scope)
        confidence = "same-block"
        if found is None:
            for scope in sorted(scope_backgrounds, key=len, reverse=True):
                if scope and decl.scope.startswith(scope):
                    found = scope_backgrounds[scope]
                    confidence = "ancestor"
                    break
        if found is None and page is not None:
            found = page
            confidence = "page"
        if found is None:
            continue

        background, bg_decl = found
        if not foreground.opaque:
            foreground = foreground.over(background)
        if foreground == background:
            continue

        pairs.append(
            Pair(foreground, background, decl, bg_decl, theme.name, confidence, kind)
        )
    return pairs


# ---------------------------------------------------------------------------
# Auditing
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    """One failing pair, with a suggested replacement."""

    pair: Pair
    target: float
    ratio: float
    lc: float
    suggestion: "Optional[Color]"
    suggested_ratio: "Optional[float]"
    fixable: bool
    reason: str

    @property
    def deficit(self) -> float:
        return self.target - self.ratio

    def as_dict(self) -> dict:
        pair = self.pair
        return {
            "file": pair.fg_decl.path,
            "line": pair.fg_decl.line,
            "selector": pair.fg_decl.selector,
            "theme": pair.theme,
            "confidence": pair.confidence,
            "kind": pair.kind,
            "property": pair.fg_decl.prop,
            "declared": pair.fg_decl.value,
            "foreground": pair.foreground.hex,
            "background": pair.background.hex,
            "background_from": pair.bg_decl.location if pair.bg_decl else "assumed",
            "ratio": round(self.ratio, 2),
            "target": self.target,
            "apca_lc": round(self.lc, 1),
            "suggestion": self.suggestion.hex if self.suggestion else None,
            "suggested_ratio": (
                round(self.suggested_ratio, 2) if self.suggested_ratio else None
            ),
            "fixable": self.fixable,
            "reason": self.reason,
        }


def audit(
    paths: "Sequence[str]",
    *,
    target: "str | float" = "AA",
    min_confidence: str = "page",
    assumed_background: "Optional[str]" = None,
) -> "tuple[list[Finding], dict[str, str], dict]":
    """Scan ``paths`` and return failing pairs worst-first."""
    threshold = WCAGLevel.parse(target)
    declarations, sources = scan_files(paths)
    themes = collect_themes(declarations)
    assumed = parse_color(assumed_background) if assumed_background else None

    allowed = {"same-block": 1, "ancestor": 2, "page": 3}
    limit = allowed.get(min_confidence, 2)

    findings: "list[Finding]" = []
    seen: "set[tuple]" = set()
    total_pairs = 0

    for theme in themes:
        for pair in build_pairs(declarations, theme, assumed_background=assumed):
            if allowed[pair.confidence] > limit:
                continue
            total_pairs += 1
            pair_target = 3.0 if pair.kind == "non-text" else threshold
            ratio = pair.ratio
            if ratio >= pair_target:
                continue

            key = (
                pair.fg_decl.path, pair.fg_decl.line, pair.fg_decl.prop,
                pair.foreground.hex, pair.background.hex,
            )
            if key in seen:
                continue
            seen.add(key)

            literal = extract_color(pair.fg_decl.value, {}) is not None
            fixed = adjust(
                pair.foreground, pair.background, target=pair_target, mode=Mode.FOREGROUND
            )
            reason = (
                "literal value; --fix can rewrite it"
                if literal
                else "value comes from a variable; edit the token definition instead"
            )
            if not fixed.success:
                reason = "cannot reach the target by changing the foreground alone"

            findings.append(
                Finding(
                    pair=pair,
                    target=pair_target,
                    ratio=ratio,
                    lc=pair.lc,
                    suggestion=fixed.foreground if fixed.success else None,
                    suggested_ratio=fixed.achieved if fixed.success else None,
                    fixable=literal and fixed.success,
                    reason=reason,
                )
            )

    findings.sort(key=lambda f: (-f.deficit, f.pair.fg_decl.path, f.pair.fg_decl.line))
    stats = {
        "files_scanned": len(sources),
        "declarations": len(declarations),
        "themes": [t.name for t in themes],
        "pairs_checked": total_pairs,
        "failures": len(findings),
    }
    return findings, sources, stats


def apply_fixes(findings: "Sequence[Finding]", sources: "dict[str, str]") -> "dict[str, int]":
    """Rewrite literal foreground values in place. Returns edits per file.

    Edits are applied back-to-front so earlier offsets stay valid, and only
    where the recorded span still holds exactly the value we scanned.
    """
    edits: "dict[str, list[tuple[int, int, str]]]" = defaultdict(list)
    for finding in findings:
        if not finding.fixable or finding.suggestion is None:
            continue
        decl = finding.pair.fg_decl
        edits[decl.path].append(
            (decl.value_start, decl.value_end, finding.suggestion.hex)
        )

    applied: "dict[str, int]" = {}
    for path, spans in edits.items():
        text = sources.get(path)
        if text is None:
            continue
        count = 0
        for start, end, replacement in sorted(spans, key=lambda s: -s[0]):
            original = text[start:end]
            try:
                if parse_color(original) == parse_color(replacement):
                    continue
            except ContrastError:
                continue  # span no longer holds a bare color; leave it alone
            text = text[:start] + replacement + text[end:]
            count += 1
        if count:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
            applied[path] = count
    return applied


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _scan_command(args: argparse.Namespace) -> int:
    declarations, _ = scan_files(args.paths)
    themes = collect_themes(declarations)
    base = themes[0]

    rows = []
    for decl in declarations:
        if decl.prop.startswith(("--", "$", "@")) or decl.prop in (
            FOREGROUND_PROPS | BACKGROUND_PROPS | NON_TEXT_PROPS
        ):
            color = extract_color(decl.value, base.variables)
            if color is not None:
                rows.append((decl, color))

    if args.json:
        print(json.dumps(
            {
                "themes": [t.name for t in themes],
                "colors": [
                    {
                        "file": d.path, "line": d.line, "selector": d.selector,
                        "property": d.prop, "declared": d.value, "resolved": c.hex,
                    }
                    for d, c in rows
                ],
            },
            indent=2,
        ))
        return 0

    if not rows:
        print("No colors found.")
        return 0

    print(f"{len(rows)} color declarations across {len({d.path for d, _ in rows})} files")
    if len(themes) > 1:
        print(f"Themes detected: {', '.join(t.name for t in themes)}")
    print()

    by_file: "dict[str, list]" = defaultdict(list)
    for decl, color in rows:
        by_file[decl.path].append((decl, color))
    for path in sorted(by_file):
        print(path)
        for decl, color in by_file[path]:
            declared = decl.value if len(decl.value) <= 34 else decl.value[:31] + "..."
            suffix = "" if declared.lower() == color.hex else f"  -> {color.hex}"
            print(f"  {decl.line:>5}  {decl.prop:<24} {declared}{suffix}")
        print()
    return 0


def _check_command(args: argparse.Namespace) -> int:
    findings, sources, stats = audit(
        args.paths,
        target=args.target,
        min_confidence=args.confidence,
        assumed_background=args.assume_bg,
    )

    if args.json:
        payload = {"stats": stats, "findings": [f.as_dict() for f in findings]}
        if args.fix:
            payload["applied"] = apply_fixes(findings, sources)
        print(json.dumps(payload, indent=2))
        return 1 if findings else 0

    print(
        f"Scanned {stats['files_scanned']} files, "
        f"{stats['pairs_checked']} color pairs, "
        f"themes: {', '.join(stats['themes'])}"
    )

    if not findings:
        print()
        print(f"No pairs fall below {WCAGLevel.parse(args.target)}:1.")
        print("Static pairing cannot see cascade-derived contrast — verify rendered pages.")
        return 0

    print(f"{len(findings)} failing pair(s), worst first:")
    print()

    by_file: "dict[str, list[Finding]]" = defaultdict(list)
    for finding in findings:
        by_file[finding.pair.fg_decl.path].append(finding)

    for path in sorted(by_file, key=lambda p: -max(f.deficit for f in by_file[p])):
        print(path)
        for finding in by_file[path]:
            pair = finding.pair
            theme = f" [{pair.theme}]" if pair.theme != "base" else ""
            note = "" if pair.confidence == "same-block" else f" ({pair.confidence} bg)"
            print(f"  {pair.fg_decl.line:>5}  {pair.fg_decl.selector or '?'}{theme}")
            print(
                f"         {pair.fg_decl.prop}: {pair.fg_decl.value}"
                f"  =>  {pair.foreground.hex} on {pair.background.hex}{note}"
            )
            print(
                f"         {finding.ratio:.2f}:1  (needs {finding.target}:1)"
                f"   APCA Lc {finding.lc:+.1f}"
            )
            if finding.suggestion:
                print(
                    f"         suggest {finding.suggestion.hex} "
                    f"-> {finding.suggested_ratio:.2f}:1   {finding.reason}"
                )
            else:
                print(f"         {finding.reason}")
            print()

    if args.fix:
        applied = apply_fixes(findings, sources)
        if applied:
            total = sum(applied.values())
            print(f"Applied {total} edit(s) across {len(applied)} file(s):")
            for path in sorted(applied):
                print(f"  {applied[path]:>3}  {path}")
        else:
            print("No literal values could be rewritten automatically.")
        skipped = [f for f in findings if not f.fixable]
        if skipped:
            print()
            print(f"{len(skipped)} finding(s) need a manual edit — see the reasons above.")
    else:
        fixable = sum(1 for f in findings if f.fixable)
        if fixable:
            print(f"{fixable} of {len(findings)} can be rewritten automatically: rerun with --fix")

    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audit",
        description="Find and repair color-contrast failures in a codebase.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="list every color declaration found")
    scan.add_argument("paths", nargs="+")
    scan.add_argument("--json", action="store_true")
    scan.set_defaults(func=_scan_command)

    check = sub.add_parser("check", help="report pairs that fail a contrast target")
    check.add_argument("paths", nargs="+")
    check.add_argument("--target", default="AA", help="AA, AAA, or a ratio (default: AA)")
    check.add_argument(
        "--confidence",
        choices=["same-block", "ancestor", "page"],
        default="page",
        help=(
            "how speculative a pairing may be before it is reported. "
            "same-block is certain, ancestor is near-certain, page assumes bare "
            "foregrounds sit on the detected body background (default: page)"
        ),
    )
    check.add_argument(
        "--assume-bg",
        metavar="COLOR",
        help="background for foregrounds with no declared surface, when none is detected",
    )
    check.add_argument("--fix", action="store_true", help="rewrite literal values in place")
    check.add_argument("--json", action="store_true")
    check.set_defaults(func=_check_command)

    return parser


def main(argv: "Optional[Sequence[str]]" = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ContrastError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

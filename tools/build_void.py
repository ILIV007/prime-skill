#!/usr/bin/env python3
"""Validate void.json and regenerate the README Void table.

Usage:
  python3 tools/build_void.py           # regenerate the README Void table
  python3 tools/build_void.py --check   # exit non-zero if stale/invalid

Stdlib only. Repo root is the parent of this script's directory.

Void is deliberately separate from the skills and the MCP shelf: its own
manifest (void.json), its own schema, its own validator, its own CI step.
A Void entry is structurally distinguishable from a skill entry and from
an MCP entry — it carries `why_valuable` and `why_not_included`, and it
carries NO category, tags, entry/special flags, transport, requires,
access, or paid fields. Void entries are link-only, vetted only, capped
at 12, and never counted anywhere: not in the skills total, not in any
category, not in the MCP count, not in tag statistics. Void never flows
into skills.json or mcps.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "void.json"
README = ROOT / "README.md"
START = "<!-- GENERATED:VOID:START -->"
END = "<!-- GENERATED:VOID:END -->"
CAP = 12
REQUIRED = ["name", "title", "description", "why_valuable",
            "why_not_included", "source", "license", "stars_at_import",
            "added"]
SOURCE_FIELDS = ["repo", "url", "commit"]
# Fields that must NEVER appear on a Void entry: they would make it look
# like a skill or an MCP entry to tooling that scans manifests.
FORBIDDEN = ["category", "tags", "entry", "special", "transport",
             "requires", "access", "paid", "adapted"]


def esc(text):
    return str(text).replace("|", "\\|")


def load(errors):
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"void.json: unreadable: {exc}")
        return None, []
    entries = data.get("entries")
    if not isinstance(entries, list):
        errors.append("void.json: 'entries' must be a list")
        return data, []
    return data, entries


def validate(data, entries, errors):
    if data is not None and data.get("count") != len(entries):
        errors.append(f"void.json: count {data.get('count')} != {len(entries)} entr(ies)")
    if len(entries) > CAP:
        errors.append(f"void.json: {len(entries)} entries exceeds the hard cap of {CAP}")
    seen = set()
    for entry in entries:
        name = entry.get("name") or "?"
        label = f"void.json:{name}"
        for field in REQUIRED:
            if field not in entry:
                errors.append(f"{label}: missing field '{field}'")
        for field in FORBIDDEN:
            if field in entry:
                errors.append(f"{label}: forbidden field '{field}' — "
                              "a Void entry must not look like a skill or MCP entry")
        if name in seen:
            errors.append(f"{label}: duplicate entry name")
        seen.add(name)
        source = entry.get("source") or {}
        for field in SOURCE_FIELDS:
            if not source.get(field):
                errors.append(f"{label}: source.{field} is empty")
        for field in ("description", "why_valuable", "why_not_included"):
            if not (entry.get(field) or "").strip():
                errors.append(f"{label}: '{field}' is empty")
        if not isinstance(entry.get("stars_at_import"), int):
            errors.append(f"{label}: stars_at_import must be an integer")


def entry_row(entry):
    source = entry["source"]
    commit = source["commit"][:7]
    stars = f"{entry['stars_at_import']:,}"
    return (f"| [{entry['name']}]({source['url']}) | {esc(entry['description'])} "
            f"| {esc(entry['why_valuable'])} | {esc(entry['why_not_included'])} "
            f"| [{source['repo']}]({source['url']}) @ {commit} · {esc(entry['license'])} · ★ {stars} |")


def render_readme(entries):
    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise SystemExit("README.md is missing the GENERATED:VOID markers")
    lines = ["| Entry | What it is | Why it's valuable | Why it's not in the collection | Source |",
             "|---|---|---|---|---|"]
    for entry in sorted(entries, key=lambda e: e["name"]):
        lines.append(entry_row(entry))
    head, _, rest = readme.partition(START)
    _, _, tail = rest.partition(END)
    return f"{head}{START}\n" + "\n".join(lines) + f"\n{END}{tail}"


def main():
    check = "--check" in sys.argv
    errors = []
    data, entries = load(errors)
    if data is not None:
        validate(data, entries, errors)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        print(f"{len(errors)} validation error(s)")
        return 1
    content = render_readme(entries)
    current = README.read_text(encoding="utf-8")
    if current != content:
        if check:
            print("STALE generated files: README.md (Void table)")
            return 1
        README.write_text(content, encoding="utf-8")
    action = "check OK" if check else "regenerated"
    print(f"{action}: {len(entries)} Void entr(ies), files: README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())

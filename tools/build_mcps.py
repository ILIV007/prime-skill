#!/usr/bin/env python3
"""Validate mcps.json and regenerate the README table of recommended MCP servers.

Usage:
  python3 tools/build_mcps.py           # regenerate the README MCP table
  python3 tools/build_mcps.py --check   # exit non-zero if stale/invalid

Stdlib only. Repo root is the parent of this script's directory.
The shelf is deliberately small: a hard cap of 12 entries, metadata and
links only (no vendored files), and every entry must carry an `access`
line stating plainly what the server can run or reach.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "mcps.json"
README = ROOT / "README.md"
START = "<!-- GENERATED:MCP:START -->"
END = "<!-- GENERATED:MCP:END -->"
CAP = 12
REQUIRED = ["name", "title", "description", "why", "source", "license",
            "stars_at_import", "added", "transport", "requires", "access",
            "paid"]
SOURCE_FIELDS = ["repo", "url", "commit"]
TRANSPORTS = {"stdio", "http"}


def esc(text):
    return str(text).replace("|", "\\|")


def load(errors):
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"mcps.json: unreadable: {exc}")
        return None, []
    servers = data.get("servers")
    if not isinstance(servers, list):
        errors.append("mcps.json: 'servers' must be a list")
        return data, []
    return data, servers


def validate(data, servers, errors):
    if data is not None and data.get("count") != len(servers):
        errors.append(f"mcps.json: count {data.get('count')} != {len(servers)} server(s)")
    if len(servers) > CAP:
        errors.append(f"mcps.json: {len(servers)} servers exceeds the hard cap of {CAP}")
    seen = set()
    for srv in servers:
        name = srv.get("name") or "?"
        label = f"mcps.json:{name}"
        for field in REQUIRED:
            if field not in srv:
                errors.append(f"{label}: missing field '{field}'")
        if name in seen:
            errors.append(f"{label}: duplicate server name")
        seen.add(name)
        source = srv.get("source") or {}
        for field in SOURCE_FIELDS:
            if not source.get(field):
                errors.append(f"{label}: source.{field} is empty")
        for field in ("description", "why", "access"):
            if not (srv.get(field) or "").strip():
                errors.append(f"{label}: '{field}' is empty (access is the required "
                              "security disclosure)")
        transport = srv.get("transport")
        if (not isinstance(transport, list) or not transport
                or not set(transport) <= TRANSPORTS):
            errors.append(f"{label}: transport must be a non-empty subset of "
                          f"{sorted(TRANSPORTS)}")
        if not isinstance(srv.get("requires"), list):
            errors.append(f"{label}: requires must be a list")
        paid = srv.get("paid")
        if paid is not False and not (isinstance(paid, str) and paid.strip()):
            errors.append(f"{label}: paid must be false or a short label (e.g. 'Paid API')")
        if not isinstance(srv.get("stars_at_import"), int):
            errors.append(f"{label}: stars_at_import must be an integer")


def server_row(srv):
    source = srv["source"]
    commit = source["commit"][:7]
    requires = "; ".join(srv.get("requires") or []) or "—"
    paid = "" if srv.get("paid") is False else f" · {srv['paid']}"
    stars = f"{srv['stars_at_import']:,}"
    return (f"| [{srv['name']}]({source['url']}) | {esc(srv['description'])} "
            f"| {esc(srv['why'])} | {' + '.join(srv['transport'])}{paid} "
            f"| {esc(requires)} | {esc(srv['access'])} "
            f"| [{source['repo']}]({source['url']}) @ {commit} · {esc(srv['license'])} · ★ {stars} |")


def render_readme(servers):
    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise SystemExit("README.md is missing the GENERATED:MCP markers")
    lines = ["| Server | What it does | Why it's here | Transport | Requires | What it can run / access | Source |",
             "|---|---|---|---|---|---|---|"]
    for srv in sorted(servers, key=lambda s: s["name"]):
        lines.append(server_row(srv))
    head, _, rest = readme.partition(START)
    _, _, tail = rest.partition(END)
    return f"{head}{START}\n" + "\n".join(lines) + f"\n{END}{tail}"


def main():
    check = "--check" in sys.argv
    errors = []
    data, servers = load(errors)
    if data is not None:
        validate(data, servers, errors)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        print(f"{len(errors)} validation error(s)")
        return 1
    content = render_readme(servers)
    current = README.read_text(encoding="utf-8")
    if current != content:
        if check:
            print("STALE generated files: README.md (MCP table)")
            return 1
        README.write_text(content, encoding="utf-8")
    action = "check OK" if check else "regenerated"
    print(f"{action}: {len(servers)} MCP server(s), files: README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())

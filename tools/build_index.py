#!/usr/bin/env python3
"""Validate skill folders and regenerate skills.json + README tables.

Usage:
  python3 tools/build_index.py           # regenerate generated files
  python3 tools/build_index.py --check   # exit non-zero if anything is stale/invalid

Stdlib only. Repo root is the parent of this script's directory.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = ROOT / "categories"
START = "<!-- GENERATED:START -->"
END = "<!-- GENERATED:END -->"
IDX_START = "<!-- GENERATED:INDEX:START -->"
IDX_END = "<!-- GENERATED:INDEX:END -->"
SP_START = "<!-- GENERATED:SPECIALS:START -->"
SP_END = "<!-- GENERATED:SPECIALS:END -->"

# Controlled tag vocabulary: cross-cutting topics only, never a restatement
# of an entry's own category. Every skill carries 1-3 of these in its
# skill.json `tags` field; anything outside this list fails validation.
# ("academic" from the seed list was folded into "research-methods" — a
# single-entry tag is not cross-cutting; "workflow" was added for reusable
# work methods that transfer across categories.)
TAGS = {
    "tokens",           # token / context economy
    "api",              # API design, testing, or access layers
    "social-data",      # social-platform data and signals
    "web-search",       # searching the open web
    "competitor",       # competitor intelligence
    "video",            # video creation, editing, and craft
    "3d",               # 3D scenes, models, and rendering
    "react",            # React / Next.js ecosystem
    "harness",          # agent-harness meta: skills, MCP, subagents
    "automation",       # scripted / pipeline automation
    "content",          # content writing and production
    "security-testing",  # security verification: testing, scanning, review
    "design-systems",   # design tokens, systems, and palettes
    "generative",       # generative art and media
    "research-methods",  # structured research and inquiry methods
    "workflow",         # reusable work methods across domains
}

SCOPES = {
    "development": "Building software: planning, implementation, testing, debugging, and harness workflows.",
    "design": "Visual and interface design: design systems, styling, branding, and generated visuals.",
    "marketing": "Go-to-market: positioning, copy, content, social, and launches.",
    "media": "Media production: video creation and editing, motion, and filmmaking craft.",
    "research": "Finding things out: social-media research, deep research, search, and literature.",
    "security": "Defending systems: secure coding, API testing, threat modeling, and incident readiness.",
    "reverse-engineering": "Understanding compiled and shipped artifacts — and hardening your own against it.",
}

REQUIRED = ["name", "title", "description", "why", "category", "source",
            "license", "stars_at_import", "added", "requires", "entry",
            "adapted", "adaptations", "tags"]
SOURCE_FIELDS = ["repo", "url", "path", "commit"]


def display_category(cat):
    return cat.replace("-", " ").title()


def esc(text):
    return str(text).replace("|", "\\|")


def load_skills(errors):
    skills = []
    if not CATEGORIES.is_dir():
        return skills
    for cat_dir in sorted(p for p in CATEGORIES.iterdir() if p.is_dir()):
        for skill_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
            meta_file = skill_dir / "skill.json"
            if not meta_file.exists():
                errors.append(f"{skill_dir}: missing skill.json")
                continue
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{meta_file}: invalid JSON: {exc}")
                continue
            skills.append((cat_dir.name, skill_dir, meta))
    return skills


def validate(skills, errors):
    seen = {}
    for cat, skill_dir, meta in skills:
        label = f"categories/{cat}/{skill_dir.name}"
        for field in REQUIRED:
            if field not in meta:
                errors.append(f"{label}: skill.json missing field '{field}'")
        if errors and meta.get("name") is None:
            continue
        name = meta.get("name")
        if name in seen:
            errors.append(f"{label}: duplicate skill name '{name}' (also in {seen[name]})")
        seen[name] = label
        if name != skill_dir.name:
            errors.append(f"{label}: name '{name}' does not match folder name")
        if meta.get("category") != cat:
            errors.append(f"{label}: category field '{meta.get('category')}' != folder '{cat}'")
        source = meta.get("source") or {}
        for field in SOURCE_FIELDS:
            if not source.get(field):
                errors.append(f"{label}: source.{field} is empty")
        for field in ("description", "why"):
            value = (meta.get(field) or "").strip()
            if not value or value == "TODO":
                errors.append(f"{label}: '{field}' is empty or TODO")
        if meta.get("entry") not in ("full", "link-only"):
            errors.append(f"{label}: entry must be 'full' or 'link-only'")
        if meta.get("entry") == "full":
            if not (skill_dir / "SKILL.md").exists():
                errors.append(f"{label}: full entry missing SKILL.md")
            licenses = [p for p in skill_dir.iterdir()
                        if p.is_file() and p.name.upper().startswith(("LICENSE", "LICENCE", "COPYING"))]
            if not licenses:
                errors.append(f"{label}: full entry missing LICENSE file (license gate)")
        elif meta.get("entry") == "link-only":
            # Link-only entries are metadata only: no vendored files, so the
            # SKILL.md / LICENSE checks do not apply, but nothing else may
            # live in the folder either.
            extra = sorted(p.name for p in skill_dir.iterdir() if p.name != "skill.json")
            if extra:
                errors.append(f"{label}: link-only entry must contain only skill.json, "
                              f"found: {', '.join(extra)}")
        if meta.get("adapted") and not (meta.get("adaptations") or "").strip():
            errors.append(f"{label}: adapted=true but adaptations note is empty")
        tags = meta.get("tags")
        if not isinstance(tags, list) or not 1 <= len(tags) <= 3:
            errors.append(f"{label}: tags must be a list of 1-3 tags")
        else:
            for tag in tags:
                if tag not in TAGS:
                    errors.append(f"{label}: unknown tag '{tag}' (not in the controlled vocabulary)")
            if len(set(tags)) != len(tags):
                errors.append(f"{label}: duplicate tags")
        if "special" in meta and not isinstance(meta.get("special"), bool):
            errors.append(f"{label}: special must be a boolean")
    return seen


def skill_row(meta, folder):
    name = meta["name"]
    requires = "; ".join(meta.get("requires") or []) or "—"
    source = meta["source"]
    commit = source["commit"][:7]
    if meta.get("entry") == "link-only":
        tree_url = f"{source['url']}/tree/{source['commit']}/{source['path']}"
        name_cell = f"[{name}]({tree_url}) · link-only"
    else:
        name_cell = f"[{name}]({folder})"
    return (f"| {name_cell} | {esc(meta['description'])} | {esc(meta['why'])} "
            f"| {esc(requires)} | [{source['repo']}]({source['url']}) @ {commit} |")


def table_for(metas, folder_of):
    lines = ["| Skill | What it does | Why it's here | Requires | Source |",
             "|---|---|---|---|---|"]
    for meta in metas:
        lines.append(skill_row(meta, folder_of(meta)))
    return lines


def render_outputs(skills):
    metas = [meta for _, _, meta in skills]
    metas.sort(key=lambda m: (m["category"], m["name"]))
    manifest = {"count": len(metas), "skills": metas}
    outputs = {"skills.json": json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"}

    by_cat = {}
    for meta in metas:
        by_cat.setdefault(meta["category"], []).append(meta)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise SystemExit("README.md is missing the GENERATED markers")
    if IDX_START not in readme or IDX_END not in readme:
        raise SystemExit("README.md is missing the GENERATED:INDEX markers")
    if SP_START not in readme or SP_END not in readme:
        raise SystemExit("README.md is missing the GENERATED:SPECIALS markers")

    link_only = sum(1 for m in metas if m.get("entry") == "link-only")
    idx = [f"**{len(metas)} skills · {len(by_cat)} categories · {link_only} link-only**",
           "",
           "| Category | Skills | Scope | Page |",
           "|---|---|---|---|"]
    for cat in sorted(by_cat):
        idx.append(f"| {display_category(cat)} | {len(by_cat[cat])} | "
                   f"{esc(SCOPES.get(cat, ''))} | [Browse →](categories/{cat}/README.md) |")
    ihead, _, irest = readme.partition(IDX_START)
    _, _, itail = irest.partition(IDX_END)
    readme = f"{ihead}{IDX_START}\n" + "\n".join(idx) + f"\n{IDX_END}{itail}"

    specials = [m for m in metas if m.get("special")]
    sp = ["| Skill | Category | Why it's here |", "|---|---|---|"]
    for m in specials:
        sp.append(f"| [{m['name']}](categories/{m['category']}/{m['name']}/) "
                  f"| {display_category(m['category'])} | {esc(m['why'])} |")
    shead, _, srest = readme.partition(SP_START)
    _, _, stail = srest.partition(SP_END)
    readme = f"{shead}{SP_START}\n" + "\n".join(sp) + f"\n{SP_END}{stail}"

    head, _, rest = readme.partition(START)
    _, _, tail = rest.partition(END)
    blocks = []
    for cat in sorted(by_cat):
        blocks.append(f"### [{display_category(cat)}](categories/{cat}/README.md) ({len(by_cat[cat])})")
        blocks.append("")
        blocks.extend(table_for(by_cat[cat], lambda m: f"categories/{m['category']}/{m['name']}/"))
        blocks.append("")
    generated = "\n".join(blocks).rstrip() + "\n"
    outputs["README.md"] = f"{head}{START}\n{generated}{END}{tail}"

    for cat in sorted(by_cat):
        lines = [f"# {display_category(cat)}", ""]
        if cat in SCOPES:
            lines += [f"*{SCOPES[cat]}*", ""]
        lines += ["Back to the [root README](../../README.md).", ""]
        lines.extend(table_for(by_cat[cat], lambda m: f"{m['name']}/"))
        outputs[f"categories/{cat}/README.md"] = "\n".join(lines) + "\n"
    return outputs


def main():
    check = "--check" in sys.argv
    errors = []
    skills = load_skills(errors)
    validate(skills, errors)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        print(f"{len(errors)} validation error(s)")
        return 1
    outputs = render_outputs(skills)
    stale = []
    for rel, content in outputs.items():
        path = ROOT / rel
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != content:
            stale.append(rel)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if check and stale:
        print("STALE generated files: " + ", ".join(sorted(stale)))
        return 1
    action = "check OK" if check else "regenerated"
    print(f"{action}: {len(skills)} skill(s), files: {', '.join(sorted(outputs))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

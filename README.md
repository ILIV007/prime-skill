# Prime Skill

A small, curated collection of genuinely useful agent skills — categorized by
function, browsable by humans and agents alike.

Most skill collections dump everything they can find. This one does the
opposite: every entry here was read, tried, and chosen because it earns its
place. Usefulness first, popularity second. If a skill's value can't be stated
in one line, it doesn't belong here.

## How to use

- **Agents:** read [`skills.json`](skills.json) at the repo root. It lists
  every skill with its category, one-line description, requirements, and exact
  source provenance (repo, path, commit).
- **Humans:** browse `categories/` below, or scan the tables in this README.
- **Install a skill:** copy its folder from `categories/<category>/<skill>/`
  into your agent's skills directory. Each folder is self-contained and keeps
  the standard `SKILL.md` format used by Claude Code, OpenAI Codex, Cursor,
  Muse, and other harnesses.

## Entry rules

- Real, standalone skills only (a `SKILL.md` a fresh agent can use) — no
  apps, models, or platforms that merely bundle internal skills.
- Maintained upstream, with a permissive license (MIT, Apache-2.0, BSD) for
  full copies; anything else is a link-only entry.
- Paid or key-gated dependencies are allowed only when labelled in the
  skill's metadata (`requires`).
- Every full entry carries its upstream `LICENSE` file and records the exact
  source commit it was imported from.
- Adaptations, when needed, are minimal and harness-neutral (no
  machine-specific paths, no private infrastructure), and are declared in
  the skill's `skill.json` (`adapted` / `adaptations`).

## Categories

<!-- GENERATED:START -->

<!-- GENERATED:END -->

## Adding a skill

Candidates are vetted against the entry rules above, then imported with
`tools/add_skill.py` (see `tools/`), which records provenance, applies the
license gate, and leaves `why` / `description` for the maintainer to fill.
`tools/build_index.py` regenerates `skills.json` and the tables above, so the
index can never drift from the content. CI runs it in `--check` mode on every
push.

## License

Repo-authored content (tools, docs, metadata, this README) is MIT — see
[`LICENSE`](LICENSE). Each skill keeps its own upstream license; the
`LICENSE` file inside each skill folder is the authoritative one for that
skill.

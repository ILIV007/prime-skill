# Prime Skill — Implementation Plan

Design: `2026-11-04-prime-skill-design.md` (approved by the owner 2026-11-04).
All steps ship through the owner's GitHub PAT connector (`custom.github-pat`),
the route used for his other repos. Working tree: `~/workspace/projects/prime-skill/`
(already holds `docs/plans/`).

## 1. Create the repository

- Create `ILIV007/prime-skill` via `POST /user/repos` (public, MIT, no
  auto-init), the same way Proxiv3 was created.
- Make a helper variant `bin/gh_api_primeskill.py` (copy of `gh_api.py`,
  `REPO = "prime-skill"`), verify with `whoami` + `repo`.
- Done when: the repo exists, is public, and the helper reads it.

## 2. Scaffold

- Files: `README.md` (hand-written intro, curation rules, entry rules,
  install-by-copy instructions; generated tables live between
  `<!-- GENERATED:START -->` / `<!-- GENERATED:END -->` markers),
  `LICENSE` (MIT, repo-authored content), `.gitignore` (OS/editor noise,
  `__pycache__`), `categories/` (populated in step 5), `tools/`,
  `docs/plans/` (the design + this plan, committed with the scaffold).
- Done when: the scaffold commit is on `main` and renders on GitHub.

## 3. tools/build_index.py (stdlib only)

- Scans `categories/<category>/<skill>/` for `skill.json` + `SKILL.md`.
- Validates: required fields present; `name` globally unique; folder category
  matches `category`; `full` entries have a `LICENSE` file in the skill
  folder; `why` and `description` are non-empty and not TODO.
- Generates: root `skills.json` (all metadata, sorted by category then name),
  the README tables between the markers, and one `README.md` per category.
- `--check` regenerates in memory and exits non-zero on any diff.
- Done when: it runs clean on the scaffold (0 skills) and fails correctly on
  a deliberately broken fixture.

## 4. tools/add_skill.py (stdlib only)

- Inputs: source repo URL, `--path` (a skill folder or a directory of skill
  folders), `--category`, optional `--only name1,name2` for subsets.
- Sparse blob-filtered clone at HEAD; resolves and records the exact commit.
- Copies runtime files only: excludes test/dev folders (`tests`, `__tests__`,
  `test`, `.github`) and anything the design's inclusion rule drops; keeps
  runtime data (CSV/JSON/fonts).
- Ensures a `LICENSE` in the skill folder: the skill's own if present, else
  the source repo's root LICENSE, else stops and reports (license gate).
- Captures `stars_at_import` from the GitHub API (null on failure, never
  blocks).
- Writes `skill.json` with `why` / `description` as TODO for the maintainer.
- Done when: a dry import of one small skill (brainstorming) produces a
  folder that passes `build_index.py` once the TODOs are filled.

## 5. Seed import (42 skills)

Run `add_skill.py` per source, then fill every `why` / `description`
(Nova-authored, one line each, concise):

- **development (7):** DietrichGebert/ponytail → ponytail, ponytail-review,
  ponytail-audit, ponytail-debt, ponytail-gain, ponytail-help;
  davila7/claude-code-templates → brainstorming
  (`cli-tool/components/skills/development/brainstorming`, references kept).
- **design (7):** nextlevelbuilder/ui-ux-pro-max-skill → ui-ux-pro-max,
  design, design-system, ui-styling, brand, banner-design, slides.
  Adaptation: rewrite `${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max`
  script paths in the main SKILL.md to paths relative to the skill folder;
  mark `adapted` with that one-liner.
- **marketing (14):** coreyhaines31/marketingskills `--only` the selected 14:
  product-marketing, copywriting, copy-editing, content-strategy, social,
  video, marketing-psychology, marketing-ideas, marketing-council,
  community-marketing, competitor-profiling, customer-research, launch,
  offers.
- **research (13):** ScrapeCreators/social-media-research-skills → all 13;
  `requires`: ["ScrapeCreators API key (paid, credit-based)"].
- **reverse-engineering (1):** morluto/rea →
  `.agents/skills/reverse-engineer-anything` only (not the internal
  maintainer skills); `requires`: ["REA toolchain (optional, for full
  function)"].
- Done when: 42 folders, every `skill.json` complete, no TODO left.

## 6. Generate and verify locally

- Run `build_index.py`; inspect `skills.json` (42 entries, 5 categories) and
  the rendered README tables.
- Spot-check three skills against their sources (file lists + one diff each).
- Done when: `--check` passes and the spot-checks match.

## 7. CI

- `.github/workflows/validate.yml`: on push and PR, run
  `python3 tools/build_index.py --check` and validate `skills.json` parses.
- Done when: the workflow is committed with step 8 and its first run is green
  (read back through the Actions API).

## 8. Ship

- Commit in batches through `gh_api_primeskill.py commit-files`:
  scaffold + tools, then one commit per category, then generated files +
  CI if not already in.
- Done when: GitHub shows all batches on `main`, the tree holds 42 skill
  folders, and the README on the repo page lists every category.

## 9. Handover

- Verify the success criteria from the design doc (agent can enumerate from
  `skills.json`; human finds a skill from the README fast; CI green).
- Report to the owner with the repo link and the counts; update memory.

## Risks and notes

- HEAD drift between planning and import is fine by design: whatever commit
  is resolved at import is the one recorded.
- The design set is a few MB (fonts, data). Acceptable for git; no LFS.
- GitHub API blob uploads for the seed are batched per category to stay well
  inside rate limits; after any uncertain commit, read the tree back before
  retrying.

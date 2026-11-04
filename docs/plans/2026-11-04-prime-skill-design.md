# Prime Skill — Design

## Intent and why

Agent skills are scattered across hundreds of repos with no quality bar: giant
mirrors dump everything (one popular collection ships 268 skills, most of them
copies of copies), and finding one good skill means redoing the same vetting
work every time. Prime Skill is the opposite: a small, curated, public
collection where every entry was read, tested, and chosen because it is
genuinely useful. The owner (Iliya, GitHub `ILIV007`) and his agents are the
first users; the public is the second. Over time, candidate repos are forwarded
to the owner, vetted against the entry rules, and only the passing skills are
added — selected by usefulness first, popularity second.

This collection expresses the owner's taste and picks. It is not an official
distribution channel for the upstream projects, so entries may be adapted —
but every skill must ship in its best harness-neutral form. The target
harnesses are the main ones (Claude Code, OpenAI Codex, Cursor, and Muse);
their common denominator, a `SKILL.md` with YAML frontmatter, is the format
every entry keeps.

## Goals

- One repo (`ILIV007/prime-skill`, public) holding the owner's vetted skill
  set, categorized by function, browsable by humans and agents alike.
- Every skill self-contained in the repo (full files) whenever its license
  allows redistribution, with exact source provenance (repo, path, pinned
  commit) recorded per skill.
- A machine-readable root manifest (`skills.json`) that agents can read to
  discover everything, generated from per-skill metadata so it can never drift
  from the content.
- Human README category tables generated from the same metadata.
- Adding a skill is one scripted, repeatable operation, not manual editing of
  five files.
- Seed content: the 42 skills already vetted and installed by the owner on
  2026-11-04 (see "Seed set").

## Non-goals

- Not a package manager, runtime, or installer platform; installation is
  "copy a folder", documented in the README.
- Not a mirror of any upstream collection, and not a host for apps, models, or
  observability platforms that merely bundle internal skills.
- No automatic syncing with upstream. Upstream updates enter only as
  deliberate, reviewed commit bumps.

## Anti-goals

- Growing into a hundreds-of-skills dump. If an entry's "why" cannot be stated
  in one line, it does not belong.
- A README that disagrees with the folders. Generated sections exist precisely
  to make this impossible.
- Entries whose content nobody on this project has read.

## Constraints

- English only for all repo content (README, metadata, docs) — owner's call.
- License gate: full copies only for permissive licenses (MIT, Apache-2.0,
  BSD). Anything else becomes a "link-only" entry (metadata + source link, no
  files).
- Paid or key-gated dependencies are allowed only when labelled in metadata
  (e.g. the ScrapeCreators set needs an API key).
- Tools are Python 3 standard library only — no pip installs to maintain the
  repo. (Marked: builder's call, approved implicitly by the owner's
  low-maintenance requirement; flag if contested.)
- Repo creation and pushes go through the owner's GitHub PAT connector, the
  same route used for his other repos. Nothing is created or pushed before the
  owner approves this design and, later, the implementation plan.

## Approaches

Considered:

- **A — Manifest-driven monorepo (chosen).** Per-skill folders under
  categories, each with a `skill.json`; a build script generates `skills.json`
  and the README/category tables; an add script performs imports. Slight
  upfront tooling cost, then the structure maintains itself.
- **B — Catalog only.** Links and descriptions, no vendored files. Zero
  license risk but not self-contained, links rot, and every install repeats
  the manual extraction work this project exists to eliminate.
- **C — Git submodules per source.** Clean provenance, but cannot cherry-pick
  subsets of a source repo (we take 14 of 54 from the marketing set) and is
  hostile to casual browsing.

The owner picked **A** on 2026-11-04, with B's provenance discipline kept
(pinned source commits per skill, link-only fallback when a license forbids
redistribution).

## Decisions made by the owner

- Name: **Prime Skill**; repo slug `prime-skill` under `ILIV007`; public.
- Audience: both — optimized for the owner's own use first, public second.
- Language: English only.
- Approach: A (manifest-driven monorepo).
- Curation basis: usefulness first, popularity as a signal; candidates arrive
  over time from the owner's forwards as well as the seed set.
- Seed versions: each source's **latest HEAD** at import time (not the older
  commits the owner originally installed). The resolved commit is still
  recorded per skill, so provenance stays exact.
- The seed entries' `why` and one-line `description` values are written by
  Nova, concise and plain, with no separate owner review gate. Future
  additions are vetted jointly with the owner when he forwards candidates.
- Content rule: only genuinely useful skills; clean, function-based
  categorization; navigable by agents and humans.

## Builder's calls (Nova's proposals, not the owner's words)

- **Taxonomy (5 categories to start):**
  - `development` — Ponytail set (6) and brainstorming (1)
  - `design` — UI/UX Pro Max set (7)
  - `marketing` — the selected marketing skills (14)
  - `research` — the ScrapeCreators social-research set (13)
  - `reverse-engineering` — the REA skill (1)
- **Layout:**
  - `categories/<category>/<skill>/` — upstream skill files (including their
    own frontmatter, so the folder drops into any agent's skills dir
    unchanged) plus `skill.json`.
  - **Inclusion rule** (builder's call, following the rule used when these
    skills were installed locally): runtime files only. Dev test suites and
    other dev-only folders are excluded at import; data a skill loads at
    runtime (CSVs, JSON data, fonts it renders with) is kept, even when
    large.
  - **Licenses** (builder's call, required by the license gate): every `full`
    skill folder carries its upstream LICENSE file, fetched at import time.
    `build_index.py` fails a `full` entry that lacks one.
  - **Names** (builder's call): `name` is globally unique across the whole
    repo, not just within a category, so agents can resolve a skill from
    `skills.json` by name alone. `build_index.py` rejects collisions; on a
    future collision the maintainer qualifies the folder name and the
    original upstream name stays visible in `source.path`.
  - `skill.json` fields: `name`, `title`, `description` (one line), `why`
    (one line), `category`, `source` {`repo`, `url`, `path`, `commit`},
    `license`, `stars_at_import` (number or null), `added` (YYYY-MM-DD),
    `requires` (list, empty when none), `entry` (`full` or `link-only`),
    `adapted` (boolean), `adaptations` (one line, empty when `adapted` is
    false).
  - **Adaptation policy** (builder's call, under the owner's framing above):
    the base is canonical upstream at HEAD. An adaptation is allowed only to
    make a skill harness-neutral (for example, replacing a harness-specific
    path variable with a path relative to the skill folder) or to remove
    references to infrastructure this repo does not ship. Environment-specific
    content (one machine's absolute paths, the owner's private connectors) is
    never vendored. Every adaptation is declared in `adapted` /
    `adaptations`, so `source.commit` never silently misdescribes a folder.
  - Root: `README.md` (hand-written intro and curation rules; generated
    tables between `<!-- GENERATED -->` markers), `skills.json` (generated),
    `LICENSE` (MIT, covering repo-authored content: tools, docs, metadata),
    `docs/plans/` for design and plan documents.
  - `tools/build_index.py` — validates every skill folder and regenerates
    `skills.json`, README tables, and one `README.md` per category.
    `--check` mode exits non-zero when generated files are stale.
  - `tools/add_skill.py` — takes a source repo URL plus a skill path (or a
    whole skills directory), sparse-fetches it, copies the selected skill
    folders into a chosen category, pins the current commit in `skill.json`,
    and leaves `why` as a TODO the maintainer must fill before commit.
  - `.github/workflows/validate.yml` — runs `build_index.py --check` and a
    JSON validity check on every push and PR.
- **Seed set (42), imported from original sources at their HEAD on import
  day (resolved commit recorded per skill), not from local copies:** DietrichGebert/ponytail (6), davila7/claude-code-templates
  brainstorming (1), nextlevelbuilder/ui-ux-pro-max-skill (7),
  coreyhaines31/marketingskills — the same 14 selected on 2026-11-04,
  ScrapeCreators/social-media-research-skills (13, `requires` labels the API
  key), morluto/rea — the user-facing skill only (1).
- **Popularity data:** `stars_at_import` is captured once at import time from
  the GitHub API; it is a snapshot, not a live counter.

## Left to the builder

- Exact README prose, badges, and table formatting.
- CLI flag design of `add_skill.py` beyond the contract above.
- Whether category READMEs are separate files or README sections, as long as
  they are generated.
- Order of implementation steps (goes in the implementation plan).

## Success criteria

- A fresh agent given only the repo URL can enumerate all skills, their
  categories, and their requirements from `skills.json` alone.
- A human can find any skill from the README in under a minute.
- Adding a new skill touches exactly: the new folder, its `skill.json`, and
  regenerated files — one command plus one commit.
- CI is green and `build_index.py --check` passes on the seed import.

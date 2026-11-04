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
### Design (8)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [algorithmic-art](categories/design/algorithmic-art/) | Creates generative art with p5.js: seeded algorithms, flow fields, and particle systems delivered as interactive HTML pieces. | The distinctive one in Anthropic's set: real generative-art capability, not another text workflow; useful for visuals and covers. | — | [anthropics/skills](https://github.com/anthropics/skills) @ ca45fc4 |
| [banner-design](categories/design/banner-design/) | Designs banners for social, ads, website heroes, and print, with multiple art-direction options. | Banners and covers are a recurring need for channels and launches. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [brand](categories/design/brand/) | Brand voice, visual identity, messaging frameworks, and consistency checks for branded content. | Keeps channel and product visuals and tone recognizably on-brand. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [design](categories/design/design/) | All-in-one design skill: brand identity, tokens, logos, icons, banners, presentations, and social visuals. | Covers the long tail of one-off design asks in a single skill. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [design-system](categories/design/design-system/) | Design-token architecture (primitive to semantic to component), component specs, and brand-compliant slides. | Keeps multi-screen products visually consistent as they grow. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [slides](categories/design/slides/) | Creates strategic HTML presentations with charts, design tokens, and responsive layouts. | Turns briefs and reports into presentable decks without design software. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [ui-styling](categories/design/ui-styling/) | Builds accessible UIs with shadcn/ui, Radix, and Tailwind, plus canvas-based visual designs. | The practical implementation partner to the design-system rules. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [ui-ux-pro-max](categories/design/ui-ux-pro-max/) | Design intelligence for web, mobile, and desktop UIs, with searchable local data on styles, palettes, font pairings, UX guidelines, and stacks. | Gives interface work a real design database instead of guesswork; the flagship of the design set. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |

### Development (18)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [brainstorming](categories/development/brainstorming/) | Clarifies what the user actually wants, one question at a time, compares 2-3 approaches, and gets a design approved before anything is built. | Stops build-first-guess-later work on new features and projects; it is the process that designed this very repo. | — | [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) @ cc3f535 |
| [mcp-builder](categories/development/mcp-builder/) | Anthropic's playbook for designing and building high-quality MCP servers, with reference guides and an evaluation harness. | The owner builds connectors and MCP-backed tools; this is the reference guide from the source. | — | [anthropics/skills](https://github.com/anthropics/skills) @ ca45fc4 |
| [ponytail](categories/development/ponytail/) | Lazy senior-dev mode: the smallest change that fully solves the task, explained in one read. | Cuts over-engineering, tokens, and cost on everyday coding without dropping safety or tests. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [ponytail-audit](categories/development/ponytail-audit/) | One-shot whole-repo audit for bugs, security holes, slow paths, untested risky code, and deletable bloat. | A fast health check for inherited or fast-grown codebases, ranked by impact. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [ponytail-debt](categories/development/ponytail-debt/) | Lists every deliberate shortcut: marker in the code as a debt ledger. | Keeps intentional shortcuts visible so they get repaid instead of forgotten. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [ponytail-gain](categories/development/ponytail-gain/) | Shows Ponytail's measured savings in code, cost, and speed from its benchmark. | Answers 'is the lazy mode actually paying off' with numbers, not vibes. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [ponytail-help](categories/development/ponytail-help/) | Quick reference card for Ponytail levels, skills, and commands. | One-shot cheat sheet so the whole set stays usable without re-reading docs. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [ponytail-review](categories/development/ponytail-review/) | Quality review of a change: correctness, safety, load behavior, tests, and whether every line earns its place. | Catches risky or bloated diffs before they ship, explained in plain language. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [skill-creator](categories/development/skill-creator/) | Anthropic's guide and tooling for creating, evaluating, and iterating on agent skills, with eval and description-tuning scripts. | This repo curates skills for a living; the official skill-authoring workflow belongs in it. | — | [anthropics/skills](https://github.com/anthropics/skills) @ ca45fc4 |
| [subagent-driven-development](categories/development/subagent-driven-development/) | Executes an implementation plan with fresh subagents per task, with spec and quality review gates between tasks. | The execution engine for writing-plans in multi-agent harnesses; how the owner's bigger builds actually get run. | a harness with subagents | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [systematic-debugging](categories/development/systematic-debugging/) | A root-cause-first debugging method: reproduce, isolate, and prove the cause before changing any code. | Ends guess-and-patch debugging loops; pairs with this project's verify-against-real-behavior rule. | — | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [test-driven-development](categories/development/test-driven-development/) | Guides red-green-refactor TDD: write the failing test first, make it pass with the smallest change, then refactor. | Proven discipline from the most-starred source in this collection; keeps agent-written code verified by construction. | — | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [using-git-worktrees](categories/development/using-git-worktrees/) | Sets up isolated git worktrees so parallel features, reviews, and experiments never collide in one working tree. | The standard companion to plan-driven work; makes parallel agent work on the owner's repos safe. | git | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [vercel-react-best-practices](categories/development/vercel-react-best-practices/) | Vercel Engineering's React and Next.js performance rules: 70 prioritized guidelines across data fetching, bundles, rendering, and re-renders. | The canonical React performance rulebook; applies to the owner's Next.js work (Eggino) and any React build. | — | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) @ 1a2c79d |
| [verification-before-completion](categories/development/verification-before-completion/) | Requires fresh evidence (test runs, command output, live checks) before any claim that work is done or fixed. | Encodes the rule that shipped means verified; cheap insurance against false 'done' reports. | — | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [webapp-testing](categories/development/webapp-testing/) | Tests local web apps with Playwright: manages the dev server, drives a real browser, and inspects console, DOM, and screenshots. | Gives agents a real-browser check for the owner's web apps and artifacts; catches what unit tests cannot see. | Python + Playwright; a local dev server | [anthropics/skills](https://github.com/anthropics/skills) @ ca45fc4 |
| [workers-best-practices](categories/development/workers-best-practices/) | Cloudflare's official best practices for Workers: configuration, runtime patterns, and platform API guidance. | Nearly all of the owner's production code runs on Workers (IVAI, TradeAgent, Proxiv3); this is the vendor's own guidance. | — | [cloudflare/skills](https://github.com/cloudflare/skills) @ 1f2cd0a |
| [writing-plans](categories/development/writing-plans/) | Turns an approved spec or design into a detailed, step-by-step implementation plan that can be executed without guessing. | The missing half of the brainstorming workflow already in this repo; makes multi-step builds land first-try instead of drifting. | — | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |

### Marketing (14)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [community-marketing](categories/marketing/community-marketing/) | Builds and leverages online communities - Discord, Slack, forums - for product growth and loyalty. | Community-led growth fits bot and channel products especially well. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [competitor-profiling](categories/marketing/competitor-profiling/) | Researches competitors from their URLs and produces structured profile dossiers. | Know exactly what rivals offer and how they position before you ship. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [content-strategy](categories/marketing/content-strategy/) | Plans what content to create: pillars, topic clusters, editorial calendars, and roadmaps. | Deciding what to publish beats publishing at random, for blogs and channels alike. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [copy-editing](categories/marketing/copy-editing/) | Edits and refreshes existing marketing copy: tightening, de-slopping, and sharpening without a rewrite. | Most real work is improving copy that already exists, not starting from zero. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [copywriting](categories/marketing/copywriting/) | Writes and improves marketing copy for pages: headlines, CTAs, value propositions, and hero sections. | Sharp copy is the cheapest conversion lever for landing pages and product posts. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [customer-research](categories/marketing/customer-research/) | Runs and synthesizes customer research: interviews, surveys, review mining, voice-of-customer, and JTBD. | Decisions grounded in real customer language outperform opinion. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [launch](categories/marketing/launch/) | Plans product launches and feature announcements: checklists, go-to-market, waitlists, and release strategy. | Launches are one-shot events; a checklist prevents unforced errors. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [marketing-council](categories/marketing/marketing-council/) | Simulates a board of legendary marketers (Godin, Ogilvy, Hormozi, and more) debating your marketing question. | Several expert lenses on one decision beat a single generic take. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [marketing-ideas](categories/marketing/marketing-ideas/) | A bank of proven marketing and growth tactics for software products, matched to the situation. | The fastest way out of 'we need growth but don't know what to try'. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [marketing-psychology](categories/marketing/marketing-psychology/) | Applies behavioral science and mental models - anchoring, social proof, scarcity, framing - to marketing. | Explains why people buy, so offers and copy stop being guesswork. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [offers](categories/marketing/offers/) | Designs the offer itself: value framing, bonus stacks, guarantees, scarcity, and payment structure. | A better offer beats better ads; core skill for anything sold or promoted. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [product-marketing](categories/marketing/product-marketing/) | Creates the product-marketing context doc - positioning, audience, ICP, brand voice - that the other marketing skills build on. | The foundation of the marketing set: write the context once, reuse it in every campaign. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [social](categories/marketing/social/) | Creates, schedules, and optimizes social media content, and runs social listening across the major platforms. | Directly useful for running and growing social and channel presences. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [video](categories/marketing/video/) | Guides AI and programmatic video production: avatars, demos, explainers, and generation pipelines. | Video is the highest-reach format; this maps the current tool landscape into workflows. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |

### Research (13)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [ad-library-teardown](categories/research/ad-library-teardown/) | Analyzes active ads from Meta, Google, and LinkedIn libraries: hooks, offers, CTAs, and claims. | Competitors publish their best-tested messaging in ad libraries for free. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [audience-research](categories/research/audience-research/) | Evaluates a creator or brand audience from public signals: demographics, geography, language, and fit. | Prevents sponsorship and partnership picks based on follower counts alone. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [comment-mining](categories/research/comment-mining/) | Mines comments and replies for objections, questions, buying intent, and voice-of-customer language. | Comments are unfiltered market research, already written by the audience. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [competitor-social-research](categories/research/competitor-social-research/) | Researches competitors' social strategy and turns public data into a practical strategy brief. | Shows what content is winning in your niche and where the gaps are. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [content-repurposing](categories/research/content-repurposing/) | Turns public videos, transcripts, and posts into threads, scripts, newsletters, and content calendars. | One good source becomes a week of channel-ready material. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [creator-profile-teardown](categories/research/creator-profile-teardown/) | Tears down a creator or brand profile: positioning, pillars, hooks, formats, and outlier posts. | A repeatable way to learn from accounts that already win. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [influencer-prospecting](categories/research/influencer-prospecting/) | Finds and scores creators in a niche for outreach, partnerships, sponsorships, and UGC. | Builds prospect lists from evidence instead of manual scrolling. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [outlier-post-finder](categories/research/outlier-post-finder/) | Finds posts that massively overperformed a creator's baseline and explains why they worked. | Modeling proven outliers is the shortest path to better content. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [product-demand-research](categories/research/product-demand-research/) | Validates product ideas by mining pain points, demand signals, and objections from social posts and Reddit. | Evidence-backed demand checks before building or launching anything. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [scrapecreators-api](categories/research/scrapecreators-api/) | Reference and access layer for the ScrapeCreators REST API: public data from 27+ social platforms. | The base skill the whole research set calls; it documents every endpoint the others use. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [social-listening-brief](categories/research/social-listening-brief/) | Produces a cited social-listening brief on what people say about a brand, topic, or niche. | A fast reputation and sentiment snapshot before campaigns or launches. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [transcript-intelligence](categories/research/transcript-intelligence/) | Summarizes and mines video transcripts for hooks, claims, quotes, and reusable content atoms. | Unlocks the content inside long videos without watching them all. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [trend-discovery](categories/research/trend-discovery/) | Finds trending topics, hashtags, sounds, and formats in a niche from public trend endpoints. | Trend timing is free reach for channels; this turns trends into content angles. | ScrapeCreators API key (paid, credit-based) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |

### Reverse Engineering (1)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [reverse-engineer-anything](categories/reverse-engineering/reverse-engineer-anything/) | Reverse engineers binaries, Electron/JS apps, .NET, firmware, and browser targets with REA, backed by runtime evidence. | The owner's reverse-engineering workhorse: explains features, compares versions, and guides reconstructions from real artifacts. | REA toolchain (optional, for full function) | [morluto/rea](https://github.com/morluto/rea) @ d7df9df |
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

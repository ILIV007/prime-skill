# Prime Skill

[![Skills](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FILIV007%2Fprime-skill%2Fmain%2Fskills.json&query=%24.count&label=skills)](skills.json)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Validate](https://github.com/ILIV007/prime-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/ILIV007/prime-skill/actions/workflows/validate.yml)

A small, curated collection of genuinely useful agent skills — categorized by
function, browsable by humans and agents alike.

🌐 **Browse the collection as a site: [iliv007.github.io/prime-skill](https://iliv007.github.io/prime-skill/)** — search, filter by category and tag, no cloning needed.

Most skill collections dump everything they can find. This one does the
opposite: every entry here was read, tried, and chosen because it earns its
place. Usefulness first, popularity second. If a skill's value can't be stated
in one line, it doesn't belong here.

## How to use

- **Agents:** read [`skills.json`](skills.json) at the repo root. It lists
  every skill with its category, one-line description, requirements, and exact
  source provenance (repo, path, commit).
- **Humans:** browse the [site](https://iliv007.github.io/prime-skill/), the
  `categories/` folders below, or scan the tables in this README.
- **Install a skill:** copy its folder from `categories/<category>/<skill>/`
  into your agent's skills directory. Each folder is self-contained and keeps
  the standard `SKILL.md` format used by Claude Code, OpenAI Codex, Cursor,
  Muse, and other harnesses. Entries marked **link-only** in the tables
  carry metadata only (their license does not allow redistribution); follow
  their source link to fetch the files.

## ⭐ Specials

The signature picks — the entries with a capability or a level of craft
nothing else here (or anywhere) quite matches.

<!-- GENERATED:SPECIALS:START -->
| Skill | Category | Why it's here |
|---|---|---|
| [algorithmic-art](categories/design/algorithmic-art/) | Design | The distinctive one in Anthropic's set: real generative-art capability, not another text workflow; useful for visuals and covers. |
| [anatomy](categories/design/anatomy/) | Design | Precise technical illustration as explanation — a capability neither the generative-art skill nor the UI set covers. |
| [color-expert](categories/design/color-expert/) | Design | The palette data elsewhere is lookup-only; this is the craft of making and judging color — perceptually uniform ramps, naming, and verified contrast. |
| [ui-ux-pro-max](categories/design/ui-ux-pro-max/) | Design | Gives interface work a real design database instead of guesswork; the flagship of the design set. |
| [caveman](categories/development/caveman/) | Development | Cuts output-token waste on every reply without losing substance; the communication-side counterpart to ponytail's lean code. |
| [ponytail](categories/development/ponytail/) | Development | Cuts over-engineering, tokens, and cost on everyday coding without dropping safety or tests. |
| [blind-llm-agents](categories/reverse-engineering/blind-llm-agents/) | Reverse Engineering | The defensive mirror of REA: REA takes artifacts apart; this protects your own releases from being taken apart. |
| [reverse-engineer-anything](categories/reverse-engineering/reverse-engineer-anything/) | Reverse Engineering | The owner's reverse-engineering workhorse: explains features, compares versions, and guides reconstructions from real artifacts. |
<!-- GENERATED:SPECIALS:END -->

## At a glance

<!-- GENERATED:INDEX:START -->
**80 skills · 7 categories · 5 link-only**

| Category | Skills | Scope | Page |
|---|---|---|---|
| Design | 11 | Visual and interface design: design systems, styling, branding, and generated visuals. | [Browse →](categories/design/README.md) |
| Development | 24 | Building software: planning, implementation, testing, debugging, and harness workflows. | [Browse →](categories/development/README.md) |
| Marketing | 12 | Go-to-market: positioning, copy, content, social, and launches. | [Browse →](categories/marketing/README.md) |
| Media | 9 | Media production: video creation and editing, motion, and filmmaking craft. | [Browse →](categories/media/README.md) |
| Research | 16 | Finding things out: social-media research, deep research, search, and literature. | [Browse →](categories/research/README.md) |
| Reverse Engineering | 2 | Understanding compiled and shipped artifacts — and hardening your own against it. | [Browse →](categories/reverse-engineering/README.md) |
| Security | 6 | Defending systems: secure coding, API testing, threat modeling, and incident readiness. | [Browse →](categories/security/README.md) |
<!-- GENERATED:INDEX:END -->

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
- **Specials** are the collection's signature picks — a unique capability
  or exceptional craft, at most one per capability cluster, flagged
  `special` in the manifest and showcased in the ⭐ Specials section above.
- Every skill carries 1–3 `tags` from a controlled vocabulary —
  cross-cutting topics only, never a restatement of its category:
  `3d`, `api`, `automation`, `competitor`, `content`, `design-systems`,
  `generative`, `harness`, `react`, `research-methods`, `security-testing`,
  `social-data`, `tokens`, `video`, `web-search`, `workflow`. Tags live in
  `skills.json` and on the site, not in the tables below; an unknown tag
  fails validation.

### Category growth

- Development splits at ~32 entries, or when a coherent subgroup reaches
  8+ entries (the harness-meta cluster — skill/MCP/subagent tooling —
  splits first).
- Research splits when general (non-social) research reaches ~6 entries.
- A new category needs a one-line scope (recorded in the generator) and
  at least 2 entries.

## Categories

<!-- GENERATED:START -->
### [Design](categories/design/README.md) (11)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [algorithmic-art](categories/design/algorithmic-art/) | Creates generative art with p5.js: seeded algorithms, flow fields, and particle systems delivered as interactive HTML pieces. | The distinctive one in Anthropic's set: real generative-art capability, not another text workflow; useful for visuals and covers. | — | [anthropics/skills](https://github.com/anthropics/skills) @ ca45fc4 |
| [anatomy](categories/design/anatomy/) | Builds crafted, interactive isometric SVG figures that explain a technical idea as a physical machine, with worked examples and a geometry-audit kit. | Precise technical illustration as explanation — a capability neither the generative-art skill nor the UI set covers. | Node 20.10+; Chrome/Chromium | [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) @ 1482e84 |
| [banner-design](categories/design/banner-design/) | Designs banners for social, ads, website heroes, and print, with multiple art-direction options. | Banners and covers are a recurring need for channels and launches. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [blender-web-3d](categories/design/blender-web-3d/) | Drives Blender headless or via MCP to build, modify, render, and optimize 3D models, then publishes them as fast Three.js/Next.js web experiences with modern color, shader, and compression pipelines. | The only Blender-to-web pipeline in the collection: real 3D asset craft with optimization and deploy covered, plus a runnable demo to start from. | Blender 4.x/5.x; Node.js 20+ | [czlonkowski/blender-web-3d-skill](https://github.com/czlonkowski/blender-web-3d-skill) @ 858762f |
| [brand](categories/design/brand/) | Brand voice, visual identity, messaging frameworks, and consistency checks for branded content. | Keeps channel and product visuals and tone recognizably on-brand. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [color-contrast](categories/design/color-contrast/) | Measures color contrast with WCAG 2.x ratios and APCA, audits a codebase or stylesheet for failing pairs (including dark mode), and repairs failures with the smallest possible color change. | The executable half of color accessibility: it audits real stylesheets, computes real ratios, and fixes failures — measurement work no resident skill does. | Python 3 | [hendurhance/color-contrast](https://github.com/hendurhance/color-contrast) @ f301f1c |
| [color-expert](categories/design/color-expert/) | Deep color expertise: color spaces (OKLCH, CIELAB), palette and ramp generation, harmony systems, color naming, pigment and print-vs-screen behavior, and contrast verification. | The palette data elsewhere is lookup-only; this is the craft of making and judging color — perceptually uniform ramps, naming, and verified contrast. | — | [meodai/skill.color-expert](https://github.com/meodai/skill.color-expert) @ 5bf7c77 |
| [design-system](categories/design/design-system/) | Design-token architecture (primitive to semantic to component), component specs, and brand-compliant slides. | Keeps multi-screen products visually consistent as they grow. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [slides](categories/design/slides/) | Creates strategic HTML presentations with charts, design tokens, and responsive layouts. | Turns briefs and reports into presentable decks without design software. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [ui-styling](categories/design/ui-styling/) | Builds accessible UIs with shadcn/ui, Radix, and Tailwind, plus canvas-based visual designs. | The practical implementation partner to the design-system rules. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |
| [ui-ux-pro-max](categories/design/ui-ux-pro-max/) | Design intelligence for web, mobile, and desktop UIs, with searchable local data on styles, palettes, font pairings, UX guidelines, and stacks. | Gives interface work a real design database instead of guesswork; the flagship of the design set. | — | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ dd9a1b4 |

### [Development](categories/development/README.md) (24)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [brainstorming](categories/development/brainstorming/) | Clarifies what the user actually wants, one question at a time, compares 2-3 approaches, and gets a design approved before anything is built. | Stops build-first-guess-later work on new features and projects; it is the process that designed this very repo. | — | [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) @ cc3f535 |
| [caveman](categories/development/caveman/) | Terse caveman voice for agent replies: answer first, fluff gone, every technical fact kept, and it stays on until told to stop. | Cuts output-token waste on every reply without losing substance; the communication-side counterpart to ponytail's lean code. | — | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) @ 2e068f7 |
| [caveman-compress](categories/development/caveman-compress/) | Compresses memory files such as CLAUDE.md or todo lists into caveman format to save input tokens, keeping a readable backup outside the tree. | Long-lived context files are re-read every session; compressing them is a permanent input-token saving rather than a one-off. | Python 3; Model provider API | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) @ 2e068f7 |
| [domain-modeling](categories/development/domain-modeling/) | Builds and sharpens a project's domain model: maintains a living glossary of codebase terminology and records architecture decisions as ADRs. | Shared vocabulary keeps agents and humans from talking past each other; this makes terminology a maintained artifact, not folklore. | — | [mattpocock/skills](https://github.com/mattpocock/skills) @ 4ae2317 |
| [find-skills](categories/development/find-skills/) | Finds and installs agent skills from the open ecosystem through the Skills CLI and the skills.sh registry. | Skill discovery is a different job from skill authoring — and the front door for growing this very collection. | Node.js; skills.sh access | [vercel-labs/skills](https://github.com/vercel-labs/skills) @ 9197d91 |
| [grill-me](categories/development/grill-me/) | A relentless one-question-at-a-time interview that stress-tests a plan or design until every branch of the decision tree is resolved. | The sharp end of requirements work: it surfaces the decisions brainstorming leaves unmade, before they turn into rework. | — | [mattpocock/skills](https://github.com/mattpocock/skills) @ 4ae2317 |
| [grilling](categories/development/grilling/) | The reusable interview engine behind grill-me: grills the user relentlessly about a plan, decision, or idea, one question at a time. | Grill-me is the session wrapper; this is the portable technique that other workflows can invoke on any decision. | — | [mattpocock/skills](https://github.com/mattpocock/skills) @ 4ae2317 |
| [mcp-builder](categories/development/mcp-builder/) | Anthropic's playbook for designing and building high-quality MCP servers, with reference guides and an evaluation harness. | The owner builds connectors and MCP-backed tools; this is the reference guide from the source. | — | [anthropics/skills](https://github.com/anthropics/skills) @ ca45fc4 |
| [ponytail](categories/development/ponytail/) | Lazy senior-dev mode: the smallest change that fully solves the task, explained in one read. | Cuts over-engineering, tokens, and cost on everyday coding without dropping safety or tests. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [ponytail-audit](categories/development/ponytail-audit/) | One-shot whole-repo audit for bugs, security holes, slow paths, untested risky code, and deletable bloat. | A fast health check for inherited or fast-grown codebases, ranked by impact. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [ponytail-debt](categories/development/ponytail-debt/) | Lists every deliberate shortcut: marker in the code as a debt ledger. | Keeps intentional shortcuts visible so they get repaid instead of forgotten. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [ponytail-review](categories/development/ponytail-review/) | Quality review of a change: correctness, safety, load behavior, tests, and whether every line earns its place. | Catches risky or bloated diffs before they ship, explained in plain language. | — | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) @ 96608e0 |
| [skill-creator](categories/development/skill-creator/) | Anthropic's guide and tooling for creating, evaluating, and iterating on agent skills, with eval and description-tuning scripts. | This repo curates skills for a living; the official skill-authoring workflow belongs in it. | — | [anthropics/skills](https://github.com/anthropics/skills) @ ca45fc4 |
| [strategic-compact](categories/development/strategic-compact/) | Suggests manual context compaction at logical task-phase boundaries, so long sessions compact deliberately instead of at arbitrary auto-compaction points. | Long agent sessions die at context limits; compacting at phase boundaries keeps the working thread coherent across a whole build. | Context-compaction harness | [affaan-m/ECC](https://github.com/affaan-m/ECC) @ b38be6a |
| [subagent-driven-development](categories/development/subagent-driven-development/) | Executes an implementation plan with fresh subagents per task, with spec and quality review gates between tasks. | The execution engine for writing-plans in multi-agent harnesses; how the owner's bigger builds actually get run. | Subagent-capable harness | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [systematic-debugging](categories/development/systematic-debugging/) | A root-cause-first debugging method: reproduce, isolate, and prove the cause before changing any code. | Ends guess-and-patch debugging loops; pairs with this project's verify-against-real-behavior rule. | — | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [test-driven-development](categories/development/test-driven-development/) | Guides red-green-refactor TDD: write the failing test first, make it pass with the smallest change, then refactor. | Proven discipline from the most-starred source in this collection; keeps agent-written code verified by construction. | — | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [threejs-fundamentals](categories/development/threejs-fundamentals/) | Three.js scene setup done right: scenes and fog, cameras, the renderer and tone mapping, the animation loop, object hierarchies, transforms, core math, and cleanup, on WebGL or WebGPU/TSL. | The fundamentals entry of the Three.js set: scene, camera, and renderer mistakes are where 3D web work goes wrong first. | Three.js project | [CloudAI-X/threejs-skills](https://github.com/CloudAI-X/threejs-skills) @ 0e18186 |
| [using-git-worktrees](categories/development/using-git-worktrees/) | Sets up isolated git worktrees so parallel features, reviews, and experiments never collide in one working tree. | The standard companion to plan-driven work; makes parallel agent work on the owner's repos safe. | Git | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [vercel-react-best-practices](categories/development/vercel-react-best-practices/) | Vercel Engineering's React and Next.js performance rules: 70 prioritized guidelines across data fetching, bundles, rendering, and re-renders. | The canonical React performance rulebook; applies to the owner's Next.js work (Eggino) and any React build. | — | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) @ 1a2c79d |
| [verification-before-completion](categories/development/verification-before-completion/) | Requires fresh evidence (test runs, command output, live checks) before any claim that work is done or fixed. | Encodes the rule that shipped means verified; cheap insurance against false 'done' reports. | — | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |
| [webapp-testing](categories/development/webapp-testing/) | Tests local web apps with Playwright: manages the dev server, drives a real browser, and inspects console, DOM, and screenshots. | Gives agents a real-browser check for the owner's web apps and artifacts; catches what unit tests cannot see. | Python 3; Playwright; Local dev server | [anthropics/skills](https://github.com/anthropics/skills) @ ca45fc4 |
| [workers-best-practices](categories/development/workers-best-practices/) | Cloudflare's official best practices for Workers: configuration, runtime patterns, and platform API guidance. | Nearly all of the owner's production code runs on Workers (IVAI, TradeAgent, Proxiv3); this is the vendor's own guidance. | — | [cloudflare/skills](https://github.com/cloudflare/skills) @ 1f2cd0a |
| [writing-plans](categories/development/writing-plans/) | Turns an approved spec or design into a detailed, step-by-step implementation plan that can be executed without guessing. | The missing half of the brainstorming workflow already in this repo; makes multi-step builds land first-try instead of drifting. | — | [obra/superpowers](https://github.com/obra/superpowers) @ 22f0b46 |

### [Marketing](categories/marketing/README.md) (12)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [community-marketing](categories/marketing/community-marketing/) | Builds and leverages online communities - Discord, Slack, forums - for product growth and loyalty. | Community-led growth fits bot and channel products especially well. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [competitor-profiling](categories/marketing/competitor-profiling/) | Researches competitors from their URLs and produces structured profile dossiers. | Know exactly what rivals offer and how they position before you ship. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [content-strategy](categories/marketing/content-strategy/) | Plans what content to create: pillars, topic clusters, editorial calendars, and roadmaps. | Deciding what to publish beats publishing at random, for blogs and channels alike. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [copy-editing](categories/marketing/copy-editing/) | Edits and refreshes existing marketing copy: tightening, de-slopping, and sharpening without a rewrite. | Most real work is improving copy that already exists, not starting from zero. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [copywriting](categories/marketing/copywriting/) | Writes and improves marketing copy for pages: headlines, CTAs, value propositions, and hero sections. | Sharp copy is the cheapest conversion lever for landing pages and product posts. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [customer-research](categories/marketing/customer-research/) | Runs and synthesizes customer research: interviews, surveys, review mining, voice-of-customer, and JTBD. | Decisions grounded in real customer language outperform opinion. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [launch](categories/marketing/launch/) | Plans product launches and feature announcements: checklists, go-to-market, waitlists, and release strategy. | Launches are one-shot events; a checklist prevents unforced errors. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [marketing-ideas](categories/marketing/marketing-ideas/) | A bank of proven marketing and growth tactics for software products, matched to the situation. | The fastest way out of 'we need growth but don't know what to try'. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [marketing-psychology](categories/marketing/marketing-psychology/) | Applies behavioral science and mental models - anchoring, social proof, scarcity, framing - to marketing. | Explains why people buy, so offers and copy stop being guesswork. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [offers](categories/marketing/offers/) | Designs the offer itself: value framing, bonus stacks, guarantees, scarcity, and payment structure. | A better offer beats better ads; core skill for anything sold or promoted. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [product-marketing](categories/marketing/product-marketing/) | Creates the product-marketing context doc - positioning, audience, ICP, brand voice - that the other marketing skills build on. | The foundation of the marketing set: write the context once, reuse it in every campaign. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [social](categories/marketing/social/) | Creates, schedules, and optimizes social media content across the major platforms. | Directly useful for running and growing social and channel presences. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |

### [Media](categories/media/README.md) (9)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [cinematic-director](https://github.com/2598588975/skills8.7/tree/eaf80017c7c19c57884da971e7c230a46b39a661/skills/cinematic-director) · link-only | Directs film and AI video like a working director: script breakdowns, beat sheets, blocking and staging, shot lists, storyboard and motion prompts, continuity bibles, and per-model adapters. | The filmmaking-craft representative: executable direction for a camera crew or a generation queue, beyond the video skill's strategy-level coverage. | — | [2598588975/skills8.7](https://github.com/2598588975/skills8.7) @ eaf8001 |
| [ffmpeg-skill](categories/media/ffmpeg-skill/) | A complete local FFmpeg editing system: 42 scripted tools to cut, join, reframe, caption, remove silence, check loudness and export audio/video. | Deterministic media-file work, fully local and scriptable — nothing else in Prime Skill touches actual audio or video files. | FFmpeg 6.1+; Python 3.10+ | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) @ 1ce2c18 |
| [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar/tree/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/plugin/skills/lemo-opuscar) · link-only | Makes complete short films entirely in code: describe a story, pick one of 66 styles (each shipped with a demo film), and the agent directs and renders it with Node/canvas/Three.js and ffmpeg — no video generator involved. | End-to-end code-film production, a genuinely distinct job from cinematic-director's planning layer; listed link-only to keep the collection's motion cluster to one vendored representative. | Node.js; FFmpeg | [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) @ bebbbe1 |
| [openwhispr-cli](categories/media/openwhispr-cli/) | Operates OpenWhispr from the terminal via the `openwhispr` CLI: manage notes, folders, transcriptions and audio, and script dictation workflows against the local desktop app or the cloud API. | Local, offline-capable dictation as an agent-operable CLI — a speech-to-text workflow nothing else in the collection covers. | OpenWhispr desktop app (local backend) or cloud account; @openwhispr/cli (Node.js 20+) | [OpenWhispr/openwhispr](https://github.com/OpenWhispr/openwhispr) @ 3e1f8c2 |
| [rea-video](categories/media/rea-video/) | Reverse-engineers how a video was made, shot by shot: classifies each shot (live action, AI-generated, 3D, 2D/stop-motion, code render, screen capture and more), detects AI edits and overlay packaging, breaks down the audio, and produces an executable remake plan. | REA's sibling for video: the only entry that analyzes and deconstructs existing videos instead of creating new ones — nothing else in the collection reads a finished video's production method. | rea-video CLI (install from the source repo); FFmpeg; Python 3.10+ | [JuneYaooo/rea-video](https://github.com/JuneYaooo/rea-video) @ c9359c4 |
| [reel-story](https://github.com/Jenesyx/arta-edit-studio/tree/a4b9345ae3b714fabd9e2808bba78269124605e1/.claude/skills/reel-story) · link-only | From Jenesyx/arta-edit-studio: turns Farsi-first talking-head videos into animated Instagram Reels — this representative skill is the full-screen story format with B-roll and stickers, rendered with HyperFrames from a Whisper transcript, with no burned-in subtitles. The repo also ships the reel-setup and reel-split skills. | A Farsi-first Reels editing workflow, unique in the collection and close to the curator's own content work; link-only while the young repo matures. | Whisper (large-v3); HyperFrames; FFmpeg | [Jenesyx/arta-edit-studio](https://github.com/Jenesyx/arta-edit-studio) @ a4b9345 |
| [remotion-best-practices](https://github.com/remotion-dev/skills/tree/c7cb2fdcacd134fb2ccb9b7a44f9ffa44e467271/skills/remotion-best-practices) · link-only | Remotion's official best practices for programmatic video in React — markup, animation, captions, maps and interactivity done right. | The motion cluster's one representative: official, actively maintained engine craft, deeper than the video skill's strategy-level coverage; link-only, no license declared. | Remotion project | [remotion-dev/skills](https://github.com/remotion-dev/skills) @ c7cb2fd |
| [video](categories/media/video/) | Guides AI and programmatic video production: avatars, demos, explainers, and generation pipelines. | Video is the highest-reach format; this maps the current tool landscape into workflows. | — | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ 88c79f6 |
| [voicestudio](categories/media/voicestudio/) | Drives a locally running VoiceStudio backend (REST API or MCP): text-to-speech with saved or designed voices, voice cloning, transcription, and automated dubbing or narration workflows. | The collection's only voice skill: local-first speech generation and cloning, no cloud TTS account — nothing else in Prime Skill makes or processes spoken audio. | VoiceStudio backend running locally (localhost:3900) | [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) @ c88bf70 |

### [Research](categories/research/README.md) (16)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [ad-library-teardown](categories/research/ad-library-teardown/) | Analyzes active ads from Meta, Google, and LinkedIn libraries: hooks, offers, CTAs, and claims. | Competitors publish their best-tested messaging in ad libraries for free. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [audience-research](categories/research/audience-research/) | Evaluates a creator or brand audience from public signals: demographics, geography, language, and fit. | Prevents sponsorship and partnership picks based on follower counts alone. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [comment-mining](categories/research/comment-mining/) | Mines comments and replies for objections, questions, buying intent, and voice-of-customer language. | Comments are unfiltered market research, already written by the audience. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [competitor-social-research](categories/research/competitor-social-research/) | Researches competitors' social strategy and turns public data into a practical strategy brief. | Shows what content is winning in your niche and where the gaps are. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [content-repurposing](categories/research/content-repurposing/) | Turns public videos, transcripts, and posts into threads, scripts, newsletters, and content calendars. | One good source becomes a week of channel-ready material. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [creator-profile-teardown](categories/research/creator-profile-teardown/) | Tears down a creator or brand profile: positioning, pillars, hooks, formats, and outlier posts. | A repeatable way to learn from accounts that already win. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [deep-research](categories/research/deep-research/) | Runs autonomous multi-step research through Google's Gemini Deep Research agent and returns detailed, cited reports for market, competitive, technical, and literature questions. | The heavyweight research option: paid per run and minutes-slow, but it produces cited reports the social-data set cannot. | GEMINI_API_KEY (paid) | [sanjay3290/ai-skills](https://github.com/sanjay3290/ai-skills) @ c842558 |
| [exa-search](categories/research/exa-search/) | Calls Exa's semantic search API directly over HTTP, with ranked results, domain and freshness filters, extracted text and highlights, structured output, and streaming responses — no SDK. | A general open-web retrieval primitive for agents, complementing the social-platform research set. | EXA_API_KEY (paid) | [exa-labs/agent-skills](https://github.com/exa-labs/agent-skills) @ 5c5c7eb |
| [influencer-prospecting](categories/research/influencer-prospecting/) | Finds and scores creators in a niche for outreach, partnerships, sponsorships, and UGC. | Builds prospect lists from evidence instead of manual scrolling. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [literature-review](categories/research/literature-review/) | Conducts systematic, scoping, and narrative literature reviews across PubMed, arXiv, bioRxiv, and Semantic Scholar, with coverage tracking and screening, delivered as Markdown or PDF. | Brings academic-grade evidence synthesis to the research category; nothing else here searches the scholarly literature. | Python 3.10+ | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) @ a25cf9e |
| [outlier-post-finder](categories/research/outlier-post-finder/) | Finds posts that massively overperformed a creator's baseline and explains why they worked. | Modeling proven outliers is the shortest path to better content. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [product-demand-research](categories/research/product-demand-research/) | Validates product ideas by mining pain points, demand signals, and objections from social posts and Reddit. | Evidence-backed demand checks before building or launching anything. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [scrapecreators-api](categories/research/scrapecreators-api/) | Reference and access layer for the ScrapeCreators REST API: public data from 27+ social platforms. | The base skill the whole research set calls; it documents every endpoint the others use. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [social-listening-brief](categories/research/social-listening-brief/) | Produces a cited social-listening brief on what people say about a brand, topic, or niche. | A fast reputation and sentiment snapshot before campaigns or launches. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [transcript-intelligence](categories/research/transcript-intelligence/) | Summarizes and mines video transcripts for hooks, claims, quotes, and reusable content atoms. | Unlocks the content inside long videos without watching them all. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |
| [trend-discovery](categories/research/trend-discovery/) | Finds trending topics, hashtags, sounds, and formats in a niche from public trend endpoints. | Trend timing is free reach for channels; this turns trends into content angles. | ScrapeCreators API key (paid) | [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills) @ 64ba7b4 |

### [Reverse Engineering](categories/reverse-engineering/README.md) (2)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [blind-llm-agents](categories/reverse-engineering/blind-llm-agents/) | Hardens release artifacts against AI reverse-engineering agents with decoys, analysis-budget exhaustion and dead ends, driven by the bla-agents CLI. | The defensive mirror of REA: REA takes artifacts apart; this protects your own releases from being taken apart. | bla-agents CLI | [qybaihe/bla](https://github.com/qybaihe/bla) @ eb44984 |
| [reverse-engineer-anything](categories/reverse-engineering/reverse-engineer-anything/) | Reverse engineers binaries, Electron/JS apps, .NET, firmware, and browser targets with REA, backed by runtime evidence. | The owner's reverse-engineering workhorse: explains features, compares versions, and guides reconstructions from real artifacts. | REA toolchain (optional) | [morluto/rea](https://github.com/morluto/rea) @ d7df9df |

### [Security](categories/security/README.md) (6)

| Skill | What it does | Why it's here | Requires | Source |
|---|---|---|---|---|
| [api-security](categories/security/api-security/) | API security testing techniques and scenario playbooks for REST, GraphQL, WebSocket, and LLM-integrated APIs, mapped to the OWASP API Top 10. | The deep, scenario-level companion to security-review: the owner's bots and workers expose APIs, and this is the offensive testing reference for them. | — | [transilienceai/communitytools](https://github.com/transilienceai/communitytools) @ 95fdc12 |
| [incident-runbook-templates](categories/security/incident-runbook-templates/) | Production-ready incident response runbook templates: severity levels, triage and escalation paths, step-by-step recovery, and communication structure. | When a live bot or worker goes down at 3 AM, a written runbook beats improvisation; this is the template set to write them from. | — | [wshobson/agents](https://github.com/wshobson/agents) @ 7e2fb55 |
| [secrets-management](categories/security/secrets-management/) | Secrets management for CI/CD pipelines using Vault, AWS Secrets Manager, and native platform tooling: storage, rotation, and least-privilege access. | Every project here juggles bot tokens and API keys; this is the disciplined way to store and rotate them instead of scattering them across configs. | — | [wshobson/agents](https://github.com/wshobson/agents) @ 7e2fb55 |
| [security-review](categories/security/security-review/) | Security checklist and patterns to run when adding authentication, handling user input, creating API endpoints, or touching secrets and payments. | The flagship security skill from the most-starred collection in this repo; turns 'did we think about security' into a concrete pre-ship checklist. | — | [affaan-m/ECC](https://github.com/affaan-m/ECC) @ b38be6a |
| [semgrep](https://github.com/trailofbits/skills/tree/711af095215ad4ecde5b90cd1d0124b3f1c4ca9e/plugins/static-analysis/skills/semgrep) · link-only | Trail of Bits' Semgrep skill: writing and running Semgrep rules for static analysis and code auditing. | The canonical static-analysis skill from a top security firm; listed link-only because its CC-BY-SA-4.0 license does not allow redistribution. | Semgrep CLI | [trailofbits/skills](https://github.com/trailofbits/skills) @ 711af09 |
| [stride-analysis-patterns](categories/security/stride-analysis-patterns/) | Applies the STRIDE methodology to threat-model a system — spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege — with mitigations for each. | Threat modeling before code exists catches design flaws no later review can; this is the canonical STRIDE pattern set from a widely used plugin library. | — | [wshobson/agents](https://github.com/wshobson/agents) @ 7e2fb55 |
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

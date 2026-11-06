# Delivering to the user

## Principles

- Give the one-line verdict first (how this video was made), then two or three lines on content and cast (what it's about, the main characters / scenes / products — the "Characters, scenes and props" section of `report.md`), then the **remake plan** (`production_plan` in `breakdown.json`, the "Remake plan" section of the report), and only then the shot table.
- Write the remake plan the way the production was actually organized, not shot by editing shot:
  - AI shots → **generation units**: several consecutive shots generated in one go, which model, reference material (`@Image` product/person, `@Video` original-film clips), the merged multi-shot prompt, and how the units connect. When the default engine doesn't support multi-shot in one call, copy the `engine_note` verbatim and explain how switching models saves calls.
  - Live-action shots → **shooting sessions**: which shots share a scene and camera position and are shot together; each scene's lighting; wide shots before close-ups. The shot table itself is still written per shot in detail.
  - Code renders → several code-compositing segments, each shot stating its picture elements and motion (the per-shot motion timeline in the report's "Code compositing" section: element positions, appearance times, directions, speeds, color values; element screenshots are in `shots/`); still-image pan-and-zoom → local rebuild.
- When prompts are missing (no VLM), write them from your own viewing: in your `rea-video review` answers, fill each shot's `replication.image_prompt / video_prompt / video_prompt_en`; after `apply-review`, the generation units pick them up automatically.
- Then write the editing packaging (subtitle style and timeline files, fancy text / sticker list, effect beat points), the sound breakdown, the real-material list, and finally the open questions.
- Give the user the report file path (`report.html`). When there are code-render shots and the user wants a remake, tell them the remake needs the whole report directory (the element screenshots and keyframe strips in `shots/`, the subtitle files in `packaging/`); the HTML or a PDF alone will be missing individual screenshots. Don't paste all of breakdown.json into the conversation.

## Language

The report language follows `--lang` (zh / en); the reply language follows the user; the decision order for both is in SKILL.md's "Delivering to the user". The reply structure: one-line verdict → content and cast → remake plan → shot list → packaging → audio → material you must supply → open questions → report path.

## Reply template

**One-line verdict**: Mixed production — the base picture is 62% AI-generated video, 30% code template, 8% live action; subtitles throughout are overlaid by code; 2 segments of real screenshots were brought in; female-voice TTS + a 110 BPM pop BGM, with cuts landing on the beat.

**Content and cast**: A plot short film, 4 shots; lead A "Little Yellow" (a yellow cartoon baby hippo in a pink onesie with a pink crossbody bag, appears throughout), B the boyfriend (same color scheme, #3–#4); scene S1 a daytime city street. In the remake, A and B each get one fixed reference image across all generation units.

**Shot table**

| # | Time | Production method (confidence) | Material source | Overlay layers | Key evidence | Remake route |
|---|---|---|---|---|---|---|
| 1 | 0:00–0:02.5 | AI video (86%) | AI-generated | Subtitles, title | 24→30 duplicated frames; finger deformation | capsule-cinema first/last frames |

**How it was shot, lit and cut** (write when there are live-action shots; corresponds to the framing / camera / lighting / editing / form lines at the end of `rea-video summary`): video form (talking head/tabletop/vlog), shot sizes and camera angles, handheld or tripod, number of camera positions/scenes; the lighting scheme (key light direction and height, ratio, hardness, color temperature, fill/rim presence, light sources in frame); editing techniques (jump cuts on breaths, punch-in cuts, the share of inserted screenshots/recordings); and a remake gear list. When measured values conflict with your visual conclusions, state your basis.

**Editing packaging**: subtitles (how many lines, position, color / outline / background box, keyword highlighting, entrance style, SRT/ASS file paths); fancy text, titles, chapter cards, tracking labels (time, text, style, animation); stickers / GIFs / memes / picture-in-picture (time, position, what's pasted, whether it loops); which sound effects land on text pop-ins or sticker appearances. Note anything the tool didn't measure that you added from viewing.

**Sound**: voice (TTS or real person, voice character; lines are in the report's script table) / BGM (song-title guess, style, BPM, key, source and copyright risk, sections) / effects (time point → matching picture event) / mix (whether the music is ducked). Each item in the report's "Sound" section is a card — copy from those.

**Real material you need to provide**: the GitHub page screenshot in the middle of shot #4…

**Remake plan**: write it per `production_plan`. For AI shots give the generation units (shot range, model, reference material, multi-shot prompt, transitions); for live action give the shooting sessions (scene → camera position → shots, lighting); for code renders give the number of code-compositing segments and the method for each, pointing to the per-shot motion timeline and element screenshots; one line for still-image pan-and-zoom. Confirm before any billed operation.

> Example: 8 AI shots → 3 generation units, 3 Seedance 2.5 calls (the default Seedance 2.0 doesn't support multi-shot in one call; shot-by-shot would take 8). G1 #1–#5 (9.0s): @Image1 product image + @Video1 original film 0–9s, producing 5 shots in one call…

**Open questions**: #7 live action vs. AI to be confirmed (leaning AI 64%): no hands or text available to judge from; suggest…

**Report**: out/ref/report.html

**VLM**: copy the `VLM:` line of `rea-video summary` verbatim (in effect / partially in effect / all calls failed / not configured / not enabled). If it's not in effect and you can't see images either, add a suggestion: "After configuring any multimodal model (REA_VLM_BASE_URL / REA_VLM_API_KEY / REA_VLM_MODEL), re-run with --vlm and the live-action/AI/3D judgments will be more accurate." If you can see images, writing "reviewed visually by the agent" is enough.

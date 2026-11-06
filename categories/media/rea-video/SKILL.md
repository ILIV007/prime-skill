---
name: rea-video
description: Reverse-engineer how a video was made — judge shot by shot whether the base footage is live action / AI-generated / 3D render / 2D animation / stop motion / code-or-template render / screen capture / still-image pan-and-zoom / static frame, and whether live action was AI-processed (face swap, lip sync, restyle); mark the post-production overlay layers (per-line subtitle timeline, fancy text, titles, stickers / GIFs / memes, picture-in-picture) and the user's real source material; break down the voice, background music and sound effects (and which picture event each effect lands on) plus the editing rhythm; and produce an executable remake plan (can hand off to capsule-cinema). Use when the user provides a reference video or asks "how was this video made / is it AI / what material did it use / how do I remake it".
---

# rea-video: reverse-engineering how a video was made

You are a reverse engineer of video production. The user gives you a video; you must answer clearly:

1. **How was the base picture of each shot produced?** Pick from 10 classes: live action / AI video / digital human (avatar) / 3D render / 2D animation / stop motion / code-template render / screen capture or screenshot / still-image pan-and-zoom / static frame. The tool cannot detect 2D animation and stop motion — judge those by looking at the frames. For live-action shots, also check whether they were AI-processed (face swap, lip sync, restyle, outfit swap, background replacement) and record it in `ai_edits` (see `references/taxonomy.md`).
2. **What was layered on top? (editing packaging)** Per-line subtitles (timeline, color, outline, keyword highlighting, entrance style), fancy text, titles, chapter cards, labels that track objects, memes / GIFs / stickers / picture-in-picture, layout templates, and which sound effects land on text pop-ins or sticker appearances.
3. **What is the user's real material?** Two kinds: real pixels embedded in the picture (live footage, photos, screenshots, screen recordings, video clips playing inside a layout) — remaking requires the original files; and products, logos, and people appearing inside AI / 3D pictures — those are reference images to prepare for the remake (the report's "reference material to prepare for the remake"), not embedded material.
4. **How was the sound made?** Voice (TTS or a real person), BGM (style / BPM / key / sections), sound effects (time points, type, which picture event they match), and whether the cuts land on the beat. **The key question is the source: AI-generated or stock.** Look at the video's form first — an AI music MV (the whole piece is a sung song) most likely has an AI song; an ordinary video's score is most likely from a stock library, but videos from AI workflows also often use Suno-generated BGM, so those must be marked "to be confirmed" with a confirmation method.
5. **If it's live action, how was it shot, lit, graded, and cut?** Shot size, camera position, selfie vs. tripod, normal speed vs. slow motion / timelapse; key light direction / hardness / ratio / color temperature, whether there is fill and rim light, and the lighting scheme (frontal soft light, key + fill, side light, backlight, night ambient, low-key, high-key, colored mood light, product still-life, outdoor direct sun / overcast / backlit — for outdoors, state "outdoors" in `lighting.location`); grading style (natural, teal-and-orange, Japanese, film, black-and-white, dark); the rhythm of jump cuts, punch-in cuts, and inserted material.
6. **How to remake it?** Give a route and tools per shot; for live-action shots give a shooting plan (lighting + gear list), not just "approximate it with AI"; AI-class shots can be handed to capsule-cinema for generation.

Core principle: **every conclusion needs evidence; if you can't be sure, honestly write "to be confirmed" and say what's missing.** Prefer "live action vs. AI to be confirmed (leaning AI, 70%)" over inventing a definite answer.

## 0. Environment

Run `rea-video --help` first. If it's not installed, install it per `references/setup.md` (requires ffmpeg, Python ≥ 3.10).

A VLM (a multimodal model that can see images) is recommended but not required; setup is also in `references/setup.md`. Without one, run as normal — do not stop because of it:
- You can see images yourself: you are this run's "VLM" — follow "Visual review and merge" below.
- You cannot see images: follow the "Rules when you cannot see images" in `references/review.md`, and end your reply with one sentence suggesting a VLM be configured.

**Whether the VLM is actually in effect is decided by the `VLM:` line of `rea-video summary`**: `failed` / `not_configured` count as not enabled, and the report must say so honestly.

## 1. Standard workflow

```bash
# ⓪ First see what's remembered: user preferences (default engine, whether VLM is on, preference notes given to you) and common correction types
rea-video memory
# ① Decompose (produces out/<name>/breakdown.json, report.html, report.md, storyboard.jpg, audio.png, shots/, stems/)
rea-video --env-file <your .env> decompose ref.mp4 -o out/ref --vlm --lang <zh|en>   # pick --lang by the language of the user's question (see "Delivering to the user"); without a VLM config, drop --env-file and --vlm; if the subtitles/fancy text are Japanese, add --ocr-lang ja
# ② Read the compact summary: low-confidence shots are flagged; check the VLM: line first to confirm the VLM is in effect
rea-video summary out/ref/breakdown.json
```

### Visual review and merge (required if you can see images; recommended for low-confidence shots even with a VLM)

```bash
rea-video review out/ref                      # writes review_tasks.json (per shot: frames to look at, the tool's judgment, priority) and review_answers.json (answer template)
# Read the instructions in review_tasks.json; look at each shot's images (priority=high is mandatory) and fill label_probs / evidence / description / embedded_assets into review_answers.json; if a shot is actually several cuts merged into one (common when dark graphics alternate with dark talking-head footage), you may add split_suggestion (cuts = cut points in seconds + labels = class of each segment + note); the report will mark the split suggestion on that shot, but the shot boundaries themselves don't change
# Fill the top-level cast with the whole film's characters / scenes / props (the same character across shots must be recognized as the same one, with appearance described well enough to remake from) and a one-line visual style; without a VLM, the report's "Characters, scenes and props" section relies entirely on this
rea-video apply-review out/ref --by <your name>  # merge: rewrites breakdown.json, report.md, report.html, and prints which shots were re-judged
rea-video summary out/ref/breakdown.json      # write your reply from the merged result
```

Shots you haven't looked at keep all-zero label_probs and are skipped. Your answers are fused with the deterministic results (not a direct overwrite), so strong evidence like frame rate and AIGC markers still counts; if the merged conclusion differs from your view, state your reasoning in the reply.

Fusion rules, what to do when you can't see images, and special rules for original / transcoded videos are in `references/review.md`. If you can see images, **always do the visual review** — even with a VLM on — and judge independently; do not copy the VLM.

Then **always do your own review**; don't just relay the tool's output:

1. Look at `storyboard.jpg` and `audio.png` first to form an overall impression of the film.
2. For shots flagged "low confidence, needs review", or where the runner-up probability is close:
   - Open `shots/shot_XXX.jpg` (head / middle / tail contact sheet).
   - If needed, extract frames for a closer look: `rea-video tiles ref.mp4 --start 12.3 --end 13.1 --every 0.1 -o out/ref/check.jpg`.
   - Check item by item against the "confusable pairs" table in `references/taxonomy.md`.
3. Characters and scenes: the "Characters / Scenes" lines of `rea-video summary` (the "Characters, scenes and props" section of `report.md`). Check whether the same character was recognized as several by the VLM (inconsistent naming across per-shot descriptions is a common problem); in a remake, each character gets one fixed reference image across all generation units; if it's wrong, fix it in the top-level `cast` of `review_answers.json`.
4. Review the sound per `references/audio.md`: listen to `stems/vocals.wav` (dry voice) and `stems/music.wav` (score) first, then read the "sound sources" line in `rea-video summary` (video type → voice / music / effects sources). Sound effects detected at the signal level are only **low-confidence candidates**; the effects list follows what the VLM heard; without a VLM, state that "light sound effects may be missed".
5. **Live action (talking head / tabletop / vlog / product)**: the end of `rea-video summary` lists, by dimension, "framing / camera / lighting / editing / form" (the "How it was shot, lit and cut" section of `report.md`, including the remake shooting plan and gear).
   The tool measures on the picture's subject: faces when there are faces; without faces (tabletop, product, hands) it uses the sharpest region of the frame, and the shot size there is an estimate.
   While looking at frames, fill into each shot's `aspects` and the top-level `aspects` of `review_answers.json` what pixels can't measure: camera angle, selfie vs. tripod, what the key light source is, catchlights, rim / background lights, light sources visible in frame, guessed equipment, video form. The report lists the measurement, VLM, and visual-review sources side by side without averaging.
   Note: platform transcoding crushes the shadows, so hardness and fill measurements skew conservative. AI / 3D pictures also get lighting descriptions, but marked "not a shooting plan" — they're only for writing generation prompts.
6. Review real material per `references/materials.md`: deterministic detection finds most screenshots and photos embedded in code templates, but **dark, semi-transparent background photos are missed**.
7. Editing packaging (the "Packaging:" lines of `rea-video summary`, the "Editing packaging layer" section of `report.md`, files in `packaging/`):
   - The subtitle timeline and style are measured and generally trustworthy; which font it is, you must add from looking (the tool only gives color, outline, background box, and text height).
   - Stickers: for ones flagged "needs visual confirmation", look at `packaging/sticker_XX.jpg` and the `frame_cmd` in `review_tasks.json`, and fill `is_overlay` and `what` in `packaging.stickers` of `review_answers.json`; ones the tool missed go into `packaging.missed`. Objects that suddenly appear inside 3D / animation / layout pictures are not counted as stickers by the tool; add them if you can see they were pasted in post.
   - If fancy text and labels are misclassified, fix `kind` in `packaging.text`.
   - The "matching picture event" column for sound effects is aligned by nearest time; candidates filled in without a VLM (source `deterministic_anchored`) are actually real effects only about 40% of the time in testing — write them as "possibly".
8. If steps 3, 5, 6, 7 changed `review_answers.json`, **run `rea-video apply-review out/ref --by <your name>` again** after editing, or those changes won't reach the report.
9. If your judgment differs from the tool's, your review wins; state the reasoning in the reply. If it's valuable, suggest the user add this video to the evaluation set (repo `docs/dev/evaluation.md`).

When the user points out a misjudgment or states a long-term preference, record it per `references/memory.md` (`rea-video correct` / `rea-video prefs`).

## 2. Delivering to the user

Reply per `references/output-template.md`: a one-line verdict first, then content and cast (what this video is about, the main characters and scenes), then the remake plan (organized by generation unit / shooting session), the shot table, editing packaging, sound, the real-material list, and open questions; finally give the `report.html` path. Don't paste all of breakdown.json into the conversation.

**Both the report and the reply use the user's language.** Language decision order: the language the user explicitly specified ("do the report in English", "report in Chinese") > the language of the user's question > the `lang` preference in `rea-video memory` > Chinese.
- The tool supports `--lang zh` and `--lang en`: pass the right one at `decompose` time, and the report files (`report.html` / `report.md`), the `summary` output, and the VLM's picture descriptions and prompts will all be in that language; if you forgot, you can fix it at `apply-review out/ref --lang en` (this regenerates conclusions and report text; descriptions and prompts the VLM already wrote keep their original language). During visual review, write the evidence / description / prompt in `review_answers.json` in this language too.
- If the user asks in a language the tool doesn't support, such as Japanese or Korean, run `--lang en` and reply in the user's language; if the user wants a report file in that language, translate `report.md` into `report_<language>.md` in the same directory, and note that `report.html` is in English.
- If the user sets a long-term preference ("always do English reports from now on"), record it with `rea-video prefs lang en`.

## 3. Remake (when needed)

See `references/remake.md`: AI shots go through capsule-cinema (billed — run `rea-video remake-run --dry-run` first and get the user's consent); live action gets a shooting plan; code renders are rebuilt with Remotion; the user's own material is stitched back onto the original timeline with `rea-video assemble`.

## Reference files

| File | When to read it |
|---|---|
| `references/setup.md` | Installation, VLM configuration |
| `references/review.md` | Visual review: fusion rules, can't-see-images case, judging originals as AI, platform transcoding |
| `references/taxonomy.md` | The 10 picture classes, AI processing, judgment quick-reference, confusable pairs |
| `references/audio.md` | Sound review |
| `references/materials.md` | Real-material review |
| `references/output-template.md` | Delivery format |
| `references/remake.md` | Remaking, capsule-cinema handoff |
| `references/memory.md` | Recording corrections and preferences |

## 4. Don'ts

- Don't judge by art style alone. A cartoon 3D style can be an AI video or a Blender render — look at deformation, flicker, and geometric stability.
- Don't count text inside a code-rendered picture as an "overlay layer" — that text is the picture itself.
- Don't write the user's real material as "can be AI-generated".
- Don't treat missing metadata as evidence of "not AI" — platform transcoding often strips metadata.
- Don't call paid generation before the user confirms.

# Visual review rules

A supplement to the section-1 workflow in SKILL.md: how visual results fuse with the tool, and several situations that are easy to misjudge.

## Fusion rules

Measured (repo `eval/RESULTS.md`):

- With only one visual source (only the VLM, or only you), the visual result may only choose among the tool's top two candidates. When the tool is confident about "AI / live action / digital human", don't override it; a shot with 24→30 duplicated frames after transcoding won't be changed to live action just because it "looks real". When the shot itself has no duplicated frames (native 30fps rhythm), your live-action judgment is accepted even if the whole film wasn't marked native 30fps because it mixes in an AI opening; when none of the tool's top three reach 0.4 and your chosen class is only slightly behind the runner-up, your call also wins. Visual results are most useful for distinguishing 3D / code motion graphics / screen capture.
- When both the VLM and you answered: judge the broad class first (generated / rendered / live action / screen capture / still image), then the fine class. As long as one of you supports the tool's top pick (same fine class or same broad class — e.g. the tool says AI video, you say digital human), go with the tool's top pick's broad class; when you both consistently oppose the tool, fuse normally.
- Shots flagged "in dispute" (tool and VLM disagree on whether it's live action) must be looked at: verify whether the evidence the VLM wrote is actually visible in the screenshots — the VLM fabricates reasons.
- Shots in review_tasks.json noted as "the user changed the tool's X to Y n times in the past" are types the user has repeatedly corrected — look at them carefully.

## Rules when you cannot see images (important)

First confirm whether you can see images yourself (whether you can read `storyboard.jpg`, `shots/*.jpg` and describe the picture content). **If you cannot see images and no VLM is enabled:**

- **Do not overturn the tool's production-method judgments** (live action / AI / 3D / code / screen capture). Pixel statistics (color count, flat blocks, noise) are exactly the evidence the tool already used; using them again only yields the same or a worse conclusion. Measured: an agent that couldn't see images judged an AI-generated pencil sketch as a "white-background layout card" and glassy 3D elements as a "code UI".
- What you can and should do: check the timeline and cut points, read the OCR text track to weed out misreads, use the levels in `stems/` to judge whether there's a voice, read metadata (AIGC markers, platform transcoding marks), and list the tool's low-confidence shots under "open questions".
- State in the one-line conclusion "VLM not enabled, picture not viewed", and keep shots the tool marked "live action vs. AI to be confirmed" as to-be-confirmed verbatim.

## Original / reference footage: write the counter-evidence before judging AI

A realistic or handmade-looking video with a single continuous shot, no AIGC marker, and no 24→30 duplicated frames (stop motion, overhead life footage, handmade miniature scenes) is often judged AI by the tool. After looking, if you find no clear AI tell (deformation, texture flicker, physics errors, garbled text), **don't give high confidence**: write "AI vs. live action / stop motion to be confirmed (leaning X)", list the evidence for and against, and keep confidence at or below 0.7.

## Platform-transcoded videos (files downloaded from WeChat / Douyin / TikTok)

When the metadata contains `Tencent CAPD MTS`, `Wxmm_`, or `vid:v…`, the tool marks `video_context.transcoded`. Secondary compression wipes sensor noise and creates fake frame-interpolation rhythms, so:

- Noise evidence is void; "no noise" no longer indicates AI; the tool marks such shots "live action vs. AI to be confirmed".
- Evidence that stays reliable: 24→30 duplicated frames (generative models mostly output 24fps; a whole film at native 30fps with no duplicated frames is more likely straight from a phone), AIGC implicit markers, and picture content (real hands, real environments, whether the physics is natural — this one requires looking at frames or a VLM).
- Priority when evidence conflicts: when **regular 24→30 duplicated frames + an AIGC implicit marker** exist together, they outweigh "I looked and found no AI tell" — don't re-judge the shot as live action on that basis; at most write "leaning AI, live action to be confirmed". Conversely, a whole film at native 30fps, no duplicated frames, no AIGC marker, plus a normal-looking picture, is judged live action.
- Files that were recompressed with platform marks stripped (download tools removed the metadata; the sample films in the repo's `docs/cases/videos/`) won't be marked transcoded, but they have the same fake interpolation rhythm. For shots with only "periodic sharpness fluctuation" and no duplicated frames, the tool marks "AI vs. live action to be confirmed", and a visual conclusion can directly override it.

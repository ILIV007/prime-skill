# Remake

## How to remake each shot class

- **AI-class shots**: use the original shot's first/last frames plus the VLM prompts, generated through capsule-cinema (billed — `--dry-run` first, and get the user's consent).
- **Still-image pan-and-zoom, static frames**: rebuild locally with the measured motion parameters.
- **Code renders**: rebuild with Remotion. Hand the report's "Code compositing" section (per-shot method, per-shot motion timeline, color values) together with the element screenshots and keyframe strips in `shots/` and `packaging/overlays.ass` to the person or LLM writing the code; animate by the timeline's times and positions, redraw the graphics from the screenshots, and cut out and use directly anything that can't be redrawn, like icons / logos / illustrations.
- **Real material**: list it and have the user provide it.
- **Sound**: prepare the three tracks separately — TTS, BGM (by BPM / key / mood), effects (by time point).

**Material the user shot themselves, or videos they generated manually on the web, stitched back onto the original timeline** (no capsule-cinema needed):

1. Map the material to shots using the shot table (shot numbers and durations in `report.md`). When one long piece covers several shots, first split it by action with ffmpeg; when the mapping is uncertain, show the user screenshots to confirm.
2. Write a `results.json`: `{"results": {"<shot number>": {"video": "<absolute path to the material>"}, ...}}`. When a manually generated "generation unit" video covers several shots, likewise first split it by the "shot i (a–b s)" times in the unit's prompt, then fill it in.
3. `rea-video assemble out/ref/breakdown.json <path to results.json>`: each piece of material is trimmed to the original shot's duration, shots left blank temporarily use the original film as a placeholder, and the sound keeps the original; outputs `remake.mp4` and a side-by-side `compare.mp4`. Tell the user which shots are still original-film placeholders and that the sound still needs replacing.

**Limits of automatic generation**: `remake-plan` and capsule-cinema currently still call the model once per shot; the multi-shot prompts of the report's "generation units" must be pasted manually by the user into a model that supports multi-shot (e.g. Jimeng / Seedance 2.5). Explain this to the user, and give the call counts for both approaches.

## capsule-cinema handoff

Generation must use capsule-cinema's own Python environment. `rea-video remake-run` / `capsule-draft` automatically find `$CAPSULE_CINEMA_PYTHON` or `<capsule-root>/.venv/bin/python`; you can also specify with `--python`.

```bash
CC=$CAPSULE_CINEMA_ROOT   # path to the capsule-cinema repo
rea-video remake-plan out/ref/breakdown.json --capsule-root $CC --engine seedance2.0   # or --mode image_to_video / --labels ai_video
rea-video remake-run out/ref/remake/jobs.json --dry-run      # show the user the tasks and cost first
rea-video remake-run out/ref/remake/jobs.json                # run only after the user confirms
rea-video assemble out/ref/breakdown.json out/ref/remake/results.json                   # stitch back onto the original timeline + compare.mp4
rea-video capsule-draft out/ref/breakdown.json --capsule-root $CC --capsule-name xxx [--write-capsule]
```

- Each job's `executor` value in jobs.json:
  - `capsule_cinema`: call a model to generate
  - `local_ffmpeg`: local rebuild of a still image
  - `keep_original`: keep the original film, e.g. code renders, screen captures, real material
- `user_assets`: the real material the user must provide for this shot. Generation results are only approximations — remind the user.
- `capsule-draft`: injects the breakdown results through capsule-cinema's own `tool_factory` without modifying capsule-cinema code; the generated recipe draft defaults to `review_required`.

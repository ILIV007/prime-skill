# Installation and VLM configuration

## Installation (one-time)

```bash
pip install "rea-video[ocr] @ git+https://github.com/JuneYaooo/rea-video"   # requires ffmpeg; Python ≥ 3.10
# or, inside the repo: bash scripts/install_skill.sh (installs the CLI and links the skill into each agent's directory)
rea-video --help
```

If pip reports `externally-managed-environment` (Homebrew / newer Ubuntu system Python), don't add `--break-system-packages`; use
`pipx install "rea-video[ocr] @ git+https://github.com/JuneYaooo/rea-video"` instead, or just run `install_skill.sh` (it automatically falls back to pipx or an in-repo `.venv`).

If you installed `[ocr]` manually, the OCR dependencies install another copy of `opencv-python`, which fights over the same `cv2` directory as the `opencv-python-headless` that rea-video uses. After installing, run once:
`pip uninstall -y opencv-python && pip install --force-reinstall --no-deps "opencv-python-headless>=4.8,<5"` (`install_skill.sh` does this automatically).

## VLM configuration (recommended, not required)

**VLM (recommended, not required)**: a VLM is a multimodal large model that can see images/video (Gemini, GPT-4o, Doubao, Qwen-VL, etc.). Without a VLM, the tool relies only on pixel statistics, frame rate, OCR, and metadata; it still runs to completion and produces a report, but **the live-action / AI / 3D distinction becomes markedly weaker**, and the sound-effects list has only low-confidence signal-level candidates. With a VLM, the tool sends each shot's short clip and key frames to it and fuses the result with the deterministic findings.

Configuration goes through an OpenAI-compatible interface, read in this order:

1. `REA_VLM_BASE_URL` / `REA_VLM_API_KEY` / `REA_VLM_MODEL` (`REA_VLM_MODEL` may list several models, comma-separated; on failure it automatically moves to the next)
2. If those are absent, fall back to capsule-cinema's `VIDEO_ANALYSIS_*` or `GEMINI3_*`

Read the configuration with `--env-file <some .env>` (e.g. reusing capsule-cinema's). **Never write keys into the conversation, the repo, or the report, and don't open the .env to look at its contents.**

If the user hasn't configured a VLM: run as normal without `--vlm`; don't abort the task because of it.

- **You can see images yourself (multimodal agent)**: you are this run's "VLM"; there's no need to suggest the user configure another one. Follow "Visual review and merge" in section 1 of SKILL.md: `rea-video review` → look at each shot and fill in answers → `rea-video apply-review`; your judgment is merged into the tool's conclusions and the report. In the conclusion, write "VLM not enabled; reviewed visually by the agent".
- **You cannot see images**: follow the "Rules when you cannot see images" in `review.md`, and end your reply with one sentence suggesting a VLM be configured (explaining it improves the live-action/AI/3D distinction and sound-effect recognition).
- Measured (2026-10-30, repo eval/RESULTS.md): merging an agent's visual review is more accurate than enabling the Gemini VLM alone; Gemini easily misjudges cartoon-3D-style AI video as 3D render and game UIs drawn into the picture as screen capture. So if you can see images, **always do the visual review** — even with a VLM on — and judge independently; don't copy the VLM.
- An external VLM still does things you can't replace: it can watch motion in video clips directly and hear the audio track. If you can only see still frames and can't hear sound, still mark sound-effect and voice sources "to be confirmed".

**Whether the VLM is actually in effect is decided by the `VLM:` line of `rea-video summary`** (also `analysis.vlm.status` in `breakdown.json`): `ok` in effect, `partial` some shots have results, `failed` requested but every call failed (e.g. a server 503), `not_configured` requested but no configuration found, `off` not requested. `failed` / `not_configured` count as VLM not enabled; the report must say so honestly and must not claim "VLM enabled".

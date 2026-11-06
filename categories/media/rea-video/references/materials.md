# The user's real material

**Definition**: pixels in the picture that the producer didn't generate or render but brought in from reality — live-action video, real photos, web/app screenshots, screen recordings, video clips playing inside a layout, pasted-on logos / product images. When remaking, the user must supply these as original files; **they must not be written as "generate with AI"**.

**Keep separate from "reference material"**: products, logos, and people appearing in AI video, digital-human, or 3D pictures have pixels made by a model or a renderer, so they don't count as real material; they are recorded in `material.references`, appear in the report as "reference material to prepare for the remake", and are fed to the model as reference images (`@ImageN`) during the remake. Products in live-action footage are props and are likewise recorded as references.

## How the tool marks it

- **Full frame**:
  - Live action → live-action video material
  - Screen capture / screenshot → screen-recording material or UI screenshot (a still one counts as a screenshot)
  - Static frame / pan-and-zoom whose source is a photo or screenshot → real photo or screenshot
  - Static frame of unknown source (no VLM) → "image material (real/AI to be confirmed)", not counted as real material
- **Embedded** (only detected inside rendered pictures, i.e. code renders, screen captures, 3D, rendered cards):
  - Photo-texture regions: high grayscale entropy, no flat fills, and not in the subtitle band → photo/image material, **marked "real or AI to be confirmed"** (what's pasted into a template may also be an AI image). Either the VLM confirms it, or you judge from the frames yourself
  - Light-colored panel + ≥6 instances of small text in a single frame → UI screenshot (counts directly as real material)
  - Motion inside a region while the surroundings are still → embedded video clip or screen recording
- **VLM**: entries in `embedded_assets` with `is_real_material=true`. When the base is a rendered layout (code, screen capture, still image), it counts as embedded material; a `real_footage` the VLM reports is recorded as an "embedded video clip" (it may itself be AI video); when the base is AI video / digital human / live action, or it's a product, logo, or person in 3D, it's recorded as reference material.

## Known misses

- Dark, semi-transparent photos used as mood backgrounds (e.g. the NASA background image in mediank): texture contrast too low for deterministic detection. When you see a dark template, look at the background yourself.
- Dark-theme web screenshots: not a light-colored panel, so undetectable — check whether there's a browser or UI frame in the picture.
- Small logos and product images overlaid on live-action or AI footage: the deterministic layer doesn't do embedded detection on photo bases (prone to false positives), so these rely on the VLM.

## How to write it in the delivery

List item by item: shot number, time, material type, position in the picture, content description, and "for the remake you need to provide: …".

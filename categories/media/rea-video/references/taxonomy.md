# Production-method taxonomy and confusable pairs

## The 10 base-picture classes

| Label | Class | Typical evidence | Remake route |
|---|---|---|---|
| live_action | Live action | Sensor noise σ>1, temporal noise >0.8, per-pixel-unchanged ratio <0.55, handheld shake, native 60fps, capture-device metadata | Live-action material (user-provided), or AI image-to-video approximation |
| ai_video | AI-generated video | Photo texture without sensor noise, 24→30 duplicated frames or frame-interpolation periodicity, smoothly drifting camera moves; the VLM sees finger, text, or object deformation or texture flicker | capsule-cinema first/last-frame generation |
| avatar | Digital-human talking head | Fixed camera, frontal face, only the mouth and head move, audio-driven | TTS/voice clone + digital human |
| cg_3d | 3D render | Flat-shaded / clean materials but the background is not pixel-frozen, stable geometry, no deformation | Blender/C4D, or AI first/last-frame approximation |
| code_render | Code/template render | Flat blocks >20%, colors used <70, many horizontal/vertical straight edges; background pixel-frozen with only local elements moving; no material texture (smooth color gradients, large saturated flat colors, glow on dark backgrounds, fractal/shader color fields); on dark backgrounds the bright parts are all fine specks/lines (particles, point clouds, wireframes) | Remotion/HTML rebuild; the report gives the method by picture type (particles → Three.js, color fields → GLSL, gradients → CSS blur, charts → SVG/D3) |
| screen_capture | Screen capture/screenshot | Large light-colored UI areas, dense small-size text, low saturation, full-page scrolling | Record the real UI (user-provided) |
| still_motion | Still-image pan-and-zoom | Rigid-transform inlier ratio >95%, residual <0.3px, no residue after compensation, no 24fps frame-rate trace | One image + local ffmpeg rebuild with the measured parameters |
| static_hold | Static frame | ≥85% of frames repeat pixel-for-pixel | One image |
| anim_2d | 2D animation | The tool can't detect it — judge visually: stable lines and flat color blocks, characters with skeletal or frame-by-frame motion, common "on twos" | Character design sheet + first/last-frame generation; for precise lip/action use AE / Live2D / Spine |
| stop_motion | Stop motion | The tool can't detect it — judge visually: real materials (clay, felt, paper), jerky motion, slight flicker between frames, constant lighting on the same physical object | Prefer really shooting it (fixed camera, ~12 shots per second); AI can only approximate |

`anim_2d` / `stop_motion` are judged only by visual sources: if only one party has looked, the conclusion is marked "to be confirmed"; the mark is removed only when both the VLM and the agent have looked.

## AI processing on live action (ai_edits)

When the base is live action or stop motion, check whether it was further processed by AI and record it in `ai_edits`; the remake plan then adds "AI processing to do after shooting" after the shooting sessions:

| kind | Type | What to look at | Remake |
|---|---|---|---|
| face_swap | Face swap | Flicker at the face edge and hairline, face/neck skin-tone or lighting mismatch, features drifting in profile | R12 video-edit model person replacement |
| lip_sync | Lip sync / dialogue change | Lip shape and jaw don't follow, blurry teeth, only the mouth region differs in quality | R13 lip re-dubbing |
| restyle | Full-segment stylistic re-render | The motion is a real person's, but the picture is in an anime/oil-painting/clay style, with texture wandering between frames | R12 video-edit model |
| outfit_swap | AI outfit swap | Clothing texture flicker, smearing where it meets the arms | R05 try-on image + video |
| bg_replace | Matting / background replacement | Halo or jaggies at hair edges, person/background light directions disagree, background perspective wrong | Green-screen keying, or R12 |
| object_edit | Object added/removed/replaced | Object-edge flicker, missing shadows | R12 |
| beautify | Beauty filter / face slimming | Over-smoothed skin, straight background lines bending near the face | Beauty filters in apps like Jianying (CapCut) |

## Judgment quick-reference

| Phenomenon | Points to |
|---|---|
| Adjacent frames repeat pixel-for-pixel, no change head-to-tail | Static frame; if it's a flat-shaded render card, classify as code render |
| The whole frame scales/translates by one rigid transform, no residue after compensation, and **no** frame-rate trace of a 24fps source | Still-image pan-and-zoom |
| Many flat color blocks, few colors, many straight horizontal/vertical edges | Render (code or 3D); background pixels completely unchanged frame to frame with only local motion → 2D code motion graphics |
| ~20% of frames duplicated, period 4–6 (24→30) | Source is 24fps: AI-generated / 3D / film material, not native phone footage |
| Only sharpness rises and falls periodically, no duplicated frames (frame interpolation) | Weak evidence: both interpolation and recompression produce this; confirm visually |
| Native ≥48fps with no duplication and no interpolation period | Mostly phone/camera live action |
| Obvious sensor noise and temporal noise, handheld shake | Live action |
| Platform-transcoded file: whole film native 30fps, live-action-class shots have no duplicated frames | Leans phone live action (after transcoding, noise evidence is void; go by frame rate) |
| Almost no color, a flat picture using single-digit colors | UI/document motion graphics (code render), not 3D |
| On a near-black background the bright parts are almost all fine specks or thin lines, no continuous lit surfaces | Particle/point-cloud/wireframe graphics (code render), not a 3D solid, AI, or night live action |
| Almost no fine texture in the whole picture: smooth color gradients, large saturated flat colors, glow on dark, or rainbow color fields | Code-drawn gradient/vector/shader picture, not a 3D render (3D has material textures like fabric and wood grain); same even if the whole frame moves |
| Music fills the whole film, the voice is singing (much sustained pitch) | Music MV → the song is most likely AI-generated |
| Narration speaking + BGM underneath | Ordinary score → leans stock library (to be confirmed; AI workflows often use Suno) |
| Noise floor jumps at cuts | The sound travels with the clips: AI video with native audio, or live-action sync sound |
| File carries a GB 45438 AIGC implicit marker, Label=1 | Declared AI-generated (this only states the whole film was declared; judge individual shots one by one) |
| Lots of small-size text inside a light-colored panel | An embedded UI screenshot → real material |
| Loud, pitched sound still present in the gaps between voice | BGM underneath |
| Large near-black areas but with grain, uneven highlights, and faces | Night/low-light live action (flat blocks from transcoding crushing shadows are not a render feature) |
| Face occupies ≥6% of the frame, present the whole shot, speaking | Close-up live action or digital human; flat blocks on walls/clothing don't count as render evidence |

## Confusable pairs (check item by item during review)

**Live action vs. AI video**
- Live action: noise grain changes per frame; hands, text, and distant people look normal; physics is correct (fabric, liquids, collisions).
- AI: skin and lighting too perfect; background people or text garbled; object edges "boil"; motion drifts slowly; the end of a shot tends to freeze.
- Frame rate: 24fps source (AI/film) vs. 60fps native (phone). Note AI interpolated to 60fps leaves a sharpness period, `sharp_period_ac>0.45`.
- The deterministic layer is weakest on this pair — **you must combine the VLM and your own frame inspection**.

**Cartoon-3D-style AI video vs. real 3D render**
- Real 3D: geometry and materials stable frame to frame, hair and fabric move physically, can loop precisely, many flat blocks, few colors.
- AI: the same object deforms slightly within a shot, texture flickers, noise looks photographic (colors used >100).
- Many "3D cartoon" accounts on Douyin are AI-generated, but without a marker you can only state a leaning.

**Dark-background particle graphics vs. 3D render vs. AI video / night live action**
- Particle graphics (code render): organs, bodies, the Earth, molecules, etc. built from thousands of glowing points or thin lines, with no continuous lit surface; often with a chapter card in the top-left, leader-line annotations, and ticking numbers. Three.js and AE Plexus / Trapcode can all make these; remake via a code project.
- 3D render: continuous surface shading, materials, and shadows.
- Night live action / AI: bright parts are objects and light spots with shading transitions, plus grain or deformation.
- During review, the `description` must state clearly what shape the particles form in each shot, the colors, and how they move (particle flow direction, morphing, push-in/orbit), and where the annotations and numbers are; the shot-by-shot table in the report's "Code compositing" section uses exactly this. Writing just "particle background" remakes into a blob of light spots.

**Code-drawn gradients / glows / color fields vs. 3D render**
- Code picture: almost no fine texture anywhere — only smooth gradients, flat color blocks, glows, and text; common forms are gradient light-spot backgrounds, frosted-glass cards, neon text, CSS 3D flipping cards, fractal zooms, and plasma shaders. Even if the whole frame moves (background drifting, glow breathing), it's a code render.
- 3D render: objects have material textures (fabric, wood grain, metal, plastic grain), cast shadows, and inter-object lighting relations.
- A flat poster with film grain added: once the grain is removed it's flat color blocks, so it counts as code render; when the grain is heavy (the tool measures noise σ≥3) the tool may not see through it — judge visually.
- A smooth gradient slowly changing color is easily mistaken for a cross-dissolve; the tool excludes this by "whether the change speed is steady"; during review, if one continuous background animation is still cut into multiple shots, treat it as one shot.

**Code render vs. screen capture/screenshot**
- Code render: large type, brand colors, crisp vectors, elements animate in.
- Screenshot: light background, dense small text, UI controls (buttons, icons, navigation), often scaled or scrolled as a whole.
- A screenshot embedded in a template: the base counts as code render, and the screenshot is listed separately under "real material".

**How to write the description for code-render shots**
- The "per-shot motion timeline" in the report's "Code compositing" section is measured by the tool: each element's position, appearance time, direction, easing curve, and color values; elements appearing in sequence are merged into one "interval X s" entry; the keyframe strip is `shots/shot_XXX_strip.jpg`, and the element screenshots and numbered collage are `shots/shot_XXX_elements.jpg`.
- Against those, write in the `description`, by number, what each element is ("1–12: rounded icon cards, popping in one by one"); don't repeat the measured values.

**Still-image pan-and-zoom vs. AI video's slow push-in**
- Pan-and-zoom: rendered by the editing software at the timeline frame rate, every frame differs, no 24→30 duplication pattern.
- AI push-in: carries the duplicated-frame pattern of a 24fps source, and the subject often has subtle motion (breathing, blinking).

**2D animation vs. code motion graphics vs. AI animation-style video**
- 2D animation: characters and performance, stable lines, frame-precise, often on twos (changes only every two frames).
- Code motion graphics: text, graphics, and UI entrances and easing; no character performance.
- AI animation style: lines wander between frames, details deform, 24fps source traces.

**Stop motion vs. AI video vs. live action**
- Stop motion: the same physical object nudged frame by frame, constant lighting, slight flicker and jerkiness between frames, fingerprints and frayed edges on materials.
- AI imitating stop motion: the material itself changes between frames (clay texture drifts), no real jerky rhythm.
- The tool often judges stop motion as AI (similar frame-rate patterns); when reviewing, focus on whether the material is stable.

**Static frame: AI image vs. real photo vs. render card**
- Render card (flat-shaded, few colors) → classify as code render.
- AI images and real photos can't be distinguished at the deterministic layer; hand them to the VLM; if it can't be judged, write "image material (real/AI to be confirmed)".

## Cuts

- Hard cut: a spike in histogram distance and pixel difference, with the changed area over 25%. Element pop-ins don't count as cuts.
- Cross-dissolve: the middle frame is a linear blend of the end frames (α in 0.2–0.8, residual <0.2), with optical flow used to exclude pan-and-zoom motion.
- Fade in/out: brightness drops to extremely dark or bright and comes back.
- MG beats: inside a long shot, "hold → animation → hold", where the two holds differ in content by more than 12%, is recorded as an in-shot beat, not a cut.

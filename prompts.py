"""Default system prompts used when generating photoshoot images.

These are editable from the UI and sent along with the dress reference photos
to the image model. Each block below renders as its own textarea in the UI.
"""

GARMENT_PROMPT = """GARMENT TRANSFER (STRICT — NO CHANGE)
Preserve 100% of the original design, print placement, stitching, proportions, and fabric.
Maintain exact:
- Kurta cut, neckline, sleeve length
- Trouser style and side border detail
- Dupatta print, border, and placement
Fabric must show natural drape, gravity, and realistic stitching.

CROSS-VIEW CONSISTENCY
The front, back, and side images are the SAME dress from different angles.
Colors, prints, embroidery, borders, trims, fabric, and proportions must be
IDENTICAL across all three views. Do not invent variations or drift between shots.

FABRIC CONDITION — ZERO WRINKLES (CRITICAL)
The garment must appear FRESHLY IRONED, CRISP, and FLAWLESSLY PRESSED on the model.
This is retail-ready editorial quality — the outfit just came off a steam press.

STRICTLY NO:
- NO wrinkles anywhere on the outfit
- NO creases (except the intentional trouser front crease if the design has one)
- NO bunching at the waist, elbows, knees, or ankles
- NO messy folds, ruffled fabric, or crumples
- NO sag lines on sleeves or trousers
- NO puckering at stitch lines
- NO accidental dupatta crumples or twists

REQUIRED:
- Every surface of the kurta is smooth, taut, and clean
- Dupatta fabric falls cleanly and smoothly across the body
- Trousers hang smoothly from waistband to ankle
- Sleeves are crisp and unwrinkled
- Fabric looks starched and pristine, as if professionally pressed moments before the shot
- Only the most subtle physics-driven micro-folds are allowed (e.g., a faint fold at the inner elbow if the arm is bent) — and these must be minimal, never messy

Pressing and smoothing must NOT affect or alter print placement, pattern alignment, embroidery, or stitching structure.
No distortion, redesign, smoothing of print detail, or pattern shifting — the garment is pristine AND identical to the reference."""

MODEL_PROMPT = """MODEL (INFLUENCER VIBE — NATURAL, RELATABLE)
South Asian female body, mid-to-late 20s build.
Slim but natural (not overly posed).
Warm natural skin tone with slight imperfections on hands, arms, neck, and chin.
Minimal jewelry: thin layered necklace resting on the collarbone.
She is wearing heels matching the color of the dress.

CROPPING — THIS IS A HEADLESS / FACELESS FASHION SHOT (#1 PRIORITY RULE)
This photograph has NO FACE and NO HEAD in it. It is a strictly body-only lookbook image.
This is the SINGLE MOST IMPORTANT RULE of the entire prompt. Every other instruction is secondary to this.

HARD CONSTRAINTS — DO NOT VIOLATE UNDER ANY CIRCUMSTANCE:
- The TOP EDGE of the image is AT LIP LEVEL. Everything above the mouth is CUT OFF — it does NOT exist in the photo.
- The image is FACELESS. There is NO face. There is NO head. There is NO portrait.
- ABSOLUTELY DO NOT render: eyes, eyelashes, eyebrows, nose, nostrils, forehead, temples, hairline, hair on the head, top of skull, ears, cheekbones, or any facial feature located above the mouth.
- DO NOT show the upper jaw, upper lip area connecting to nose, or any anatomy that implies a face is just out of frame in a way that lets you draw it.
- DO NOT generate a full-body shot that includes the head — the head MUST be cut off by the top of the frame.
- DO NOT generate a face and then crop it; the face must NEVER be drawn in the first place.
- DO NOT show the model's face from any angle: not from the side, not from behind, not in shadow, not blurred, not pixelated, not turned away, not partially hidden. NO FACE PIXELS AT ALL.

WHAT IS ALLOWED IN THE FRAME (and ONLY this):
- A small sliver of the lower lip and chin at the very top edge of the photo (optional — may also be cropped away).
- Jawline (lower portion only, below the mouth), neck, collarbones, shoulders.
- Full torso, arms, hands, hips, legs, feet, shoes.
- The complete outfit — kurta, dupatta, trousers — and the background.

CAMERA POSITION (use this to enforce the crop):
- Frame the camera so the TOP of the picture lands on the model's mouth line.
- Imagine the model's face is physically ABOVE the photograph — outside it, not visible, not implied.
- This is identical to anonymous e-commerce fashion photography (think SSENSE, Net-a-Porter "model body" thumbnails) where the model is intentionally faceless.

VERIFICATION CHECKLIST (the output FAILS if any of these are true):
- ❌ Any eye is visible
- ❌ A nose is visible
- ❌ A forehead is visible
- ❌ Hair on the head is visible
- ❌ Two full lips with surrounding face are visible (only a thin lip sliver at the very top is allowed)
- ❌ The viewer can tell what the model's face looks like

If you cannot satisfy these constraints with the requested pose, CHANGE the framing — crop tighter, lower the camera, or zoom in — but NEVER show the face. The face rule overrides pose, composition, and every other instruction in this prompt."""

BACKGROUND_PROMPT = """BACKGROUND (REAL HOME — NOT STAGED)
Ultra-realistic lived-in luxury home interior.
Polished beige marble flooring with soft natural reflections.
Dusty rose velvet sofas (slightly used, not perfectly arranged).
Vintage grandfather clock as a subtle presence.
Walls: warm off-white.
Carpet: neutral, slightly imperfect placement.

LIGHTING
Soft natural daylight from a window on the right side.
Slightly uneven, realistic home lighting.
Soft shadows, no harsh contrast.

PHOTOGRAPHY
Shot like high-end influencer content.
Slight handheld realism.
Natural depth of field (not overly cinematic blur).
35mm–50mm lens feel.
Color grading: neutral to slightly warm."""

OUTPUT_PROMPT = """OUTPUT FRAMING
Portrait 4:5 aspect ratio.
Body-only shot: top edge at lip level, bottom edge at the floor with feet and heels visible.
Clean, visible floor beneath the feet.
The outfit is the unambiguous hero of the shot.

IMAGE QUALITY (MAXIMIZE)
Ultra-high-resolution, magazine-grade editorial fashion photography.
Razor-sharp focus on garment fabric, stitching, embroidery, and print detail.
Rich natural color depth, real-camera micro-contrast, subtle film-like grain.
Crisp textile rendering — visible weave, print crispness, clean stitch lines.
No plastic skin, no AI smoothing, no painted look, no artificial glow.
Photoreal only. 8K-equivalent detail in fabric and shoes."""

# Per-angle prompt blocks. The UI shows these as three editable textareas and
# sends the relevant one as the `pose` field when generating each shot.
ANGLE_FRONT = """ANGLE: FRONT
Model faces the camera directly (square to the lens), body open.
Pose: both hands lightly adjusting the dupatta at front — one hand near the shoulder, one near the waist. Posture relaxed, slight lean on one leg, candid mid-adjustment feel.
Show the full front of the outfit: kurta neckline, front print, sleeve fall, dupatta placement across the chest, trouser front."""

ANGLE_BACK = """ANGLE: BACK
Model is turned with her BACK to the camera. Head is turned away from the lens (and in any case, no face is in the frame).
Pose: standing with weight on one leg, one hand loosely holding the dupatta behind, other hand relaxed at her side. Slight contrapposto.
Show the full back of the outfit: back neckline cut, kurta back panel, dupatta drape behind the shoulders, trouser back, heel detail."""

ANGLE_SIDE = """ANGLE: SIDE
Model is in a clean 90-degree side profile to the camera.
Pose: weight on the back leg, front leg slightly forward, dupatta flowing naturally along the side, one hand lightly grazing the kurta side seam, the other relaxed.
Show the full side silhouette: kurta side panel and side slit, dupatta length, trouser side border, shoe profile."""

ANGLES = {
    "front": ANGLE_FRONT,
    "back": ANGLE_BACK,
    "side": ANGLE_SIDE,
}


DESIGN_CONSISTENCY_EMPHASIS = (
    "============================================================\n"
    "ABSOLUTE RULE — GARMENT DESIGN CONSISTENCY ACROSS ALL VIEWS\n"
    "============================================================\n"
    "The provided reference images are the SAME physical garment photographed from "
    "different angles (front / back / side). When generating any angle, you MUST "
    "render the EXACT SAME dress with IDENTICAL design details:\n"
    "- IDENTICAL fabric color, shade, and saturation (no drift between views)\n"
    "- IDENTICAL print pattern, motif scale, and placement\n"
    "- IDENTICAL embroidery placement, density, and stitching detail\n"
    "- IDENTICAL neckline shape, sleeve length, cuff detail, hem length\n"
    "- IDENTICAL dupatta print, border, pallu detail, and drape length\n"
    "- IDENTICAL trouser cut, side border, ankle detail, and waistband\n"
    "- IDENTICAL material weight, weave, sheen, and texture\n"
    "- IDENTICAL buttons, ties, tassels, lace, piping, zippers, and all trims\n"
    "\n"
    "DO NOT:\n"
    "- Invent design variations not shown in the references\n"
    "- Shift, rescale, or relocate prints / motifs between angles\n"
    "- Change embroidery shape or position between angles\n"
    "- Change fabric color, shade, or saturation between angles\n"
    "- Add details absent from the references\n"
    "- Remove details present in the references\n"
    "- Replace any part of the outfit with a different design\n"
    "\n"
    "When rendering the BACK angle: use the BACK reference image to copy the exact "
    "back-panel design. When rendering the SIDE angle: use the SIDE reference to copy "
    "the exact side silhouette. If a specific angle reference is missing, INFER the "
    "unseen side from the adjacent references while keeping color, print, and material "
    "IDENTICAL — never invent new ornamentation.\n"
    "\n"
    "This is ONE dress shown from multiple angles. Every generated view must look "
    "like the same physical garment photographed moments apart."
)


FACE_CROP_EMPHASIS = (
    "============================================================\n"
    "ABSOLUTE #1 RULE — NO FACE, NO HEAD, FACELESS IMAGE ONLY\n"
    "============================================================\n"
    "This image MUST be FACELESS and HEADLESS. There is NO FACE in this photograph. "
    "The model's HEAD IS NOT IN THE FRAME. The TOP EDGE of the photo cuts across the MOUTH.\n"
    "\n"
    "STRICTLY FORBIDDEN — DO NOT RENDER ANY OF THESE:\n"
    "- NO eyes. NO eyelashes. NO eyebrows.\n"
    "- NO nose. NO nostrils.\n"
    "- NO forehead. NO temples. NO hairline.\n"
    "- NO hair on the head. NO scalp. NO top of head. NO skull.\n"
    "- NO ears.\n"
    "- NO upper cheeks. NO cheekbones.\n"
    "- NO full face from any angle (front, side, back, blurred, shadowed, pixelated, turned away — NONE).\n"
    "- NO portrait. NO headshot. NO half-face. NO three-quarter face.\n"
    "- NO implied face just above the frame edge with smooth-skin transition that could be mistaken for a chin/face.\n"
    "\n"
    "STRICTLY ALLOWED — ONLY these body parts may appear:\n"
    "- A thin sliver of the lower lip and chin at the very top edge (or no lips at all — both are fine).\n"
    "- Lower jawline, neck, collarbones, shoulders, torso, arms, hands, hips, legs, feet, shoes.\n"
    "- The outfit and the background.\n"
    "\n"
    "FRAMING INSTRUCTION:\n"
    "Position the camera so the TOP of the frame lands ON THE MOUTH LINE. "
    "The model's face exists ABOVE the photograph — physically outside it, completely invisible. "
    "Treat this exactly like SSENSE / Net-a-Porter / Zara anonymous body-only e-commerce thumbnails: "
    "deliberately faceless by framing, where the OUTFIT is the subject and the model is anonymous.\n"
    "\n"
    "FAILURE DEFINITION:\n"
    "If even ONE of {eye, nose, forehead, eyebrow, hair on head, ear, full lips with surrounding face} is visible, "
    "the output is a FAILURE and must be re-composed. The face rule OVERRIDES every other instruction in this prompt — "
    "pose, composition, lighting, garment display — all of them are SECONDARY to keeping the face out of the image.\n"
    "============================================================"
)


def build_reference_key(angles: list[str]) -> str:
    """Describe which reference image corresponds to which view.

    `angles` is an ordered list like ["front", "back", "side"] matching the
    order the reference files are sent to the image model.
    """
    if not angles:
        return ""
    lines = []
    for i, a in enumerate(angles):
        if a in ("front", "back", "side"):
            lines.append(f"- Reference image #{i + 1}: {a.upper()} view of the IDENTICAL garment")
    if not lines:
        return ""
    return (
        "REFERENCE IMAGE KEY — USE THESE TO LOCK DESIGN DETAILS ACROSS ANGLES:\n"
        + "\n".join(lines)
        + "\nWhen generating an angle that has a matching reference, COPY that reference's design "
        "EXACTLY — same colors, prints, embroidery, borders, and stitching. When generating an angle "
        "without its own reference, INFER it from the adjacent references while keeping every design "
        "element identical; do NOT invent new motifs or trims."
    )


def build_prompt(
    garment: str,
    model: str,
    background: str,
    output: str,
    pose: str,
    reference_key: str = "",
) -> str:
    """Assemble the final prompt sent to the image model for a single shot.

    `pose` receives the angle-specific block (front / back / side) that the UI
    sends per generation. `reference_key` is an optional mapping of reference
    image index → angle, injected near the top so the model knows which
    reference is which.
    """
    ref_block = f"{reference_key}\n\n" if reference_key else ""
    return (
        f"{FACE_CROP_EMPHASIS}\n\n"
        f"{DESIGN_CONSISTENCY_EMPHASIS}\n\n"
        f"{ref_block}"
        "Ultra-realistic Instagram influencer-style FACELESS body-only fashion photo of a South Asian female model "
        "wearing the exact outfit from the provided mannequin reference images. "
        "The photograph is FRAMED FROM THE LIPS DOWN ONLY. The face, head, eyes, nose, forehead, and hair are "
        "NOT in the image. The image starts at mouth level and extends down to the feet. "
        "This is a headless lookbook shot — the OUTFIT is the subject, the model is anonymous by framing. "
        "The outfit in this image is IDENTICAL in every detail to the provided references.\n\n"
        f"{garment}\n\n"
        f"{model}\n\n"
        f"{pose}\n\n"
        f"{background}\n\n"
        f"{output}\n\n"
        f"{DESIGN_CONSISTENCY_EMPHASIS}\n\n"
        f"{FACE_CROP_EMPHASIS}\n\n"
        "FINAL REMINDER BEFORE GENERATION:\n"
        "1. NO FACE — the image must be faceless, framed from the lips down only.\n"
        "2. IDENTICAL DRESS — the garment must exactly match the reference images in every design detail.\n"
        "If either rule would be violated, re-compose the image until BOTH rules are satisfied."
    )


DEFAULTS = {
    "garment": GARMENT_PROMPT,
    "model": MODEL_PROMPT,
    "background": BACKGROUND_PROMPT,
    "output": OUTPUT_PROMPT,
    "angles": ANGLES,
}

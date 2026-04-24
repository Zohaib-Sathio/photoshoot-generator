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

FABRIC CONDITION (CRITICAL)
Garment must be neatly pressed and well-prepared:
- Clean, crisp, and freshly ironed
- No unwanted wrinkles, creases, or messy folds
- Only subtle natural micro-folds where required by body movement
Pressing must NOT affect or change print placement, pattern alignment, embroidery, or stitching structure.
No distortion, redesign, smoothing, or pattern shifting."""

MODEL_PROMPT = """MODEL (INFLUENCER VIBE — NATURAL, RELATABLE)
South Asian female body, mid-to-late 20s build.
Slim but natural (not overly posed).
Warm natural skin tone with slight imperfections on hands, arms, neck, and chin.
Minimal jewelry: thin layered necklace resting on the collarbone.
She is wearing heels matching the color of the dress.

CROPPING — THIS IS A HEADLESS / FACELESS FASHION SHOT
This photograph has NO FACE and NO HEAD in it. It is a body-only lookbook image.
- The TOP EDGE of the frame sits AT LIP LEVEL. Everything above the mouth is OUTSIDE the photo.
- No eyes, no nose, no forehead, no eyebrows, no hairline, no ears, no top of head, no cheeks above the mouth.
- Do NOT generate a full face. Do NOT generate a portrait. Do NOT draw facial features above the mouth.
- What IS visible at the top of the frame: a sliver of lips and chin only.
- Treat this like high-end e-commerce fashion photography where the subject is deliberately anonymous by framing — the OUTFIT is the hero, the person is only a body below the lips.
If the pose would naturally show the face, CROP TIGHTER or LOWER the camera — never include the face."""

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


FACE_CROP_EMPHASIS = (
    "ABSOLUTE COMPOSITION RULE — READ FIRST, APPLY LAST:\n"
    "This image is a HEADLESS, FACELESS fashion lookbook photograph. "
    "NO face, NO head, NO facial features appear anywhere in the output. "
    "The TOP EDGE of the frame cuts across the MOUTH — only a sliver of lips and chin is visible at the top. "
    "Forbidden in the image: eyes, nose, forehead, eyebrows, hairline, ears, top of head, full face, portrait framing. "
    "Allowed in the image: partial lips, chin, jawline, neck, shoulders, torso, arms, hands, hips, legs, feet, outfit, background. "
    "Think of this as anonymous high-end e-commerce fashion photography: the outfit is the subject, "
    "the person is deliberately made anonymous by cropping the camera at the mouth line. "
    "If any pose or composition choice would bring the face into the frame, crop tighter or lower the camera — "
    "the face rule overrides every other instruction."
)


def build_prompt(
    garment: str,
    model: str,
    background: str,
    output: str,
    pose: str,
) -> str:
    """Assemble the final prompt sent to the image model for a single shot.

    `pose` here receives the angle-specific block (front / back / side) that
    the UI sends per generation.
    """
    return (
        f"{FACE_CROP_EMPHASIS}\n\n"
        "Ultra-realistic Instagram influencer-style fashion photo of a South Asian female model "
        "wearing the exact outfit from the provided mannequin reference images. "
        "The photograph is framed from the LIPS DOWN ONLY — the face is not in the image.\n\n"
        f"{garment}\n\n"
        f"{model}\n\n"
        f"{pose}\n\n"
        f"{background}\n\n"
        f"{output}\n\n"
        f"{FACE_CROP_EMPHASIS}"
    )


DEFAULTS = {
    "garment": GARMENT_PROMPT,
    "model": MODEL_PROMPT,
    "background": BACKGROUND_PROMPT,
    "output": OUTPUT_PROMPT,
    "angles": ANGLES,
}

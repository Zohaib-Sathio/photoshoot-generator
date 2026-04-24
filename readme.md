system workflow:
i need to create a page where we will upload images of the dresses, we need to     
generate photoshoot images of those dresses.
we will uploaded 2 to 5 photos of the dress with different angles, front, back, side etc...
now you need to put those dresses on a model to showcase the dress with elegant background.
about the model; we only need photoshoot image of the model upto her lips, we dont want to show the face in the photo.

design the system ui, where i can select add dress to upload pictures of the dress in mannequin, if i need to add multiple dresses i can click on add dress and i can upload images of the dress separately, so that all are separate and we will generate images of the dress separately.

also there should be fields where we can see the system prompt related to background, dress and model, basically all relevant instructions which produce the best results. each image should have slighly different pose.

after selecting the images of the dresses i can start the process step and at the end we should be able to download the newly generated images.

here is some inspiration for the image generation prompt, you can add more instructions to enhance the image production quality.

{Ultra-realistic Instagram influencer-style fashion photo of a South Asian female model wearing the exact outfit from the provided mannequin image.
GARMENT TRANSFER (STRICT — NO CHANGE)
Preserve 100% original design, print placement, stitching, proportions, and fabric
Maintain exact:
Kurta cut, neckline, sleeve length
Trouser style and side border detail
Dupatta print, border, and placement
Fabric must show natural drape, gravity, and realistic stitching
FABRIC CONDITION (CRITICAL ADDITION):
 Garment must be neatly pressed and well-prepared:
Fabric appears clean, crisp, and freshly ironed
No unwanted wrinkles, creases, or messy folds
Only subtle, natural micro-folds where required by body movement
IMPORTANT:
 Pressing must NOT affect or change:
print placement
pattern alignment
embroidery
stitching structure
she should be wearing heels matching with the color of the dress.
No distortion, redesign, smoothing, or pattern shifting
MODEL (INFLUENCER VIBE — NATURAL, RELATABLE)
South Asian female, mid-to-late 20s
 Slim but natural (not overly posed)
 Warm natural skin tone with slight imperfections
Hair in slightly loose low bun (few natural flyaways)
Minimal jewelry:
small gold studs
thin layered necklace
Makeup: soft, everyday influencer look
CROPPING (STRICT)
Frame from lips down only
 No eyes, nose, forehead
POSE
Both hands lightly adjusting dupatta at front (one near shoulder, one near waist), posture relaxed, slight lean on one leg — candid mid-adjustment feel
BACKGROUND (REAL HOME — NOT STAGED)
Ultra-realistic lived-in luxury home interior
Polished beige marble flooring with soft natural reflections
Dusty rose velvet sofas (slightly used, not perfectly arranged)
Vintage grandfather clock (subtle presence)
Walls: warm off-white
 Carpet: neutral, slightly imperfect placement
LIGHTING
Soft natural daylight from window (right side)
 Slightly uneven, realistic home lighting
 Soft shadows, no harsh contrast
PHOTOGRAPHY
Shot like high-end influencer content
Slight handheld realism
Natural depth of field (not overly cinematic blur)
35mm–50mm lens feel
Color grading: neutral to slightly warm
OUTPUT
Portrait (4:5)
 Full body (lips to feet)
 Clean floor visible
Outfit is the clear hero}


for image generation, usage openai's images 2.0 model, i will upload the api key in .env file. https://developers.openai.com/api/docs/models/gpt-image-2

s
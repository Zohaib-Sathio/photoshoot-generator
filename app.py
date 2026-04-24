"""FastAPI backend for the photoshoot generator.

Endpoints:
    GET  /api/defaults              -> default prompt blocks + pose library
    POST /api/generate              -> generate one photoshoot image
    GET  /outputs/{job}/{filename}  -> serve a generated image
    GET  /outputs/{job}.zip         -> download all images from a job as ZIP
    GET  /                          -> static UI
"""
from __future__ import annotations

import io
import json
import shutil
import uuid
import zipfile
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import prompts
from image_generator import DEFAULT_PROVIDER, generate_photoshoot


load_dotenv()

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15 MB per image
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


app = FastAPI(title="Photoshoot Generator")


@app.get("/api/defaults")
def defaults() -> JSONResponse:
    return JSONResponse({**prompts.DEFAULTS, "provider": DEFAULT_PROVIDER})


@app.post("/api/generate")
async def generate(
    dress_name: str = Form(...),
    pose: str = Form(...),
    garment_prompt: str = Form(...),
    model_prompt: str = Form(...),
    background_prompt: str = Form(...),
    output_prompt: str = Form(...),
    shot_index: int = Form(0),
    job_id: str = Form(""),
    provider: str = Form("gemini"),
    angle: str = Form("front"),
    references: List[UploadFile] = File(...),
) -> JSONResponse:
    if provider not in {"gemini", "openai"}:
        raise HTTPException(400, f"Unsupported provider: {provider}")
    if angle not in {"front", "back", "side"}:
        raise HTTPException(400, f"Unsupported angle: {angle}")
    if not references:
        raise HTTPException(400, "At least one reference image is required.")
    if len(references) > 5:
        raise HTTPException(400, "Maximum 5 reference images per dress.")

    job = job_id or uuid.uuid4().hex[:12]
    job_dir = OUTPUT_DIR / job
    job_dir.mkdir(exist_ok=True)

    ref_dir = UPLOAD_DIR / job / _slug(dress_name) / angle
    ref_dir.mkdir(parents=True, exist_ok=True)

    ref_paths: list[Path] = []
    for idx, up in enumerate(references):
        ext = Path(up.filename or "").suffix.lower() or ".png"
        if ext not in ALLOWED_EXTS:
            raise HTTPException(400, f"Unsupported file type: {ext}")
        body = await up.read()
        if len(body) > MAX_UPLOAD_BYTES:
            raise HTTPException(400, f"Image too large: {up.filename}")
        dest = ref_dir / f"ref_{idx:02d}{ext}"
        dest.write_bytes(body)
        ref_paths.append(dest)

    final_prompt = prompts.build_prompt(
        garment=garment_prompt,
        model=model_prompt,
        background=background_prompt,
        output=output_prompt,
        pose=pose,
    )

    try:
        png_bytes = generate_photoshoot(ref_paths, final_prompt, provider=provider)  # type: ignore[arg-type]
    except Exception as e:
        raise HTTPException(500, f"Image generation failed: {e}") from e

    filename = f"{_slug(dress_name)}_{angle}.png"
    out_path = job_dir / filename
    out_path.write_bytes(png_bytes)

    return JSONResponse(
        {
            "job_id": job,
            "dress": dress_name,
            "angle": angle,
            "shot_index": shot_index,
            "filename": filename,
            "url": f"/outputs/{job}/{filename}",
            "prompt": final_prompt,
        }
    )


@app.post("/api/refine")
async def refine(
    job_id: str = Form(...),
    dress_name: str = Form(...),
    angle: str = Form(...),
    provider: str = Form("gemini"),
    base_prompt: str = Form(...),
    extra_instructions: str = Form(...),
) -> JSONResponse:
    """Re-generate a previously generated image with additional user instructions.

    Uses the references already stored on disk from the original generation so
    the client doesn't need to re-upload.
    """
    if provider not in {"gemini", "openai"}:
        raise HTTPException(400, f"Unsupported provider: {provider}")
    if angle not in {"front", "back", "side"}:
        raise HTTPException(400, f"Unsupported angle: {angle}")
    extra = (extra_instructions or "").strip()
    if not extra:
        raise HTTPException(400, "Extra instructions are empty.")

    ref_dir = UPLOAD_DIR / job_id / _slug(dress_name) / angle
    if not ref_dir.is_dir():
        raise HTTPException(404, "Original references not found for this image.")
    ref_paths = sorted(ref_dir.glob("ref_*"))
    if not ref_paths:
        raise HTTPException(404, "No reference images on disk for this job.")

    final_prompt = (
        f"{base_prompt}\n\n"
        "ADDITIONAL USER INSTRUCTIONS — APPLY ON TOP OF EVERYTHING ABOVE "
        "(these are higher priority than the defaults, except the face-crop rule):\n"
        f"{extra}\n\n"
        f"{prompts.FACE_CROP_EMPHASIS}"
    )

    try:
        png_bytes = generate_photoshoot(ref_paths, final_prompt, provider=provider)  # type: ignore[arg-type]
    except Exception as e:
        raise HTTPException(500, f"Image refinement failed: {e}") from e

    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    base_slug = _slug(dress_name)
    existing = list(job_dir.glob(f"{base_slug}_{angle}_refined*.png"))
    n = len(existing) + 1
    filename = f"{base_slug}_{angle}_refined{n:02d}.png"
    out_path = job_dir / filename
    out_path.write_bytes(png_bytes)

    return JSONResponse(
        {
            "job_id": job_id,
            "dress": dress_name,
            "angle": angle,
            "filename": filename,
            "url": f"/outputs/{job_id}/{filename}",
            "prompt": final_prompt,
            "refined": True,
            "refine_index": n,
        }
    )


@app.get("/outputs/{job}/{filename}")
def get_output(job: str, filename: str) -> FileResponse:
    path = OUTPUT_DIR / job / filename
    if not path.is_file():
        raise HTTPException(404, "Not found")
    return FileResponse(path)


@app.get("/outputs/{job}.zip")
def get_output_zip(job: str) -> StreamingResponse:
    job_dir = OUTPUT_DIR / job
    if not job_dir.is_dir():
        raise HTTPException(404, "Job not found")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(job_dir.glob("*.png")):
            zf.write(f, arcname=f.name)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="photoshoot_{job}.zip"'},
    )


def _slug(s: str) -> str:
    keep = [c if c.isalnum() or c in "-_" else "_" for c in s.strip()]
    slug = "".join(keep).strip("_") or "dress"
    return slug[:40]


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

"""Image generation backends.

Two providers are supported and selected per request:
    - "gemini" : Google Gemini 2.5 Flash Image ("nano banana"). Default.
    - "openai" : OpenAI gpt-image-2 (requires verified org).

Both return PNG/JPEG bytes given a prompt and a list of reference images.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Iterable, Literal


Provider = Literal["gemini", "openai"]
DEFAULT_PROVIDER: Provider = os.getenv("IMAGE_PROVIDER", "gemini")  # type: ignore[assignment]


def generate_photoshoot(
    reference_paths: Iterable[str | Path],
    prompt: str,
    provider: Provider = DEFAULT_PROVIDER,
) -> bytes:
    paths = [Path(p) for p in reference_paths]
    if not paths:
        raise ValueError("At least one reference image is required.")

    if provider == "gemini":
        return _generate_gemini(paths, prompt)
    if provider == "openai":
        return _generate_openai(paths, prompt)
    raise ValueError(f"Unknown image provider: {provider}")


# ------------------------------------------------------------------
# Gemini (google-genai) — gemini-2.5-flash-image
# ------------------------------------------------------------------
def _generate_gemini(paths: list[Path], prompt: str) -> bytes:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY (or GOOGLE_API_KEY) is not set. Add it to your .env file."
        )

    from google import genai
    from PIL import Image

    # "Nano Banana Pro" = gemini-3-pro-image-preview. Higher fidelity and
    # stronger instruction-following than the 2.5 flash image model.
    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")
    client = genai.Client(api_key=api_key)

    images = [Image.open(p) for p in paths]
    contents: list = [prompt, *images]

    response = client.models.generate_content(model=model, contents=contents)

    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        feedback = getattr(response, "prompt_feedback", None)
        raise RuntimeError(
            f"Gemini returned no candidates. Prompt feedback: {feedback}"
        )

    for part in candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline and getattr(inline, "data", None):
            data = inline.data
            if isinstance(data, str):
                return base64.b64decode(data)
            return bytes(data)

    text_parts = [
        getattr(p, "text", "") for p in candidates[0].content.parts if getattr(p, "text", None)
    ]
    raise RuntimeError(
        "Gemini response did not contain an image. "
        f"Text returned: {' '.join(text_parts)[:300] or '(none)'}"
    )


# ------------------------------------------------------------------
# OpenAI — gpt-image-2 / gpt-image-1
# ------------------------------------------------------------------
def _generate_openai(paths: list[Path], prompt: str) -> bytes:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env file.")

    from openai import OpenAI

    model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")
    size = os.getenv("OPENAI_IMAGE_SIZE", "1024x1536")
    quality = os.getenv("OPENAI_IMAGE_QUALITY", "high")
    client = OpenAI(api_key=api_key)

    open_files = [open(p, "rb") for p in paths]
    try:
        result = client.images.edit(
            model=model,
            image=open_files,
            prompt=prompt,
            size=size,
            n=1,
            quality=quality,
        )
    finally:
        for f in open_files:
            try:
                f.close()
            except Exception:
                pass

    data = result.data[0]
    if getattr(data, "b64_json", None):
        return base64.b64decode(data.b64_json)
    url = getattr(data, "url", None)
    if url:
        import urllib.request

        with urllib.request.urlopen(url) as resp:
            return resp.read()
    raise RuntimeError("OpenAI image response contained neither b64_json nor url.")

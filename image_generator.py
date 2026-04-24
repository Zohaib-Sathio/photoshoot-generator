"""Image generation backends with token-usage + cost accounting.

Two providers are supported and selected per request:
    - "gemini" : Google Gemini 3 Pro Image Preview (Nano Banana Pro). Default.
    - "openai" : OpenAI gpt-image-2 (requires verified org).

generate_photoshoot() returns (png_bytes, meta_dict). `meta_dict` contains
provider, model, token breakdown, and computed USD cost.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Iterable, Literal


Provider = Literal["gemini", "openai"]
DEFAULT_PROVIDER: Provider = os.getenv("IMAGE_PROVIDER", "gemini")  # type: ignore[assignment]


# -------------------------------------------------------------------
# Gemini pricing (USD per 1M tokens, Google AI Studio / Gemini API).
# Nano Banana Pro = gemini-3-pro-image-preview.
#   input text + input image : $2.00 / 1M
#   output text / thinking   : $12.00 / 1M
#   output image             : $120.00 / 1M
# -------------------------------------------------------------------
GEMINI_PRICE = {
    "input": 2.0,
    "output_text": 12.0,
    "output_image": 120.0,
}


def generate_photoshoot(
    reference_paths: Iterable[str | Path],
    prompt: str,
    provider: Provider = DEFAULT_PROVIDER,
) -> tuple[bytes, dict]:
    paths = [Path(p) for p in reference_paths]
    if not paths:
        raise ValueError("At least one reference image is required.")

    if provider == "gemini":
        return _generate_gemini(paths, prompt)
    if provider == "openai":
        return _generate_openai(paths, prompt)
    raise ValueError(f"Unknown image provider: {provider}")


# ------------------------------------------------------------------
# Gemini (google-genai) — gemini-3-pro-image-preview (Nano Banana Pro)
# ------------------------------------------------------------------
def _generate_gemini(paths: list[Path], prompt: str) -> tuple[bytes, dict]:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY (or GOOGLE_API_KEY) is not set. Add it to your .env file."
        )

    from google import genai
    from PIL import Image

    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")
    image_size = os.getenv("GEMINI_IMAGE_SIZE", "2K")      # "512" | "1K" | "2K" | "4K"
    aspect_ratio = os.getenv("GEMINI_ASPECT_RATIO", "4:5")

    client = genai.Client(api_key=api_key)
    images = [Image.open(p) for p in paths]
    contents: list = [prompt, *images]

    response = None
    # Try the modern GenerateContentConfig path with image_config set to 2K 4:5.
    try:
        from google.genai import types

        cfg = types.GenerateContentConfig(
            image_config=types.ImageConfig(
                image_size=image_size,
                aspect_ratio=aspect_ratio,
            )
        )
        response = client.models.generate_content(model=model, contents=contents, config=cfg)
    except Exception:
        # Older SDK or unsupported fields — retry without image_config.
        response = client.models.generate_content(model=model, contents=contents)

    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        feedback = getattr(response, "prompt_feedback", None)
        raise RuntimeError(f"Gemini returned no candidates. Prompt feedback: {feedback}")

    image_bytes: bytes | None = None
    text_parts: list[str] = []
    for part in candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline and getattr(inline, "data", None):
            data = inline.data
            image_bytes = base64.b64decode(data) if isinstance(data, str) else bytes(data)
            break
        if getattr(part, "text", None):
            text_parts.append(part.text)

    if not image_bytes:
        raise RuntimeError(
            "Gemini response did not contain an image. "
            f"Text returned: {' '.join(text_parts)[:300] or '(none)'}"
        )

    meta = _gemini_usage_meta(response, model=model, image_size=image_size, aspect_ratio=aspect_ratio)
    return image_bytes, meta


def _gemini_usage_meta(response, *, model: str, image_size: str, aspect_ratio: str) -> dict:
    meta = {
        "provider": "gemini",
        "model": model,
        "image_size": image_size,
        "aspect_ratio": aspect_ratio,
        "input_tokens": 0,
        "output_text_tokens": 0,
        "output_image_tokens": 0,
        "total_tokens": 0,
        "cost_usd": 0.0,
        "cost_breakdown": {"input": 0.0, "output_text": 0.0, "output_image": 0.0},
    }

    usage = getattr(response, "usage_metadata", None)
    if not usage:
        return meta

    input_tokens = getattr(usage, "prompt_token_count", 0) or 0
    candidates_total = getattr(usage, "candidates_token_count", 0) or 0

    text_out = 0
    image_out = 0
    details = getattr(usage, "candidates_tokens_details", None) or []
    if details:
        for d in details:
            mod = getattr(d, "modality", "")
            if hasattr(mod, "name"):
                mod = mod.name
            count = getattr(d, "token_count", 0) or 0
            if str(mod).upper() == "IMAGE":
                image_out += count
            else:
                text_out += count
    else:
        # Image-generation calls return image output as the candidate tokens.
        image_out = candidates_total

    cost_input = input_tokens * GEMINI_PRICE["input"] / 1_000_000
    cost_text = text_out * GEMINI_PRICE["output_text"] / 1_000_000
    cost_image = image_out * GEMINI_PRICE["output_image"] / 1_000_000

    meta.update(
        {
            "input_tokens": input_tokens,
            "output_text_tokens": text_out,
            "output_image_tokens": image_out,
            "total_tokens": input_tokens + text_out + image_out,
            "cost_usd": round(cost_input + cost_text + cost_image, 6),
            "cost_breakdown": {
                "input": round(cost_input, 6),
                "output_text": round(cost_text, 6),
                "output_image": round(cost_image, 6),
            },
        }
    )
    return meta


# ------------------------------------------------------------------
# OpenAI — gpt-image-2 / gpt-image-1
# No token-level usage is returned for image.edit; we return zeros and the
# client can treat cost as unavailable for this provider.
# ------------------------------------------------------------------
def _generate_openai(paths: list[Path], prompt: str) -> tuple[bytes, dict]:
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
        image_bytes = base64.b64decode(data.b64_json)
    else:
        url = getattr(data, "url", None)
        if not url:
            raise RuntimeError("OpenAI image response contained neither b64_json nor url.")
        import urllib.request

        with urllib.request.urlopen(url) as resp:
            image_bytes = resp.read()

    meta = {
        "provider": "openai",
        "model": model,
        "image_size": size,
        "aspect_ratio": None,
        "input_tokens": 0,
        "output_text_tokens": 0,
        "output_image_tokens": 0,
        "total_tokens": 0,
        "cost_usd": None,  # signal "unavailable"
        "cost_breakdown": None,
    }
    return image_bytes, meta

"""Geração via API Freepik/Magnific (assíncrona): Flux 2 Klein, GPT Image 2 Edit, upscaler."""
from __future__ import annotations

import base64
import io
import time
from pathlib import Path

import httpx
from PIL import Image

from .env import key
from .gemini import _img_part

BASE = "https://api.freepik.com/v1/ai"


def _hdr() -> dict:
    return {"x-freepik-api-key": key("MAGNIFIC_API_KEY"), "Content-Type": "application/json"}


def _b64(p: str | Path, max_side: int = 1536) -> str:
    return _img_part(p, max_side)["inline_data"]["data"]


def _task(path: str, body: dict, timeout: float = 600) -> list[str]:
    r = httpx.post(f"{BASE}/{path}", headers=_hdr(), json=body, timeout=120)
    if r.status_code >= 300:
        raise RuntimeError(f"Freepik {path} {r.status_code}: {r.text[:400]}")
    tid = r.json()["data"]["task_id"]
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        d = httpx.get(f"{BASE}/{path}/{tid}", headers=_hdr(), timeout=60).json()["data"]
        if d["status"] == "COMPLETED":
            return d["generated"]
        if d["status"] == "FAILED":
            raise RuntimeError(f"Freepik {path} FAILED: {d.get('error')}")
    raise TimeoutError(f"Freepik {path} sem resposta em {timeout}s")


def _download(url: str) -> Image.Image:
    r = httpx.get(url, timeout=120, follow_redirects=True)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content))


def flux_klein(prompt: str, refs: list[str | Path], *, resolution: str = "2k") -> Image.Image:
    body = {"prompt": prompt, "aspect_ratio": "horizontal_2_1", "resolution": resolution, "output_format": "png"}
    for i, p in enumerate(refs[:4]):
        body["input_image" + ("" if i == 0 else f"_{i + 1}")] = _b64(p)
    return _download(_task("text-to-image/flux-2-klein", body)[0])


def gpt_image_2_edit(prompt: str, refs: list[str | Path], *, resolution: str = "2k", quality: str = "medium") -> Image.Image:
    body = {"prompt": prompt, "reference_images": [_b64(p) for p in refs[:16]], "aspect_ratio": "horizontal_2_1",
            "resolution": resolution, "quality": quality, "output_format": "png", "num_images": 1}
    return _download(_task("text-to-image/gpt-image-2-edit", body)[0])


def gpt_image_2(prompt: str, *, resolution: str = "2k", quality: str = "medium") -> Image.Image:
    body = {"prompt": prompt, "aspect_ratio": "horizontal_2_1", "resolution": resolution, "quality": quality,
            "output_format": "png", "num_images": 1}
    return _download(_task("text-to-image/gpt-image-2", body)[0])


def upscale(img_path: str | Path, scale: int = 2) -> Image.Image:
    body = {"image": base64.b64encode(Path(img_path).read_bytes()).decode(), "scale_factor": str(scale), "optimized_for": "standard"}
    return _download(_task("image-upscaler", body, timeout=900)[0])

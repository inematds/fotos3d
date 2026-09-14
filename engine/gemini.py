"""Cliente Gemini: visão (análise das fotos) e geração de imagem com referências."""
from __future__ import annotations

import base64
import io
import json
import mimetypes
import time
from pathlib import Path

import httpx
from PIL import Image

from .env import key

BASE = "https://generativelanguage.googleapis.com/v1beta/models"
VISION_MODEL = "gemini-3-flash-preview"
IMAGE_MODELS = {
    "gemini-flash": "gemini-3.1-flash-image",   # rápido e barato
    "gemini-pro": "gemini-3-pro-image",          # mais fiel, até 4K
}


def _img_part(path: str | Path, max_side: int = 1536) -> dict:
    """Reduz a imagem (economiza tokens) e devolve inline_data."""
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}


def _post(model: str, body: dict, timeout: float = 300) -> dict:
    url = f"{BASE}/{model}:generateContent"
    last = None
    for tentativa in range(3):
        r = httpx.post(url, params={"key": key("GEMINI_API_KEY")}, json=body, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        last = f"{r.status_code}: {r.text[:400]}"
        if r.status_code in (429, 500, 503):
            time.sleep(5 * (tentativa + 1))
            continue
        break
    raise RuntimeError(f"Gemini {model} falhou — {last}")


def vision_json(prompt: str, imagens: list[str | Path], model: str = VISION_MODEL) -> dict:
    parts = [{"text": prompt}] + [_img_part(p) for p in imagens]
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    try:
        out = _post(model, body, timeout=180)
    except RuntimeError:
        out = _post("gemini-2.5-flash", body, timeout=180)  # fallback se o preview estiver fora (503)
    txt = "".join(p.get("text", "") for p in out["candidates"][0]["content"]["parts"])
    txt = txt.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    obj, _ = json.JSONDecoder().raw_decode(txt[txt.find("{"):])  # ignora texto extra após o JSON
    return obj


def gerar_imagem(prompt: str, referencias: list[str | Path] | None = None, *, modelo: str = "gemini-flash",
                 aspect_ratio: str = "16:9", image_size: str = "2K") -> Image.Image:
    """Gera uma imagem (com ou sem referências) e devolve PIL.Image."""
    parts = [{"text": prompt}] + [_img_part(p) for p in (referencias or [])]
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio, "imageSize": image_size},
        },
    }
    out = _post(IMAGE_MODELS.get(modelo, modelo), body)
    for cand in out.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if "inlineData" in part:
                return Image.open(io.BytesIO(base64.b64decode(part["inlineData"]["data"])))
    raise RuntimeError(f"Gemini não devolveu imagem: {json.dumps(out)[:600]}")

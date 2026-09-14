"""Geração de imagem via OpenRouter (modelos Gemini Image / GPT Image) com referências."""
from __future__ import annotations

import base64
import io
import json
import time
from pathlib import Path

import httpx
from PIL import Image

from .env import key
from .gemini import _img_part

URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS = {
    "or-gemini-flash": "google/gemini-3.1-flash-image",
    "or-gemini-pro": "google/gemini-3-pro-image",
    "or-gpt-image": "openai/gpt-5-image",
}


def gerar_imagem(prompt: str, referencias: list[str | Path] | None = None, *, modelo: str = "or-gemini-flash",
                 aspect_ratio: str = "16:9", image_size: str = "2K") -> Image.Image:
    content = [{"type": "text", "text": prompt}]
    for p in referencias or []:
        d = _img_part(p)["inline_data"]
        content.append({"type": "image_url", "image_url": {"url": f"data:{d['mime_type']};base64,{d['data']}"}})
    body = {
        "model": MODELS.get(modelo, modelo),
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
        "image_config": {"aspect_ratio": aspect_ratio, "image_size": image_size},
    }
    hdr = {"Authorization": f"Bearer {key('OPENROUTER_API_KEY')}", "HTTP-Referer": "https://inema.club", "X-Title": "fotos3d"}
    last = None
    for tentativa in range(3):
        r = httpx.post(URL, headers=hdr, json=body, timeout=600)
        if r.status_code == 200:
            out = r.json()
            msg = out["choices"][0]["message"]
            for im in msg.get("images") or []:
                url = im.get("image_url", {}).get("url", "")
                if url.startswith("data:"):
                    return Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1])))
            last = f"sem imagem na resposta: {json.dumps(out)[:400]}"
            break
        last = f"{r.status_code}: {r.text[:400]}"
        if r.status_code in (429, 500, 502, 503):
            time.sleep(5 * (tentativa + 1))
            continue
        break
    raise RuntimeError(f"OpenRouter {body['model']} falhou — {last}")

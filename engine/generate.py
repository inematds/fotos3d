"""Etapa 3: gerar a panorâmica equiretangular a partir do prompt + fotos de referência."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from .checks import TARGET_H, TARGET_W
from .providers import DEFAULT, gerar


def gerar_panorama(prompt: str, fotos: list[str | Path], *, modelo: str = DEFAULT, image_size: str = "2K") -> Image.Image:
    """Gera no ratio nativo do modelo e leva para 2:1 exato.

    Modelos Gemini não têm 2:1 nativo: geramos 16:9 e reamostramos para 2:1
    (estiro horizontal de 12,5%, imperceptível numa equiretangular inferida).
    """
    img = gerar(prompt, fotos, modelo=modelo, image_size=image_size).convert("RGB")
    w, h = img.size
    alvo_w = max(TARGET_W, w) if w >= TARGET_W else TARGET_W
    alvo_h = alvo_w // 2
    if (w, h) != (alvo_w, alvo_h):
        img = img.resize((alvo_w, alvo_h), Image.LANCZOS)
    return img

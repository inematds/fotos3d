"""Registro de modelos de imagem disponíveis (id → provedor, custo estimado, ratio suportado)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from . import freepik, gemini, openrouter

# id: (provedor, nome exibido, custo estimado por imagem, ratio da panorâmica que o modelo aceita)
MODELOS = {
    "or-gemini-flash": ("openrouter", "Gemini 3.1 Flash Image (OpenRouter)", "~US$0,04", "16:9"),
    "or-gemini-pro":   ("openrouter", "Gemini 3 Pro Image (OpenRouter)", "~US$0,13 (2K) / 0,24 (4K)", "16:9"),
    "gemini-flash":    ("gemini", "Gemini 3.1 Flash Image (API Google, paga)", "~US$0,04", "16:9"),
    "gemini-pro":      ("gemini", "Gemini 3 Pro Image (API Google, paga)", "~US$0,13", "16:9"),
    "flux-klein":      ("freepik", "Flux 2 Klein (Magnific, 2:1 nativo, 2048x1024)", "10 créditos", "2:1"),
    "gpt-image-2":     ("freepik", "GPT Image 2 Edit (Magnific, 2:1 nativo, até 4K)", "~45-90 créditos", "2:1"),
}
DEFAULT = "flux-klein"


def gerar(prompt: str, referencias: list[str | Path] | None, *, modelo: str = DEFAULT,
          aspect_ratio: str | None = None, image_size: str = "2K") -> Image.Image:
    prov, _, _, ratio = MODELOS[modelo]
    ar = aspect_ratio or ratio
    if prov == "freepik":
        if modelo == "flux-klein":
            return freepik.flux_klein(prompt, referencias or [], resolution="2k")
        return freepik.gpt_image_2_edit(prompt, referencias or [], resolution=image_size.lower(), quality="medium")
    if prov == "openrouter":
        return openrouter.gerar_imagem(prompt, referencias, modelo=modelo, aspect_ratio=ar, image_size=image_size)
    return gemini.gerar_imagem(prompt, referencias, modelo=modelo, aspect_ratio=ar, image_size=image_size)

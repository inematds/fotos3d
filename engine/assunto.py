"""Modo 2: a partir de um assunto em texto, criar as fotos do cômodo."""
from __future__ import annotations

from pathlib import Path

from .providers import gerar as gerar_imagem, DEFAULT

VISTAS = [
    ("01-ampla", "Wide establishing shot of the room from the entrance, showing the main wall and most of the furniture."),
    ("02-esquerda", "Same room, camera turned 90° to the LEFT of the first view, showing the left wall."),
    ("03-direita", "Same room, camera turned 90° to the RIGHT of the first view, showing the right wall."),
    ("04-oposta", "Same room, camera turned 180°, looking back toward the entrance / the wall opposite the first view."),
    ("05-detalhe", "Same room, medium shot from a corner showing the main seating area and the window together."),
]

BASE_PROMPT = ("Realistic real-estate interior photograph, natural light, eye-level camera, 24mm lens, sharp, "
               "no people, no text, no watermark. Room: {assunto}.")

CONSISTENCIA = (" This must be the SAME room as the reference photo: identical walls, floor, ceiling, windows, doors, "
                "furniture, materials, colors and lighting; only the camera direction changes. Do not add or remove furniture.")


def criar_fotos(assunto: str, destino: str | Path, *, modelo: str = DEFAULT, n: int = 5,
                progresso=None) -> list[Path]:
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    saidas: list[Path] = []
    base_path = None
    for i, (nome, vista) in enumerate(VISTAS[:n], 1):
        if progresso:
            progresso(f"Gerando foto {i}/{n}: {nome}")
        prompt = BASE_PROMPT.format(assunto=assunto) + " " + vista
        refs = []
        if base_path:
            prompt += CONSISTENCIA
            refs = [base_path]
        img = gerar_imagem(prompt, refs, modelo=modelo, aspect_ratio="4:3", image_size="1K")
        p = destino / f"{nome}.jpg"
        img.convert("RGB").save(p, quality=92)
        saidas.append(p)
        base_path = base_path or p
    return saidas

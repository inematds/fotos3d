"""Checagens de uma panorâmica equiretangular: proporção, resolução e costura."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image

TARGET_W, TARGET_H = 4096, 2048
SEAM_OK = 12.0       # diferença média (0-255) até onde a costura é considerada boa
SEAM_BAD = 30.0      # acima disso, costura visível


@dataclass
class Relatorio:
    largura: int
    altura: int
    ratio: float
    ratio_ok: bool
    resolucao_ok: bool
    seam_score: float
    seam_ok: bool
    seam_status: str
    ajustes: list[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


def seam_score(img: Image.Image, faixa: int = 8) -> float:
    """Diferença média absoluta entre as `faixa` colunas mais à esquerda e mais à direita.

    Numa equiretangular correta a borda direita continua na esquerda, então as
    colunas extremas devem ser parecidas. 0 = perfeito. Compara em resolução
    reduzida para tolerar ruído fino.
    """
    small = img.convert("RGB").resize((1024, 512))
    a = np.asarray(small, dtype=np.float32)
    esq = a[:, :faixa, :].mean(axis=1)
    dir_ = a[:, -faixa:, :].mean(axis=1)
    return float(np.abs(esq - dir_).mean())


def corrigir_ratio(img: Image.Image) -> tuple[Image.Image, list[str]]:
    """Garante 2:1 exato por crop central mínimo + resize."""
    ajustes: list[str] = []
    w, h = img.size
    if abs(w / h - 2.0) > 0.005:
        if w / h > 2.0:  # largo demais: corta laterais
            nw = int(round(h * 2))
            x0 = (w - nw) // 2
            img = img.crop((x0, 0, x0 + nw, h))
        else:  # alto demais: corta topo/base
            nh = int(round(w / 2))
            y0 = (h - nh) // 2
            img = img.crop((0, y0, w, y0 + nh))
        ajustes.append(f"crop central para 2:1 (de {w}x{h} para {img.size[0]}x{img.size[1]})")
    return img, ajustes


def garantir_resolucao(img: Image.Image) -> tuple[Image.Image, list[str]]:
    ajustes: list[str] = []
    if img.size[0] < TARGET_W:
        ajustes.append(f"upscale bicúbico de {img.size[0]}x{img.size[1]} para {TARGET_W}x{TARGET_H}")
        img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    return img, ajustes


def checar(caminho: str | Path, corrigir: bool = True, salvar_em: str | Path | None = None) -> Relatorio:
    img = Image.open(caminho)
    ajustes: list[str] = []
    w0, h0 = img.size
    if corrigir:
        img, a1 = corrigir_ratio(img)
        img, a2 = garantir_resolucao(img)
        ajustes = a1 + a2
        if ajustes and salvar_em:
            img.save(salvar_em)
    w, h = img.size
    score = seam_score(img)
    status = "boa" if score <= SEAM_OK else ("aceitável" if score <= SEAM_BAD else "visível")
    return Relatorio(
        largura=w, altura=h, ratio=round(w / h, 4), ratio_ok=abs(w / h - 2) < 0.005,
        resolucao_ok=w >= TARGET_W, seam_score=round(score, 2), seam_ok=score <= SEAM_BAD,
        seam_status=status, ajustes=ajustes,
    )


if __name__ == "__main__":
    import sys
    print(checar(sys.argv[1], corrigir=False).to_json())

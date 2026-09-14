"""Suavização da costura esquerda↔direita de uma equiretangular (crossfade curto nas bordas)."""
from __future__ import annotations

import numpy as np
from PIL import Image


def suavizar_costura(img: Image.Image, fracao: float = 0.015) -> Image.Image:
    """Faz um crossfade entre as bordas para o wrap ficar contínuo.

    Roda a imagem meia volta (a costura vai pro centro), mistura uma faixa
    estreita ao redor dela com pesos lineares e desfaz a rotação. Não corrige
    geometria, só elimina a linha dura.
    """
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    h, w, _ = a.shape
    n = max(8, int(w * fracao))
    r = np.roll(a, w // 2, axis=1)  # costura agora em x = w//2
    c = w // 2
    esq = r[:, c - n:c, :]
    dir_ = r[:, c:c + n, :]
    # a faixa esquerda deve terminar parecendo o início da direita, e vice-versa
    t = np.linspace(0, 1, 2 * n, dtype=np.float32)[None, :, None]
    faixa = np.concatenate([esq, dir_], axis=1)
    espelho = np.concatenate([dir_[:, :1, :].repeat(n, axis=1), esq[:, -1:, :].repeat(n, axis=1)], axis=1)
    # mistura suave: pesos em forma de sino centrados na costura
    peso = (1 - np.abs(t * 2 - 1)) * 0.6
    mix = faixa * (1 - peso) + espelho * peso
    r[:, c - n:c + n, :] = mix
    out = np.roll(r, -(w // 2), axis=1)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

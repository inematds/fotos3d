import numpy as np
from PIL import Image

from engine.checks import checar, corrigir_ratio, seam_score


def _gradiente_ciclico(w=1024, h=512):
    # padrão que se repete em 360°: seno horizontal → borda esquerda == direita
    x = np.linspace(0, 2 * np.pi, w, endpoint=False)
    linha = ((np.sin(x) + 1) * 127).astype(np.uint8)
    a = np.repeat(linha[None, :], h, axis=0)
    return Image.fromarray(np.stack([a, a, a], axis=-1))


def test_seam_perfeita_da_score_baixo():
    assert seam_score(_gradiente_ciclico()) < 10


def test_seam_quebrada_da_score_alto():
    img = _gradiente_ciclico()
    a = np.asarray(img).copy()
    a[:, -60:, :] = 255  # borda direita branca, esquerda cinza escuro
    assert seam_score(Image.fromarray(a)) > 30


def test_corrigir_ratio_largo():
    img = Image.new("RGB", (3000, 1000))
    out, ajustes = corrigir_ratio(img)
    assert out.size == (2000, 1000) and ajustes


def test_corrigir_ratio_alto():
    img = Image.new("RGB", (2000, 1500))
    out, _ = corrigir_ratio(img)
    assert out.size == (2000, 1000)


def test_checar_upscale(tmp_path):
    p = tmp_path / "p.png"
    _gradiente_ciclico().save(p)
    out = tmp_path / "o.png"
    r = checar(p, salvar_em=out)
    assert r.largura == 4096 and r.altura == 2048 and r.ratio_ok and r.resolucao_ok
    assert out.exists()

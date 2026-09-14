"""Pipeline completo: fotos (ou assunto) → análise → prompt → panorâmica 360 → checagens → arquivos."""
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path
from typing import Callable

from .analyze import analisar
from .assunto import criar_fotos
from .checks import SEAM_BAD, SEAM_OK, checar
from PIL import Image
from .env import OUTPUT_DIR
from .generate import gerar_panorama
from .prompt import montar_prompt, prompt_reforco_costura
from .seam import suavizar_costura
from .providers import DEFAULT

EXT = {".jpg", ".jpeg", ".png", ".webp"}
Progresso = Callable[[str], None]


def listar_fotos(pasta: str | Path) -> list[Path]:
    return sorted(p for p in Path(pasta).iterdir() if p.suffix.lower() in EXT)


def rodar(*, nome: str, fotos: list[Path] | None = None, assunto: str | None = None, modelo: str = DEFAULT,
          image_size: str = "2K", progresso: Progresso = print, retry_costura: bool = True) -> dict:
    t0 = time.time()
    out = OUTPUT_DIR / nome
    out.mkdir(parents=True, exist_ok=True)

    if assunto and not fotos:
        progresso("Modo assunto: criando fotos do cômodo")
        fotos = criar_fotos(assunto, out / "fotos", modelo=modelo, progresso=progresso)
    elif fotos:
        (out / "fotos").mkdir(exist_ok=True)
        fotos = [Path(shutil.copy(f, out / "fotos" / Path(f).name)) for f in fotos]
    else:
        raise ValueError("informe fotos ou assunto")
    if len(fotos) < 2:
        raise ValueError("preciso de pelo menos 2 fotos do cômodo")

    progresso(f"Analisando {len(fotos)} fotos (visão)")
    analise = analisar(fotos, salvar_em=out / "analise.json")
    prompt = montar_prompt(analise)
    (out / "prompt.txt").write_text(prompt)

    progresso(f"Gerando panorâmica 360 com {modelo}")
    img = gerar_panorama(prompt, fotos, modelo=modelo, image_size=image_size)
    final = out / f"{nome}-360.png"
    img.save(final)
    rel = checar(final, salvar_em=final)
    progresso(f"Checagem: {rel.largura}x{rel.altura}, costura {rel.seam_status} ({rel.seam_score})")

    if retry_costura and rel.seam_score > SEAM_BAD:
        progresso("Costura visível: regenerando uma vez com reforço")
        img2 = gerar_panorama(prompt_reforco_costura(prompt), fotos, modelo=modelo, image_size=image_size)
        alt = out / f"{nome}-360-v2.png"
        img2.save(alt)
        rel2 = checar(alt, salvar_em=alt)
        progresso(f"Checagem v2: costura {rel2.seam_status} ({rel2.seam_score})")
        if rel2.seam_score < rel.seam_score:
            shutil.copy(alt, final)
            rel = rel2

    if rel.seam_score > SEAM_OK:
        progresso("Suavizando costura (crossfade nas bordas)")
        suavizar_costura(Image.open(final)).save(final)
        rel = checar(final, corrigir=False)
        progresso(f"Costura após suavização: {rel.seam_status} ({rel.seam_score})")

    relatorio = {"nome": nome, "modelo": modelo, "fotos": [str(f) for f in fotos], "panorama": str(final),
                 "checagem": json.loads(rel.to_json()), "segundos": round(time.time() - t0, 1),
                 "tipo_comodo": analise.get("tipo_comodo")}
    (out / "relatorio.json").write_text(json.dumps(relatorio, indent=2, ensure_ascii=False))
    progresso(f"Pronto: {final}")
    return relatorio


def main() -> None:
    ap = argparse.ArgumentParser(description="fotos3d — fotos ou assunto → panorâmica 360")
    ap.add_argument("entrada", nargs="?", help="pasta com fotos do cômodo")
    ap.add_argument("--assunto", help="descrição do cômodo (gera as fotos)")
    ap.add_argument("--nome", required=True)
    ap.add_argument("--modelo", default=DEFAULT)
    ap.add_argument("--size", default="2K", choices=["1K", "2K", "4K"])
    ap.add_argument("--sem-retry", action="store_true")
    a = ap.parse_args()
    fotos = listar_fotos(a.entrada) if a.entrada else None
    r = rodar(nome=a.nome, fotos=fotos, assunto=a.assunto, modelo=a.modelo, image_size=a.size, retry_costura=not a.sem_retry)
    print(json.dumps(r["checagem"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

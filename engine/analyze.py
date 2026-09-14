"""Etapa 1: entender as fotos como um único cômodo."""
from __future__ import annotations

import json
from pathlib import Path

from .gemini import vision_json

PROMPT = """Você recebe várias fotos do MESMO cômodo, tiradas de pontos e direções diferentes.
Tarefa: reconstruir mentalmente o cômodo como um espaço único e responder em JSON com:
{
 "tipo_comodo": "sala de estar | cozinha | quarto | ...",
 "estilo": "descrição curta do estilo e materiais dominantes",
 "iluminacao": "fonte, direção, temperatura de cor, hora do dia",
 "paredes": [{"id":"N|E|S|W","descricao":"o que há nessa parede: janelas, portas, quadros, móveis encostados"}],
 "moveis": [{"nome":"...","posicao":"parede/canto/centro","aparece_nas_fotos":[1,2]}],
 "piso": "...", "teto": "...",
 "fotos": [{"indice":1,"direcao_estimada":"N|NE|E|...","descricao":"o que a foto mostra","ponto_de_vista":"de onde foi tirada"}],
 "areas_nao_vistas": "quais paredes/cantos nenhuma foto cobre e o que provavelmente há lá (inferência conservadora)",
 "descricao_360": "parágrafo único, em inglês, descrevendo o cômodo girando 360° a partir do centro, no sentido horário começando pela parede mais reconhecível; cite cada móvel, porta e janela UMA vez só, com posição relativa. Sem pessoas, sem texto."
}
As fotos estão numeradas na ordem em que foram enviadas (1 = primeira). Não invente objetos que não aparecem; para áreas não vistas, sugira apenas parede lisa ou continuação coerente do que existe."""


def analisar(fotos: list[str | Path], salvar_em: str | Path | None = None) -> dict:
    fotos = sorted(fotos, key=lambda p: str(p))
    dados = vision_json(PROMPT, fotos)
    dados["_fotos"] = [str(p) for p in fotos]
    if salvar_em:
        Path(salvar_em).write_text(json.dumps(dados, indent=2, ensure_ascii=False))
    return dados

---
name: property-360
description: Transforma várias fotos comuns de um MESMO cômodo (ou só uma descrição em texto) numa panorâmica 360° equiretangular 2:1 (4096×2048) fotorrealista, fiel ao imóvel, com checagem de proporção e costura e viewer 360. Use quando o usuário pedir "360 da sala", "panorâmica do cômodo", "tour virtual a partir de fotos", "vira 360", "property 360", ou der uma pasta de fotos de um ambiente / um assunto de cômodo e quiser a imagem 360.
---

# property-360 — fotos comuns → sala em 360°

Motor: `~/projetos/fotos3d` (Python). Saída: `~/projetos/output/fotos3d/<nome>/`.

## Fluxo (o script faz tudo; você orquestra e revisa)

1. **Entrada.** Pasta com 4–6 fotos do mesmo cômodo (JPG/PNG), ou `--assunto "descrição"` (a IA cria 5 fotos coerentes antes).
2. **Rodar:**
   ```bash
   cd ~/projetos/fotos3d
   python3 -m engine.pipeline <pasta_fotos> --nome <nome-da-sala> [--modelo flux-klein|gpt-image-2|or-gemini-pro|or-gemini-flash] [--size 2K|4K]
   python3 -m engine.pipeline --assunto "sala moderna, sofá cinza, janela ampla..." --nome <nome>
   ```
   Etapas internas: visão (Gemini) entende as fotos como um único cômodo → prompt conservador (preservar, não redesenhar, sem pessoas/texto) → geração com as fotos como referência em 2:1 → checagem (ratio exato, ≥4096×2048, score de costura) → 1 regeneração automática se a costura estiver ruim.
3. **Revisar** a imagem: abrir `viewer/index.html?src=<png>` ou a interface web (`uvicorn web.app:app --port 8360`). Olhar no viewer, não na imagem plana: móvel duplicado, porta/janela repetida, parede impossível, salto de luz, quebra no ponto de virada.
4. **Se estiver ruim:** regenerar (mesmo comando) ou trocar de modelo. Relatório em `relatorio.json` (score de costura: ≤12 boa, ≤30 aceitável, >30 visível).

## Modelos

| id | quando usar | custo |
|---|---|---|
| `flux-klein` (padrão) | melhor custo/fidelidade; 2:1 nativo, 2048×1024 reamostrado para 4096 | 10 créditos Magnific |
| `gpt-image-2` | melhor qualidade (projeção esférica correta, costura boa); 16 refs, até 4K; ~80 s | ~45–90 créditos |
| `or-gemini-pro` | alternativa via OpenRouter (16:9 reamostrado p/ 2:1) | ~US$0,13 |

## Regras

- É reconstrução por IA, não scan: áreas não fotografadas são inferidas. Avisar o usuário.
- Nunca redesenhar: se o resultado adicionou móveis/janelas, regenerar; não "melhorar" o imóvel.
- Várias salas: rodar uma vez por pasta (`--nome living`, `--nome cozinha`...). Tour ligando as salas é fase 2.
- Keys carregadas em runtime de `~/projetos/wifi/.env` (MAGNIFIC_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY). Não imprimir.

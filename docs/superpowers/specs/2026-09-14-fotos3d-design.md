# fotos3d — fotos comuns de um cômodo → panorâmica 360° (design)

Data: 2026-09-14. Baseado no tutorial "Turn Multiple Property Photos Into a 360° Interior Image With Codex" (AI Video Lab / Skool).

## Objetivo

Receber 4–6 fotos normais de um mesmo cômodo e produzir UMA panorâmica equiretangular 2:1 (alvo 4096×2048) fotorrealista, fiel ao imóvel, visualizável num viewer 360. Uso: marketing imobiliário, preview, insumo para vídeo IA. Não é scan fiel (LiDAR); áreas não fotografadas são inferidas pela IA.

## O que o tutorial esconde

"Codex" não gera imagem. O agente (Codex/Claude Code) faz visão + orquestração; a panorâmica sai de um modelo de imagem multi-referência (Nano Banana 2, Seedream, Flux Klein via API Freepik/Magnific; ou Gemini direto). A escolha do gerador é a decisão central e é validada por spike pago pequeno.

## Componentes

1. **`engine/`** (Python, sem MCP, chama API HTTP)
   - `analyze.py` — visão (Gemini) sobre as fotos → JSON: layout, paredes, portas, janelas, móveis, iluminação, ordem angular estimada das fotos.
   - `prompt.py` — JSON da sala → prompt de geração conservador (preservar, não redesenhar, sem pessoas/texto, 2:1, bordas contínuas).
   - `generate.py` — chama o modelo com as fotos como referência; polling; download.
   - `checks.py` — proporção 2:1 exata (corrige por resize), resolução mínima (upscale se preciso), score de costura (borda esquerda × direita), relatório JSON.
   - `pipeline.py` — CLI: `python -m engine.pipeline <pasta_fotos> --nome sala --modelo X` → salva em `~/projetos/output/fotos3d/<nome>-360.png` + `<nome>-relatorio.json`.
2. **`web/`** — FastAPI + página única: upload/pasta, nome, modelo (com custo), Gerar, progresso por etapa, resultado em viewer 360 embutido (Pannellum via cdnjs), baixar, regenerar, galeria de saídas.
3. **`viewer/index.html`** — viewer 360 standalone (arrasta o PNG ou `?src=`).
4. **`skill/property-360/SKILL.md`** — skill Claude Code que descreve o fluxo e chama o pipeline; instalada em `~/.claude/skills/property-360`.
5. **`guia/index.html`** — landing + guia (skill projetos-landing-guia), publicada no GitHub Pages `inematds/fotos3d`, e card no portal inema.club.

## Fluxo

fotos → analyze (visão) → prompt → generate (multi-ref, 2:1) → checks (ratio, resolução, costura) → [se costura ruim: 1 retry com prompt reforçado] → salvar → viewer.

## Erros

- API sem crédito/auth → mensagem clara, sem retry infinito (máx. 2 tentativas, timeout 5 min por geração).
- Modelo devolve ratio ≠ 2:1 → corrigir por resize/crop central e registrar no relatório.
- Costura ruim (score acima do limiar) → 1 regeneração; se persistir, entregar com aviso.

## Testes

- `checks.py` com testes unitários (imagens sintéticas: seam perfeita vs. quebrada, ratio errado).
- Spike: mesma sala em 2–3 modelos; comparação visual no viewer; decisão registrada em `docs/api-freepik.md`.
- Fim a fim com `samples/sala/`.

## Fora de escopo (fase 2)

Tour multi-cômodo com hotspots; edição manual de costura; modelo 3D real.

## Convenções

Saída em `~/projetos/output/fotos3d/`. Keys carregadas em runtime de `~/projetos/wifi/.env`. Repo `inematds/fotos3d`, autor `inematds`. Versão inicial `v1.0.0`.

## Modo 2: por assunto (adicionado 2026-09-14)

Entrada alternativa: só um texto ("sala moderna, sofá cinza, janela ampla, piso de madeira"). Fluxo: texto → 1 foto-base ampla do cômodo (text-to-image) → 4–5 vistas adicionais do MESMO cômodo usando a foto-base como referência (virada pra janela, pra entrada, parede oposta, detalhe) → segue o pipeline normal (analyze → generate 360 → checks). As fotos geradas ficam em `~/projetos/output/fotos3d/<nome>/fotos/` e podem ser trocadas/editadas antes da 360. Na interface: aba "Por fotos" e aba "Por assunto".

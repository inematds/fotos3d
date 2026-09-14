# fotos3d — fotos comuns de um cômodo → sala em 360°

Versão 1.0.0. Pega 4–6 fotos normais de um mesmo ambiente (ou só uma descrição em texto) e gera uma panorâmica **equiretangular 2:1 (4096×2048)** fotorrealista, fiel ao imóvel, que você gira num viewer 360 como num tour virtual. Sem câmera 360, sem scan, sem software 3D.

> É **reconstrução por IA**, não medição: as áreas que nenhuma foto mostra são inferidas de forma conservadora. Serve para marketing imobiliário, preview, conteúdo de tour virtual e insumo para vídeo IA. Não substitui um scan LiDAR.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/fotos3d/guia/**

Baseado no tutorial "Turn Multiple Property Photos Into a 360° Interior Image With Codex" (AI Video Lab). A diferença: aqui a peça que o tutorial esconde (qual modelo de imagem gera a 360) está resolvida e testada.

## Como funciona

```
fotos (ou assunto) → visão (Gemini) entende o cômodo → prompt conservador
→ modelo de imagem com as fotos como referência, 2:1 nativo
→ checagens (ratio exato, ≥4096×2048, score de costura) → suavização da costura → PNG + relatório
```

Modelos testados na mesma sala (Robie House, 6 fotos reais):

| id | provedor | 2:1 nativo | resultado | custo |
|---|---|---|---|---|
| `flux-klein` (padrão) | Freepik/Magnific | sim (2048×1024 → upscale) | equiretangular real, muito fiel | 10 créditos |
| `gpt-image-2` | Freepik/Magnific | sim, até 4K, 16 refs | **melhor qualidade**: projeção esférica correta, costura boa (8), ~80 s | ~45–90 créditos |
| `or-gemini-pro` | OpenRouter | não (16:9 → 2:1) | 360 plausível, menos fiel (mudou tapete e janelas), costura ruim | ~US$0,13 |
| `or-gemini-flash` | OpenRouter | não | tende a sair grande-angular, não 360 | ~US$0,04 |

## Uso

```bash
cd ~/projetos/fotos3d
pip install -r requirements.txt

# por fotos
python3 -m engine.pipeline /caminho/fotos-da-sala --nome sala-302

# por assunto (a IA cria 5 fotos coerentes e depois a 360)
python3 -m engine.pipeline --assunto "sala moderna, sofá cinza em L, janela grande, piso de madeira clara" --nome demo

# interface web (upload, progresso, viewer 360, galeria)
uvicorn web.app:app --port 8360   # abre http://127.0.0.1:8360
```

Saída em `~/projetos/output/fotos3d/<nome>/`: `<nome>-360.png`, `analise.json`, `prompt.txt`, `relatorio.json`, `fotos/`.

Viewer avulso: abra `viewer/index.html` no navegador e arraste o PNG.

## Skill (Claude Code)

`skill/property-360/SKILL.md` — instale com `ln -s ~/projetos/fotos3d/skill/property-360 ~/.claude/skills/property-360`. Depois: *"usa a skill property-360 nas fotos da pasta X"*.

## Chaves

Carregadas em runtime de `~/projetos/wifi/.env`: `MAGNIFIC_API_KEY` (Freepik), `GEMINI_API_KEY` (visão), `OPENROUTER_API_KEY` (opcional). Nada é copiado.

## Testes

```bash
python3 -m pytest -q tests
```

## Amostra

`samples/sala/` — 6 fotos da sala da Robie House (Frank Lloyd Wright), Wikimedia Commons, foto de w_lemay, CC BY-SA 2.0.

## Licença

MIT.

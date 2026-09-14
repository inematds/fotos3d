# FALHAS — fotos3d

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-09-14 | Visão Gemini (`gemini-3-flash-preview`) devolveu 503 e derrubou a corrida do GPT Image 2 | fallback para `gemini-2.5-flash` na `vision_json` quando o preview falha | infra |
| 2026-09-14 | `json.loads` quebrou ("Extra data") porque o modelo de visão devolveu texto depois do JSON | `raw_decode` a partir do primeiro `{` + strip de cercas ```json | prompt |
| 2026-09-14 | Geração de imagem nas 4 chaves Google (`GEMINI_API_KEY*`, `GOOGLE_API_KEY`) → 429 "free tier limit 0" | usar OpenRouter (mesmos modelos Gemini Image) e Freepik/Magnific; Gemini direto só para visão | infra |
| 2026-09-14 | Gemini Flash Image entregou foto grande-angular esticada, não equiretangular 360 | trocar o padrão para Flux 2 Klein (2:1 nativo) + prompt com cues de projeção esférica | prompt |

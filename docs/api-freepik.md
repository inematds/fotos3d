# API Freepik / Magnific — geração de imagem com referências (pesquisa 2026-09-14)

Objetivo: gerar panorâmica equiretangular **2:1** (ideal 4096x2048) de uma sala a partir de 4–6 fotos de referência, via script Python.

Fontes: `https://docs.freepik.com` (hoje redireciona/rebrandeada como *Magnific API* — `docs.magnific.com`; conteúdo idêntico; OpenAPI embutido nas páginas `.md`).
Teste real feito em 2026-09-14 com a chave `MAGNIFIC_API_KEY` de `~/projetos/wifi/.env`.

## 1. Fundamentos (valem para todos os modelos)

| Item | Valor |
|---|---|
| Base URL | `https://api.freepik.com` **e** `https://api.magnific.com` (ambos respondem 200 — testado) |
| Auth header | `x-freepik-api-key: <KEY>` **ou** `x-magnific-api-key: <KEY>` (os dois funcionam com a mesma chave — testado) |
| Content-Type | `application/json` |
| Fluxo | assíncrono: `POST` → `{"data":{"task_id","status":"CREATED"}}` → `GET <mesmo path>/{task_id}` até `status` = `COMPLETED` \| `FAILED` (ou `webhook_url` no body) |
| Status | `CREATED`, `IN_PROGRESS`, `COMPLETED`, `FAILED` |
| Resultado | `data.generated[]` = lista de URLs (CDN `cdn-magnific.freepik.com`, com token/expiração) — baixar logo |
| Refs — formato | depende do modelo: base64 puro (sem prefixo `data:`), URL pública HTTPS, ou objeto `{image,text,mime_type}` (ver tabela) |
| Custo | API **sempre** desconta créditos (o "ilimitado" do plano só vale no app web). A doc pública não lista preço por modelo; usar `simulate_cost` no MCP ou a tabela medida em `~/.claude/runbooks/magnific-modelos.md` como estimativa |
| Tamanho custom em px | **nenhum** dos modelos com multi-referência aceita `width/height` livres. Só `flux-2-pro` (sem ratio nomeado, `width`/`height` 256–1440) e `flux-2-turbo` têm pixels custom — e 1440 é o teto, longe de 4096 |

Nomenclatura dos ratios: família Flux/GPT/Seedream usa **enums nomeados** (`horizontal_2_1`, `widescreen_16_9`…); família Gemini/Nano Banana usa **string numérica** (`"16:9"`, `"21:9"`). Passar `"2:1"` num modelo de enum nomeado → HTTP 400.

## 2. Tabela modelo × endpoint × refs × ratios × custo × testado

| Modelo | Endpoint `POST /v1/ai/...` | Refs (qtd / formato) | Ratios / resolução | **2:1?** | Custo (estim.) | Testado? |
|---|---|---|---|---|---|---|
| **Flux 2 Klein** | `text-to-image/flux-2-klein` | até 4: `input_image`, `input_image_2..4` — **base64** | enums: `square_1_1, widescreen_16_9, social_story_9_16, portrait_2_3, traditional_3_4, vertical_1_2, horizontal_2_1, social_post_4_5, standard_3_2, classic_4_3`; `resolution: 1k\|2k` (2k = dobro, cap 2048px/lado) | **SIM** `horizontal_2_1` → 1408×704 (1k) / 2048×1024 (2k) — ambos medidos | ~10 cr | **SIM** — 2 chamadas sem ref: 1k → 1408×704, 2k → 2048×1024, JPEG, ~3 s cada. Refs base64 **não** testadas |
| Flux 2 Pro | `text-to-image/flux-2-pro` | até 4: `input_image..4` — base64 | `width`/`height` livres **256–1440** (default 1024×768), sem enum | SIM (ex.: 1440×720) — mas máx 1440 de largura | ? (n/ medido) | não |
| Flux Kontext Pro | `text-to-image/flux-kontext-pro` | **1** (`input_image`, URL) | `square_1_1, classic_4_3, traditional_3_4, widescreen_16_9, social_story_9_16, standard_3_2` | **NÃO** | ? | não |
| Flux Kontext Max | `text-to-image/flux-kontext-max` | até 4 (`input_image..4`, **URL**) | 10 enums incl. `horizontal_2_1` e `vertical_1_2`; `output_format png\|jpeg` | **SIM** `horizontal_2_1` (px não documentado; classe ~1MP) | ? | não |
| **Gemini 2.5 Flash Image** ("nano banana" v1) | `gemini-2-5-flash-image-preview` (sem `text-to-image/` no path) | até **3**: `reference_images: ["<base64>" \| "<url>"]` | **nenhum parâmetro** de ratio/resolução (segue a ref / 1:1) | NÃO | ? | não |
| **Nano Banana Pro** (Gemini 3 Pro Image) | `text-to-image/nano-banana-pro` | até **14**: `reference_images: [{image: <URL pública>, text?, mime_type: image/png\|jpeg\|webp}]` — **só URL** (ou GCS) | `aspect_ratio: 1:1, 2:3, 3:2, 4:3, 3:4, 5:4, 4:5, 16:9, 9:16, 21:9`; `resolution: 1K\|2K\|4K` (default 2K) | **NÃO** (só 16:9 ou 21:9) | ~75 cr | não |
| **Nano Banana Pro Flash** (= "Nano Banana 2", Gemini 3.1 Flash Image) | `text-to-image/nano-banana-pro-flash` | até 14 (schema; overview diz 3) — mesmo objeto `{image: URL, text, mime_type}` | mesmos ratios de cima; `resolution 1K\|2K\|4K` (default 1K); `use_google_search_tool` | **NÃO** | ~75 cr | não |
| Seedream 4.5 Edit | `text-to-image/seedream-v4-5-edit` | 1–**5**: `reference_images: ["<base64>" \| "<url>"]` (obrigatório) | `square_1_1 (2048²), widescreen_16_9 (2730×1536), social_story_9_16, portrait_2_3, traditional_3_4, standard_3_2, classic_4_3, cinematic_21_9 (3062×1312)`; ~4 MP fixo | **NÃO** | ~50 cr | não |
| Seedream V5 Lite Edit | `text-to-image/seedream-v5-lite-edit` | 1–5, mesmo formato | mesmos 8 enums, 4 MP | NÃO | ? | não |
| **Seedream 5.0 Pro Edit** | `text-to-image/seedream-v5-pro-edit` | 1–**10**: `reference_images: ["<base64>" \| "<url>"]` (obrigatório) | mesmos 8 enums; `resolution: 1.5k\|2k` (2k ≈ 4.19 MP) | **NÃO** | ~100 cr | não |
| GPT Image 2 (t2i) | `text-to-image/gpt-image-2` | 0 | `square_1_1, classic_4_3, traditional_3_4, widescreen_16_9, social_story_9_16, film_horizontal_21_9, standard_3_2, portrait_2_3, horizontal_2_1, banner_3_1`; `resolution 1k\|2k\|4k`; `quality low\|medium\|high`; `num_images` ≤10 | SIM | tier×res: 1k×1, 2k×2, 4k×3 | não |
| **GPT Image 2 Edit** | `text-to-image/gpt-image-2-edit` | 1–**16**: `reference_images: ["<https url>" \| "<base64>" \| "<upload id>"]` (≤20 MiB cada, ≤64 MiB total) | mesmos 10 enums incl. **`horizontal_2_1`**; `resolution 1k\|2k\|4k` (não muda preço no edit); `quality` | **SIM** | por output; input domina | não |

Notas:
- **"GPT Image 1.5"** não existe mais na doc da API — foi substituído por **GPT Image 2** (`gpt-image-2` / `gpt-image-2-edit`). No MCP ainda há `gpt-1.5`, mas via HTTP é o 2.
- **"Nano Banana 2"** na doc = `nano-banana-pro-flash` (Gemini 3.1 Flash). O "Nano Banana 2 Lite" existe só no MCP (`imagen-nano-banana-2-lite`), não na API HTTP.
- `GET /v1/ai/text-to-image/<modelo>` (lista de tasks) retornou 404 no teste — usar sempre `GET .../{task_id}`.
- Pixels exatos do 2:1 em cada modelo: Klein 1408×704 (1k) / 2048×1024 (2k); GPT Image 2 — 2:1 em 1k/2k/4k, px não tabelados na doc (esperar ~2048×1024 em 2k, ~4096×2048 em 4k — **confirmar com 1 chamada**).

## 3. Exemplos reais (request/response) — teste de 2026-09-14

### 3.1 POST Flux 2 Klein (sem referência, só validação)

```bash
set -a; source ~/projetos/wifi/.env; set +a
curl -s -X POST "https://api.freepik.com/v1/ai/text-to-image/flux-2-klein" \
  -H "x-freepik-api-key: $MAGNIFIC_API_KEY" -H "Content-Type: application/json" \
  -d '{"prompt":"a wide interior photo of a living room",
       "aspect_ratio":"horizontal_2_1","resolution":"1k","output_format":"jpeg"}'
```

Resposta (200):
```json
{"data":{"task_id":"e30e9302-ad84-487b-9002-8746f01f495d","status":"CREATED","error":null,"generated":[]}}
```

### 3.2 GET polling

```bash
curl -s "https://api.freepik.com/v1/ai/text-to-image/flux-2-klein/e30e9302-ad84-487b-9002-8746f01f495d" \
  -H "x-freepik-api-key: $MAGNIFIC_API_KEY"
```

Resposta (já `COMPLETED` no 1º poll, ~3 s):
```json
{"data":{"task_id":"e30e9302-ad84-487b-9002-8746f01f495d","status":"COMPLETED","error":null,
 "generated":["https://cdn-magnific.freepik.com/result_FLUX_2_KLEIN_e30e9302-..._0.jpeg?token=exp=1789394468~hmac=...&size=stable"]}}
```
Imagem baixada: **1408×704 JPEG** (bate com a tabela `horizontal_2_1` @1k).
Segunda chamada igual com `"resolution":"2k"` (task `df6a212c-...`): `COMPLETED` no 1º poll, imagem **2048×1024 JPEG** — confirma que o 2k dobra o 1k dentro do cap de 2048 px.

### 3.3 Body com referências — por modelo (da OpenAPI)

Flux 2 Klein (base64 puro, sem `data:` prefix):
```json
{"prompt":"...","aspect_ratio":"horizontal_2_1","resolution":"2k","output_format":"png",
 "input_image":"<b64>","input_image_2":"<b64>","input_image_3":"<b64>","input_image_4":"<b64>"}
```

GPT Image 2 Edit:
```json
{"prompt":"...","reference_images":["https://.../foto1.jpg","<b64>", "..."],
 "aspect_ratio":"horizontal_2_1","resolution":"4k","quality":"high","output_format":"png","num_images":1}
```

Seedream 5.0 Pro Edit (sem 2:1 — usar 21:9 e recortar/expandir, ou 16:9):
```json
{"prompt":"...","reference_images":["<b64 ou url>", "..."],"aspect_ratio":"cinematic_21_9","resolution":"2k"}
```

Nano Banana Pro / Pro Flash (refs **só por URL pública**):
```json
{"prompt":"...","aspect_ratio":"21:9","resolution":"4K",
 "reference_images":[{"image":"https://.../foto1.jpg","mime_type":"image/jpeg","text":"north wall"},
                     {"image":"https://.../foto2.jpg","mime_type":"image/jpeg","text":"east wall"}]}
```

Gemini 2.5 Flash Image (Freepik):
```json
{"prompt":"...","reference_images":["<b64>","https://.../foto2.jpg","<b64>"]}
```
GET: `/v1/ai/gemini-2-5-flash-image-preview/{task_id}`.

### 3.4 Esqueleto Python (requests)

```python
import os, time, base64, requests
BASE = "https://api.freepik.com"
H = {"x-freepik-api-key": os.environ["MAGNIFIC_API_KEY"], "Content-Type": "application/json"}
def b64(p): return base64.b64encode(open(p, "rb").read()).decode()

def run(model_path, body, timeout=300):
    r = requests.post(f"{BASE}/v1/ai/{model_path}", headers=H, json=body); r.raise_for_status()
    tid = r.json()["data"]["task_id"]
    t0 = time.time()
    while time.time() - t0 < timeout:
        d = requests.get(f"{BASE}/v1/ai/{model_path}/{tid}", headers=H).json()["data"]
        if d["status"] == "COMPLETED": return d["generated"]
        if d["status"] == "FAILED": raise RuntimeError(d)
        time.sleep(3)
    raise TimeoutError(tid)

# ex.: Klein com 4 refs em 2:1
refs = ["s1.jpg", "s2.jpg", "s3.jpg", "s4.jpg"]
body = {"prompt": "360 equirectangular panorama of this living room, seamless, 2:1",
        "aspect_ratio": "horizontal_2_1", "resolution": "2k", "output_format": "png"}
for i, p in enumerate(refs): body["input_image" + ("" if i == 0 else f"_{i+1}")] = b64(p)
urls = run("text-to-image/flux-2-klein", body)
```

## 4. Google Gemini direto (GEMINI_API_KEY) — aceita 2:1?

**NÃO.** Lista fixa, sem 2:1 nem tamanho custom. Testado em 2026-09-14 (retorna 400, sem custo):

- `POST /v1beta/models/gemini-2.5-flash-image:generateContent` com `generationConfig.imageConfig.aspectRatio="2:1"` →
  `400: aspect_ratio must be one of '1:1','1:4','1:8','2:3','3:2','3:4','4:1','4:3','4:5','5:4','8:1','9:16','16:9','21:9'`
- `gemini-3-pro-image-preview` (mesmo endpoint, `imageSize:"2K"`) → mesma lista, mesmo erro.
- `POST /v1beta/interactions` com `gemini-3.1-flash-lite-image`, `response_format.aspect_ratio="2:1"` → `invalid_request`, lista: `1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, 1:8, 8:1, 1:4, 4:1`.

Modelos de imagem disponíveis na chave: `gemini-2.5-flash-image`, `gemini-3-pro-image-preview`, `gemini-3-pro-image`, `gemini-3.1-flash-image-preview`, `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image`.

Resoluções por ratio (doc oficial): 3 Pro Image 21:9 → 1584×672 (1K) / 3168×1344 (2K) / **6336×2688 (4K)**; 16:9 → 5504×3072 (4K). `image_size` tem que ser `"1K"|"2K"|"4K"` com K maiúsculo. Refs: até 14 imagens (3 Pro: 6 objetos + 5 personagens + 3 estilo; 3.1 Flash: 10 + 4), inline base64 `{"type":"image","mime_type":...,"data":...}`. Por default o output copia o tamanho da ref de entrada.

## 5. Recomendação para panorama 2:1 multi-referência

Só **quatro** rotas dão 2:1 nativo na Freepik: **Flux 2 Klein** (4 refs, 2048×1024 medido), **GPT Image 2 Edit** (16 refs, até 4k), **Flux Kontext Max** (4 refs por URL, ~1MP) e **Flux 2 Pro** (4 refs base64, `width/height` livres mas teto 1440 → 1440×720, abaixo do Klein 2k — por isso fora da lista principal). Nenhuma Gemini/Seedream dá 2:1.

1. **Principal — GPT Image 2 Edit** (`text-to-image/gpt-image-2-edit`, `aspect_ratio: horizontal_2_1`, `resolution: 4k`, `quality: high`, 4–6 refs em `reference_images`). Único com 2:1 nativo em resolução alta e que aceita todas as 4–6 fotos. Ponto de atenção: preço por output no tier `high` (6× `low`) — prototipar em `low`/`1k`, finalizar em `high`/`4k`. Confirmar px reais do 4k×2:1 com 1 chamada barata (`quality: low`).
2. **Barato / rascunho — Flux 2 Klein** (`horizontal_2_1`, `2k` → 2048×1024, 4 refs base64, ~10 cr, ~3 s). Validado nesta sessão: auth, fluxo assíncrono e tamanho de saída em 1k e 2k (sem refs — o envio de `input_image*` ainda não foi testado). Depois upscale 2× para 4096×2048 via `POST /v1/ai/image-upscaler` (ou `image-upscaler-precision-v2`; ambos com `GET .../{task-id}` — paths confirmados no índice da doc). Serve para iterar prompt antes de gastar no GPT.
3. **Fallback qualidade sem 2:1 — Nano Banana Pro** (Gemini 3 Pro Image, 14 refs por URL, `21:9` @`4K` ≈ 6336×2688) ou **Seedream 5 Pro Edit** (10 refs, `cinematic_21_9` @2k ≈ 3062×1312). Gerar em 21:9 e converter para 2:1 por **outpaint vertical** (`POST /v1/ai/image-expand/seedream-v4-5`, `/v1/ai/image-expand/flux-pro` ou `/v1/ai/image-expand/ideogram` — paths confirmados no índice da doc, parâmetros não pesquisados) ou por crop lateral (21:9 → 2:1 perde ~14 % da largura — ruim para equiretangular, que precisa fechar 360°; preferir expandir em altura). Nano Banana exige refs em **URL pública** (subir as fotos antes: GitHub raw, R2, etc.).
4. **Gemini direto**: mesma restrição (só 21:9 / 16:9), mas mais barato por token e 14 refs inline base64 — bom para a etapa de "entender a sala" e gerar 21:9 @4K; ainda precisa do passo de outpaint para 2:1.

Observação para equiretangular: nenhum desses modelos garante costura 360° (borda esquerda = borda direita). Planejar pós-processo (blend das bordas / inpaint da emenda) independente do modelo.

# fotos3d — ordinary room photos → 360° room

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

Version 1.0.0. Takes 4–6 regular photos of the same room (or just a text description) and generates a photorealistic **2:1 equirectangular panorama (4096×2048)** that faithfully represents the property and that you can rotate in a 360 viewer, like a virtual tour. No 360 camera, scan, or 3D software needed.

> This is **AI reconstruction**, not measurement: areas that no photo shows are conservatively inferred. It is useful for real estate marketing, previews, virtual tour content, and input for AI video. It does not replace a LiDAR scan.

## 📖 User Guide

Complete guide (landing page + step-by-step): **https://inematds.github.io/fotos3d/guia/en/**

Based on the tutorial "Turn Multiple Property Photos Into a 360° Interior Image With Codex" (AI Video Lab). The difference: the part the tutorial leaves out (which image model generates the 360) is solved and tested here.

## How it works

```
photos (or subject) → vision (Gemini) understands the room → conservative prompt
→ image model with the photos as references, native 2:1
→ checks (exact ratio, ≥4096×2048, seam score) → seam smoothing → PNG + report
```

Models tested in the same room (Robie House, 6 actual photos):

| id | provider | native 2:1 | result | cost |
|---|---|---|---|---|
| `flux-klein` (default) | Freepik/Magnific | yes (2048×1024, resampled to 4096) | real equirectangular, very faithful | 10 credits |
| `gpt-image-2` | Freepik/Magnific | yes, up to 4K, 16 refs | **best quality**: correct spherical projection, good seam (8), ~80 s | ~45–90 credits |
| `or-gemini-pro` | OpenRouter | no (16:9 → 2:1) | plausible 360, less faithful (changed rug and windows), poor seam | ~US$0.13 |
| `or-gemini-flash` | OpenRouter | no | tends to come out wide-angle, not 360 | ~US$0.04 |

## Usage

```bash
cd ~/projetos/fotos3d
pip install -r requirements.txt

# from photos
python3 -m engine.pipeline /path/to/room-photos --nome sala-302

# from a subject (AI creates 5 consistent photos and then the 360)
python3 -m engine.pipeline --assunto "modern living room, gray L-shaped sofa, large window, light wood floor" --nome demo

# web interface (upload, progress, 360 viewer, gallery)
uvicorn web.app:app --port 8360   # opens http://127.0.0.1:8360
```

Output in `~/projetos/output/fotos3d/<nome>/`: `<nome>-360.png`, `analise.json`, `prompt.txt`, `relatorio.json`, `fotos/`.

Standalone viewer: open `viewer/index.html` in a browser and drag the PNG.

## Skill (Claude Code)

`skill/property-360/SKILL.md` — install with `ln -s ~/projetos/fotos3d/skill/property-360 ~/.claude/skills/property-360`. Then: *"use the property-360 skill on the photos in folder X"*.

## Keys

Loaded at runtime from `~/projetos/wifi/.env`: `MAGNIFIC_API_KEY` (Freepik), `GEMINI_API_KEY` (vision), `OPENROUTER_API_KEY` (optional). Nothing is copied.

## Tests

```bash
python3 -m pytest -q tests
```

## Sample

`samples/sala/` — 6 photos of the Robie House living room (Frank Lloyd Wright), Wikimedia Commons, photo by w_lemay, CC BY-SA 2.0.

## License

MIT.

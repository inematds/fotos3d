# fotos3d — fotos comunes de una habitación → sala 360°

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

Versión 1.0.0. Toma 4–6 fotos normales de un mismo ambiente (o solo una descripción en texto) y genera una panorámica **equirectangular 2:1 (4096×2048)** fotorrealista, fiel al inmueble, que puedes girar en un visor 360 como en un tour virtual. Sin cámara 360, sin escaneo, sin software 3D.

> Es una **reconstrucción con IA**, no una medición: las áreas que no aparecen en ninguna foto se infieren de forma conservadora. Sirve para marketing inmobiliario, vistas previas, contenido para tours virtuales y material de entrada para video con IA. No reemplaza un escaneo LiDAR.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/fotos3d/guia/es/**

Basado en el tutorial "Turn Multiple Property Photos Into a 360° Interior Image With Codex" (AI Video Lab). La diferencia: aquí ya está resuelta y probada la pieza que el tutorial oculta (qué modelo de imagen genera la 360).

## Cómo funciona

```
fotos (o tema) → visión (Gemini) entiende la habitación → prompt conservador
→ modelo de imagen con las fotos como referencia, 2:1 nativo
→ comprobaciones (ratio exacto, ≥4096×2048, score de costura) → suavizado de la costura → PNG + informe
```

Modelos probados en la misma habitación (Robie House, 6 fotos reales):

| id | proveedor | 2:1 nativo | resultado | costo |
|---|---|---|---|---|
| `flux-klein` (predeterminado) | Freepik/Magnific | sí (2048×1024, remuestreado a 4096) | equirectangular real, muy fiel | 10 créditos |
| `gpt-image-2` | Freepik/Magnific | sí, hasta 4K, 16 refs | **mejor calidad**: proyección esférica correcta, buena costura (8), ~80 s | ~45–90 créditos |
| `or-gemini-pro` | OpenRouter | no (16:9 → 2:1) | 360 plausible, menos fiel (cambió la alfombra y las ventanas), costura deficiente | ~US$0,13 |
| `or-gemini-flash` | OpenRouter | no | tiende a salir gran angular, no 360 | ~US$0,04 |

## Uso

```bash
cd ~/projetos/fotos3d
pip install -r requirements.txt

# con fotos
python3 -m engine.pipeline /caminho/fotos-da-sala --nome sala-302

# por tema (la IA crea 5 fotos coherentes y luego la 360)
python3 -m engine.pipeline --assunto "sala moderna, sofá cinza em L, janela grande, piso de madeira clara" --nome demo

# interfaz web (carga, progreso, visor 360, galería)
uvicorn web.app:app --port 8360   # abre http://127.0.0.1:8360
```

Salida en `~/projetos/output/fotos3d/<nome>/`: `<nome>-360.png`, `analise.json`, `prompt.txt`, `relatorio.json`, `fotos/`.

Visor independiente: abre `viewer/index.html` en el navegador y arrastra el PNG.

## Skill (Claude Code)

`skill/property-360/SKILL.md` — instala con `ln -s ~/projetos/fotos3d/skill/property-360 ~/.claude/skills/property-360`. Después: *"usa la skill property-360 en las fotos de la carpeta X"*.

## Claves

Se cargan en tiempo de ejecución desde `~/projetos/wifi/.env`: `MAGNIFIC_API_KEY` (Freepik), `GEMINI_API_KEY` (visión), `OPENROUTER_API_KEY` (opcional). No se copia nada.

## Pruebas

```bash
python3 -m pytest -q tests
```

## Muestra

`samples/sala/` — 6 fotos de la sala de Robie House (Frank Lloyd Wright), Wikimedia Commons, foto de w_lemay, CC BY-SA 2.0.

## Licencia

MIT.

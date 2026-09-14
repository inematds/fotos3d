"""Etapa 2: da análise para o prompt de geração da panorâmica."""
from __future__ import annotations

REGRAS = """Create ONE seamless 360-degree EQUIRECTANGULAR panorama (spherical projection, like a Google Street View / 360 camera export: 2:1 aspect ratio, full 360° horizontal × 180° vertical field of view) of the EXACT room shown in the reference photos. Camera at the center of the room at eye level (1.5 m). Horizon line exactly at the vertical middle; the floor fills the bottom half and stretches/curves toward the bottom edge, the ceiling fills the top half and converges toward the top edge; straight horizontal lines (skirting, ceiling edges, window sills) appear as gentle curves, vertical lines stay vertical. The four walls of the room must ALL be visible across the width — this is NOT a wide-angle photo, it is the whole room unwrapped.

Strict rules:
- Preserve the real property: same walls, doors, windows, furniture, materials, colors and lighting as the references. Do not redesign, do not restage, do not add decoration.
- Every piece of furniture, door and window appears exactly ONCE, in its true relative position. No duplicates.
- Consistent architecture: straight vertical lines, plausible room geometry, floor at the bottom half, ceiling at the top half.
- The left and right edges must connect perfectly (continuous wall/floor/ceiling across the wrap).
- Unseen areas: continue the existing walls, floor and ceiling conservatively; plain wall is preferred over invented objects.
- Realistic interior real-estate photography, natural lighting matching the references, sharp, high detail.
- No people, no text, no watermark, no borders, no fisheye circles, no split frames.

Room description (clockwise from the center):
"""


def montar_prompt(analise: dict) -> str:
    desc = analise.get("descricao_360") or ""
    extras = []
    if analise.get("iluminacao"):
        extras.append(f"Lighting: {analise['iluminacao']}.")
    if analise.get("areas_nao_vistas"):
        extras.append(f"Unseen areas (fill conservatively): {analise['areas_nao_vistas']}.")
    return REGRAS + desc + "\n" + " ".join(extras)


def prompt_reforco_costura(base: str) -> str:
    return base + "\nIMPORTANT: the image wraps horizontally — the far right edge continues into the far left edge with identical wall, floor and ceiling; place a plain wall section across the wrap point, never a window or a piece of furniture."

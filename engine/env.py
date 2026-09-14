"""Carrega chaves em runtime dos .env padrão (nunca copia valores)."""
from __future__ import annotations

import os
from pathlib import Path

ENV_FILES = [Path.home() / "projetos/wifi/.env", Path.home() / "projetos/openpcbotv2/.env"]
OUTPUT_DIR = Path(os.environ.get("FOTOS3D_OUTPUT", Path.home() / "projetos/output/fotos3d"))


def load_env() -> None:
    for f in ENV_FILES:
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and v and k not in os.environ:
                os.environ[k] = v


def key(name: str) -> str:
    load_env()
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"{name} não encontrada nos .env padrão")
    return v

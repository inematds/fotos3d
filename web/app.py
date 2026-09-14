"""Interface web local do fotos3d: upload de fotos ou assunto → panorâmica 360 → viewer."""
from __future__ import annotations

import json
import re
import shutil
import threading
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from engine.env import OUTPUT_DIR
from engine.pipeline import rodar
from engine.providers import DEFAULT, MODELOS

app = FastAPI(title="fotos3d")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATIC = Path(__file__).parent / "static"
UPLOADS = OUTPUT_DIR / "_uploads"
JOBS: dict[str, dict] = {}


def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", s.strip().lower()).strip("-")
    return s or f"sala-{int(time.time())}"


def _run(job_id: str, **kw) -> None:
    job = JOBS[job_id]

    def prog(msg: str) -> None:
        job["log"].append(msg)

    try:
        job["status"] = "rodando"
        r = rodar(progresso=prog, **kw)
        job["resultado"] = r
        job["status"] = "pronto"
    except Exception as e:  # noqa: BLE001
        job["status"] = "erro"
        job["erro"] = str(e)
        job["log"].append(f"ERRO: {e}")


@app.get("/api/modelos")
def modelos():
    return {"default": DEFAULT, "modelos": [{"id": k, "nome": v[1], "custo": v[2], "ratio": v[3]} for k, v in MODELOS.items()]}


@app.post("/api/jobs")
async def criar_job(nome: str = Form(...), modelo: str = Form(DEFAULT), size: str = Form("2K"),
                    assunto: str = Form(""), pasta: str = Form(""), fotos: list[UploadFile] = File(default=[])):
    if modelo not in MODELOS:
        raise HTTPException(400, "modelo desconhecido")
    nome = _slug(nome)
    caminhos: list[Path] = []
    if pasta:
        p = Path(pasta).expanduser()
        if not p.is_dir():
            raise HTTPException(400, f"pasta não encontrada: {pasta}")
        caminhos = sorted(x for x in p.iterdir() if x.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
    elif fotos:
        d = UPLOADS / nome
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        for i, f in enumerate(fotos, 1):
            ext = Path(f.filename or "x.jpg").suffix.lower() or ".jpg"
            dest = d / f"{i:02d}{ext}"
            dest.write_bytes(await f.read())
            caminhos.append(dest)
    if not caminhos and not assunto.strip():
        raise HTTPException(400, "envie fotos, uma pasta ou um assunto")
    job_id = uuid.uuid4().hex[:8]
    JOBS[job_id] = {"id": job_id, "nome": nome, "status": "na fila", "log": [], "resultado": None, "criado": time.time()}
    threading.Thread(target=_run, args=(job_id,), kwargs=dict(nome=nome, fotos=caminhos or None, assunto=assunto.strip() or None,
                                                              modelo=modelo, image_size=size), daemon=True).start()
    return {"id": job_id, "nome": nome}


@app.get("/api/jobs/{job_id}")
def job(job_id: str):
    j = JOBS.get(job_id)
    if not j:
        raise HTTPException(404)
    out = dict(j)
    if j["resultado"]:
        out["panorama_url"] = f"/out/{j['nome']}/{Path(j['resultado']['panorama']).name}"
    return out


@app.get("/api/galeria")
def galeria():
    itens = []
    for d in sorted(OUTPUT_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        rel = d / "relatorio.json"
        if d.is_dir() and rel.exists():
            r = json.loads(rel.read_text())
            pano = Path(r["panorama"])
            if pano.exists():
                itens.append({"nome": r["nome"], "modelo": r["modelo"], "tipo": r.get("tipo_comodo"), "url": f"/out/{d.name}/{pano.name}",
                              "costura": r["checagem"]["seam_status"], "score": r["checagem"]["seam_score"],
                              "fotos": [f"/out/{d.name}/fotos/{Path(f).name}" for f in r["fotos"] if (d / "fotos" / Path(f).name).exists()]})
    return itens


@app.delete("/api/galeria/{nome}")
def apagar(nome: str):
    d = OUTPUT_DIR / _slug(nome)
    if not d.is_dir():
        raise HTTPException(404)
    shutil.rmtree(d)
    return {"ok": True}


app.mount("/out", StaticFiles(directory=str(OUTPUT_DIR)), name="out")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/", StaticFiles(directory=str(STATIC)), name="static")

"""Kamifuda web app — FastAPI entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.card import THEMES, CardRequest, render_card

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="紙札 Kamifuda",
    description="一言を、そのまま共有できる画像カードにする小さなツール。",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

MAX_TEXT = 200
MAX_ATTR = 60


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"themes": list(THEMES.keys())},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/card")
async def create_card(
    text: str = Form(...),
    attribution: str = Form(""),
    theme: str = Form("mist"),
) -> Response:
    text = text.strip()
    attribution = attribution.strip()
    if not text:
        raise HTTPException(status_code=400, detail="本文を入力してください")
    if len(text) > MAX_TEXT:
        raise HTTPException(status_code=400, detail=f"本文は{MAX_TEXT}文字以内にしてください")
    if len(attribution) > MAX_ATTR:
        raise HTTPException(status_code=400, detail=f"出典は{MAX_ATTR}文字以内にしてください")
    if theme not in THEMES:
        raise HTTPException(status_code=400, detail="不明なテーマです")

    png = render_card(CardRequest(text=text, attribution=attribution, theme=theme))
    return Response(
        content=png,
        media_type="image/png",
        headers={"Content-Disposition": 'inline; filename="kamifuda.png"'},
    )

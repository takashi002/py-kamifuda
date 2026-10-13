"""Render quote cards as PNG images with Pillow."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1200
HEIGHT = 630

THEMES: dict[str, dict[str, tuple[int, int, int]]] = {
    "mist": {
        "bg_top": (232, 240, 236),
        "bg_bottom": (214, 226, 222),
        "ink": (28, 43, 42),
        "muted": (74, 98, 94),
        "accent": (45, 122, 111),
        "rule": (45, 122, 111),
    },
    "ink": {
        "bg_top": (24, 32, 40),
        "bg_bottom": (14, 20, 28),
        "ink": (236, 240, 238),
        "muted": (156, 170, 168),
        "accent": (120, 196, 176),
        "rule": (120, 196, 176),
    },
    "sun": {
        "bg_top": (255, 244, 230),
        "bg_bottom": (255, 228, 196),
        "ink": (62, 36, 18),
        "muted": (140, 96, 58),
        "accent": (196, 92, 48),
        "rule": (196, 92, 48),
    },
}

FONT_CANDIDATES = [
    Path(__file__).resolve().parent / "static" / "fonts" / "NotoSansJP.ttf",
    Path("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]


@dataclass
class CardRequest:
    text: str
    attribution: str = ""
    theme: str = "mist"


def resolve_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    # Prefer wrapping on whitespace; for CJK, wrap by character count.
    if any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in text):
        lines: list[str] = []
        current = ""
        for ch in text.replace("\r\n", "\n"):
            if ch == "\n":
                lines.append(current)
                current = ""
                continue
            trial = current + ch
            if draw.textlength(trial, font=font) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
        return lines or [""]

    paragraphs = text.replace("\r\n", "\n").split("\n")
    lines = []
    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append("")
            continue
        # Approximate wrap then refine with measured width.
        approx = max(8, int(max_width / max(font.size * 0.55, 1)))
        for rough in textwrap.wrap(paragraph, width=approx) or [""]:
            words = rough.split(" ")
            current = words[0] if words else ""
            for word in words[1:]:
                trial = f"{current} {word}"
                if draw.textlength(trial, font=font) <= max_width:
                    current = trial
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
    return lines or [""]


def render_card(req: CardRequest) -> bytes:
    theme = THEMES.get(req.theme, THEMES["mist"])
    image = Image.new("RGB", (WIDTH, HEIGHT), theme["bg_top"])
    draw = ImageDraw.Draw(image)

    # Soft vertical wash
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = tuple(
            int(theme["bg_top"][i] * (1 - t) + theme["bg_bottom"][i] * t) for i in range(3)
        )
        draw.line([(0, y), (WIDTH, y)], fill=color)

    # Quiet margin frame
    margin = 48
    draw.rectangle(
        [margin, margin, WIDTH - margin, HEIGHT - margin],
        outline=theme["rule"],
        width=2,
    )
    draw.rectangle(
        [margin + 10, margin + 10, WIDTH - margin - 10, HEIGHT - margin - 10],
        outline=(*theme["rule"],),
        width=1,
    )

    brand_font = resolve_font(28)
    quote_font = resolve_font(54)
    attr_font = resolve_font(28)

    draw.text((margin + 36, margin + 28), "紙札", font=brand_font, fill=theme["accent"])

    body = (req.text or "").strip() or "ここに一言を書く"
    max_text_width = WIDTH - (margin + 36) * 2
    lines = _wrap_text(body, quote_font, max_text_width, draw)
    line_height = int(quote_font.size * 1.35)
    block_height = line_height * len(lines)
    start_y = (HEIGHT - block_height) // 2 - 10

    for i, line in enumerate(lines[:8]):
        draw.text(
            (margin + 36, start_y + i * line_height),
            line,
            font=quote_font,
            fill=theme["ink"],
        )

    attribution = (req.attribution or "").strip()
    if attribution:
        label = f"— {attribution}"
        draw.text(
            (margin + 36, HEIGHT - margin - 70),
            label,
            font=attr_font,
            fill=theme["muted"],
        )

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()

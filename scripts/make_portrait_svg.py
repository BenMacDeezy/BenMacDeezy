#!/usr/bin/env python3
"""
Embed the actual (background-removed, contrast-enhanced) photo into a terminal-
style card SVG -- instead of converting it to character-art, which two rounds
of feedback confirmed doesn't read as a recognizable likeness at any resolution
that still fits a README. This guarantees it looks like the actual photo.

Base64-embeds the PNG directly (self-contained, no external file dependency).
Reveal is a single CSS fade/rise (finite, one-shot, no loop) -- same proven
mechanism as the heatmap.
"""
import base64
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "ben-portrait.svg")
USER = os.environ.get("GH_PROFILE_USER", "BenMacDeezy").lower()

PAD = 20
TITLEBAR_H = 30
IMG_W = 340

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"

STATIC = bool(os.environ.get("STATIC"))
FADE_DUR = 0.6

im = Image.open(SRC)
img_h = round(IMG_W * im.height / im.width)

with open(SRC, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("ascii")

canvas_w = IMG_W + PAD * 2
canvas_h = TITLEBAR_H + img_h + PAD * 2

css = f"""
@keyframes fadein {{
  from {{ opacity: 0; transform: translateY(6px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
.photo {{ animation: fadein {FADE_DUR:.2f}s ease-out both; }}
""".strip()

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
    f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">',
]
if not STATIC:
    parts.append(f'<style>{css}</style>')
parts.append('<defs>'
             f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient>'
             f'<clipPath id="imgclip"><rect x="{PAD}" y="{TITLEBAR_H+PAD}" width="{IMG_W}" '
             f'height="{img_h}" rx="6"/></clipPath>'
             '</defs>')
parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" '
             f'fill="none" stroke="{FRAME}" stroke-width="1"/>')
parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{canvas_w/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">{USER}@github: ~$ open portrait.png</text>')

cls = "" if STATIC else ' class="photo"'
parts.append(f'<g{cls} clip-path="url(#imgclip)">')
parts.append(f'<image x="{PAD}" y="{TITLEBAR_H+PAD}" width="{IMG_W}" height="{img_h}" '
             f'href="data:image/png;base64,{b64}" preserveAspectRatio="xMidYMid slice"/>')
parts.append('</g>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", canvas_w, "x", canvas_h)

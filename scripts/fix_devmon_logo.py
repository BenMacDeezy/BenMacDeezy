#!/usr/bin/env python3
"""
Rebuild the devmon logo without the flattened raster card (which baked in
opaque white corners around its rounded-rect shape) or any card/background at
all -- just the actual pixel-art creature sprite + text, on a fully transparent
canvas, so it composites cleanly wherever it's placed (our profile README, the
devmon repo's own README, dark or light backgrounds).

The clean 64x64 transparent sprite is extracted from devmon's own
art/logo/devmon-logo.svg (which composes the sprite + real <text> elements --
the flat .png export is the thing that's broken, not the source art).
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SPRITE = os.path.join(HERE, "..", "devmon-sprite.png")
OUT = os.path.join(HERE, "..", "devmon-logo.png")

SPRITE_SCALE = 4  # 64x64 -> 256x256, nearest-neighbor to keep pixel-art crisp
PAD_TOP = 8
GAP = 16
TITLE_SIZE = 46
TAG_SIZE = 17

TITLE_COLOR = (232, 236, 244, 255)   # #e8ecf4, matches source SVG
TAG_COLOR = (59, 130, 246, 255)      # #3b82f6, matches source SVG

sprite = Image.open(SPRITE).convert("RGBA")
sprite = sprite.resize((sprite.width * SPRITE_SCALE, sprite.height * SPRITE_SCALE), Image.NEAREST)

title_font = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", TITLE_SIZE)
tag_font = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", TAG_SIZE)

tmp = Image.new("RGBA", (10, 10))
d = ImageDraw.Draw(tmp)
title_bbox = d.textbbox((0, 0), "DevMon", font=title_font)
tag_text = "[≡] CODE. BATTLE. EVOLVE."
tag_bbox = d.textbbox((0, 0), tag_text, font=tag_font)

canvas_w = max(sprite.width, title_bbox[2] - title_bbox[0], tag_bbox[2] - tag_bbox[0]) + 40
canvas_h = PAD_TOP + sprite.height + GAP + (title_bbox[3] - title_bbox[1]) + 10 + (tag_bbox[3] - tag_bbox[1]) + 10

canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
canvas.alpha_composite(sprite, ((canvas_w - sprite.width) // 2, PAD_TOP))

d = ImageDraw.Draw(canvas)
y = PAD_TOP + sprite.height + GAP
d.text((canvas_w / 2, y), "DevMon", font=title_font, fill=TITLE_COLOR, anchor="ma")
y += (title_bbox[3] - title_bbox[1]) + 14
d.text((canvas_w / 2, y), tag_text, font=tag_font, fill=TAG_COLOR, anchor="ma")

canvas.save(OUT)
print("wrote", OUT, canvas.size)

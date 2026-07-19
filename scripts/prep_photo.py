import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

# 1. cut out the subject
cut = remove(Image.open(INP).convert("RGBA"))
rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])                 # 0 = background

# 2. local-contrast the luminance (CLAHE)
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
gray = clahe.apply(gray)

# a touch of global lift so the face sits in the sparse end of the ramp
gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=18)

# 3. paste onto white using the alpha mask (hard-threshold first so faint
#    background matting doesn't ghost through, then feather a hair to avoid a halo)
ALPHA_FLOOR = 60
alpha = np.where(alpha < ALPHA_FLOOR, 0, alpha).astype(np.uint8)
mask = (alpha.astype(np.float32) / 255.0)
mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
out = gray.astype(np.float32) * mask + 255.0 * (1.0 - mask)
out = np.clip(out, 0, 255).astype(np.uint8)

# 4. crop to the subject's bounding box (plus a small margin) -- source photos
#    often have a lot of empty space around the subject, which just wastes
#    resolution once this gets squeezed down to a coarse character grid.
ys, xs = np.where(alpha > 0)
if len(ys):
    pad = 24
    y0, y1 = max(0, ys.min() - pad), min(out.shape[0], ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(out.shape[1], xs.max() + pad)
    out = out[y0:y1, x0:x1]

Image.fromarray(out, mode="L").save(OUT)
print("wrote", OUT, out.shape)

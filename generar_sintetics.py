"""
generar_sintetics.py
Genera '=' i ':' sintetics (ja que HASY no els te).
Son formes molt simples: podem generar-ne milers amb variabilitat.
"""
import os
import random
import numpy as np
from PIL import Image, ImageDraw

random.seed(42)
np.random.seed(42)

DESTI = os.path.expanduser('~/Desktop/TDR-github/dades_sintetiques')
N_PER_CLASSE = 800
MID = 200

def dibuixar_igual(draw, cx, cy, ample, gruix, sep):
    draw.line([(cx-ample/2, cy-sep/2), (cx+ample/2, cy-sep/2)], fill=0, width=gruix)
    draw.line([(cx-ample/2, cy+sep/2), (cx+ample/2, cy+sep/2)], fill=0, width=gruix)

def dibuixar_dospunts(draw, cx, cy, radi, sep):
    draw.ellipse([cx-radi, cy-sep/2-radi, cx+radi, cy-sep/2+radi], fill=0)
    draw.ellipse([cx-radi, cy+sep/2-radi, cx+radi, cy+sep/2+radi], fill=0)

def generar(desti, prefix, funcio, n):
    os.makedirs(desti, exist_ok=True)
    for i in range(n):
        img = Image.new('L', (MID, MID), color=255)
        draw = ImageDraw.Draw(img)
        cx = MID/2 + random.randint(-8, 8)
        cy = MID/2 + random.randint(-8, 8)
        if prefix == 'igual':
            ample = random.randint(90, 140)
            gruix = random.randint(6, 14)
            sep = random.randint(30, 60)
            dibuixar_igual(draw, cx, cy, ample, gruix, sep)
        else:
            radi = random.randint(8, 16)
            sep = random.randint(60, 90)
            dibuixar_dospunts(draw, cx, cy, radi, sep)

        angle = random.uniform(-10, 10)
        img = img.rotate(angle, fillcolor=255, resample=Image.BILINEAR)

        arr = np.array(img)
        mask = arr < 200
        if mask.any():
            ys, xs = np.where(mask)
            img = img.crop((int(xs.min()), int(ys.min()), int(xs.max())+1, int(ys.max())+1))

        w, h = img.size
        mida_max = max(w, h)
        pad = max(2, int(mida_max * 0.15))
        canvas = Image.new('L', (mida_max + 2*pad, mida_max + 2*pad), color=255)
        canvas.paste(img, ((mida_max - w)//2 + pad, (mida_max - h)//2 + pad))
        canvas = canvas.resize((28, 28), Image.LANCZOS)
        canvas.save(os.path.join(desti, f'sint_{prefix}_{i:04d}.png'))

generar(os.path.join(DESTI, '='), 'igual', dibuixar_igual, N_PER_CLASSE)
generar(os.path.join(DESTI, 'div'), 'div', dibuixar_dospunts, N_PER_CLASSE)
print(f"Fet! {N_PER_CLASSE} imatges de '=' i {N_PER_CLASSE} de ':' a {DESTI}")

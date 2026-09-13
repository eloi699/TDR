"""
test_model_v2.py
Test REALISTA: fa servir la mateixa funcio que l'app (analitzar_imatge),
que prova 3 orientacions. I prova TOTES les fotos, no nomes 5.
"""
import glob
import os

import cv2
import numpy as np
from tensorflow.keras.models import load_model
from motor import analitzar_imatge

CLASSES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
           '+', '-', 'x', ':', '=']

DADES_ELOI = os.path.expanduser('~/Desktop/python 3/dades_eloi')
MAPATGE = {
    '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9',
    '+':'+','-':'-','x':'x','=':'=',
}

model = load_model('model_matematic.keras')
print("Model carregat. Fent test exhaustiu...\n")

total_glob = 0
encerts_glob = 0
resultats = {}

for carpeta, simbol_esperat in MAPATGE.items():
    ruta = os.path.join(DADES_ELOI, carpeta)
    if not os.path.isdir(ruta):
        continue
    fitxers = sorted(glob.glob(os.path.join(ruta, '*')))
    fitxers = [f for f in fitxers if f.lower().endswith(('.png','.jpg','.jpeg'))]
    if not fitxers:
        continue

    encerts = 0
    for f in fitxers:
        img = cv2.imread(f, cv2.IMREAD_COLOR)
        if img is None:
            continue
        try:
            _, eq, _, _, _ = analitzar_imatge(img, model)
            # eq pot ser un sol caracter o mes. Si comenca amb el nostre, ok
            llegit = eq[0] if eq else '?'
        except Exception as e:
            llegit = '?'
        if llegit == simbol_esperat:
            encerts += 1
        total_glob += 1
    acc = encerts / len(fitxers) * 100 if fitxers else 0
    resultats[simbol_esperat] = (encerts, len(fitxers), acc)
    encerts_glob += encerts
    print(f"  {simbol_esperat!r:4}: {encerts:3}/{len(fitxers):3}  ({acc:5.1f}%)")

print()
print("=== RESUM ===")
for c, (e, n, a) in resultats.items():
    est = "***" if a >= 80 else "   " if a >= 50 else "!! "
    print(f"  {est} {c!r:4}: {a:5.1f}%")

print(f"\nTOTAL: {encerts_glob}/{total_glob} ({encerts_glob/total_glob*100:.1f}%)")

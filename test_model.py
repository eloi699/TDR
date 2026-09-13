"""
test_model.py
Prova el model amb fotos REALS de dades_eloi/ per veure si encerta.
"""
import glob
import os
import random

import cv2
import numpy as np
from tensorflow.keras.models import load_model

from preprocessar import preprocessar_caracter

CLASSES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', 'x', ':', '=']
DADES_ELOI = os.path.expanduser('~/Desktop/python 3/dades_eloi')

random.seed(0)
model = load_model('model_matematic.keras')

# Mapatge carpeta -> simbol (la teva carpeta '-' té fotos de restes, etc.)
MAPATGE = {
    '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
    '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
    '+': '+', '-': '-', 'x': 'x', '=': '=',
}

encerts = 0
total = 0
resultats_per_classe = {}

for carpeta, simbol_esperat in MAPATGE.items():
    ruta = os.path.join(DADES_ELOI, carpeta)
    if not os.path.isdir(ruta):
        print(f"[!] No existeix {ruta}")
        continue

    fitxers = sorted(glob.glob(os.path.join(ruta, '*')))
    fitxers = [f for f in fitxers if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not fitxers:
        continue

    # Agafem fins a 5 aleatoris per classe
    mostra = random.sample(fitxers, min(5, len(fitxers)))
    encerts_classe = 0

    for f in mostra:
        img = cv2.imread(f, cv2.IMREAD_COLOR)
        if img is None:
            continue
        prep = preprocessar_caracter(img)
        pred = model.predict(prep.reshape(1, 28, 28, 1).astype('float32') / 255, verbose=0)[0]
        idx = int(np.argmax(pred))
        conf = pred[idx] * 100
        encert = (CLASSES[idx] == simbol_esperat)
        if encert:
            encerts += 1
            encerts_classe += 1
        total += 1
        marca = "OK " if encert else "ERR"
        print(f"  [{marca}] {os.path.basename(f):35s} esperat {simbol_esperat!r:4} -> predit {CLASSES[idx]!r:4} ({conf:.1f}%)")

    acc = encerts_classe / len(mostra) * 100
    resultats_per_classe[simbol_esperat] = acc

print()
print("=== RESUM PER CLASSE ===")
for c, acc in resultats_per_classe.items():
    estrelles = "***" if acc >= 80 else "   " if acc >= 40 else "!! "
    print(f"  {estrelles} {c!r:4}: {acc:5.1f}%")

if total:
    print(f"\nTotal: {encerts}/{total} ({encerts/total*100:.1f}%)")

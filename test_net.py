"""
test_net.py
Test NET: nomes el model + preprocessar_caracter. Sense detector.
Mesura la qualitat REAL del model amb les meves fotos.
"""
import glob, os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from preprocessar import preprocessar_caracter

CLASSES = ['0','1','2','3','4','5','6','7','8','9','+','-','x',':','=']
DADES = os.path.expanduser('~/Desktop/python 3/dades_eloi')
MAPATGE = {
    '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9',
    '+':'+','-':'-','x':'x','=':'=',
}

model = load_model('model_matematic.keras')
total, encerts = 0, 0
for carpeta, simbol in MAPATGE.items():
    ruta = os.path.join(DADES, carpeta)
    if not os.path.isdir(ruta): continue
    fitxers = sorted(glob.glob(os.path.join(ruta, '*')))
    fitxers = [f for f in fitxers if f.lower().endswith(('.png','.jpg','.jpeg'))]
    ok = 0
    for f in fitxers:
        img = cv2.imread(f)
        if img is None: continue
        prep = preprocessar_caracter(img)
        pred = model.predict(prep.reshape(1,28,28,1).astype('float32')/255, verbose=0)[0]
        idx = int(np.argmax(pred))
        if CLASSES[idx] == simbol: ok += 1
        total += 1
    acc = ok/len(fitxers)*100 if fitxers else 0
    est = "***" if acc >= 80 else "   " if acc >= 50 else "!! "
    print(f"  {est} {simbol!r:4}: {ok:3}/{len(fitxers):3} ({acc:5.1f}%)")
    encerts += ok

print(f"\nTOTAL: {encerts}/{total} ({encerts/total*100:.1f}%)")

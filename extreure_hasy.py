"""
extreure_hasy.py
================
Llegeix el HASYv2 i copia només les imatges dels simbols que ens interessen
a una carpeta 'dades_hasy/' amb la mateixa estructura que 'dades_eloi/'.
"""
import csv
import os
import shutil

HASY_BASE = os.path.expanduser('~/Desktop/python 3/HASYv2')
HASY_LABELS = os.path.join(HASY_BASE, 'hasy-data-labels.csv')
DESTI = os.path.expanduser('~/Desktop/TDR-github/dades_hasy')

MAPA_SIMBOLS = {
    70: '0', 71: '1', 72: '2', 73: '3', 74: '4',
    75: '5', 76: '6', 77: '7', 78: '8', 79: '9',
    113: 'x',
    195: '-',
    196: '+',
    922: 'div',
}

comptadors = {nom: 0 for nom in MAPA_SIMBOLS.values()}

print(f"Llegint {HASY_LABELS}...")
with open(HASY_LABELS, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    files = list(reader)

print(f"Total files al CSV: {len(files)}")

for fila in files:
    symbol_id = int(fila['symbol_id'])
    if symbol_id not in MAPA_SIMBOLS:
        continue

    nom_classe = MAPA_SIMBOLS[symbol_id]
    ruta_origen = os.path.join(HASY_BASE, fila['path'])
    if not os.path.exists(ruta_origen):
        continue

    carpeta_desti = os.path.join(DESTI, nom_classe)
    os.makedirs(carpeta_desti, exist_ok=True)

    nom_fitxer = os.path.basename(fila['path'])
    ruta_desti = os.path.join(carpeta_desti, nom_fitxer)
    shutil.copy2(ruta_origen, ruta_desti)
    comptadors[nom_classe] += 1

print("\n=== RESUM ===")
for nom, n in sorted(comptadors.items()):
    print(f"  {nom:>4}: {n} imatges copiades")
print(f"\nTotal: {sum(comptadors.values())} imatges a {DESTI}")

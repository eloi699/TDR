"""
motor.py
========
Aquest fitxer conté el "cervell" del projecte: el preprocessament de la
imatge, la detecció de caràcters, la predicció amb la IA i la resolució
matemàtica. NO té cap finestra emergent ni `input()`, perquè està pensat
per ser cridat des d'una aplicació (per exemple app.py amb Streamlit).

Si vols fer servir el projecte des de la terminal (sense app visual),
pots seguir fent servir operacions.py tal com el tenies.
"""

import cv2
import numpy as np
import tensorflow as tf

# ATENCIÓ: aquest ordre HA DE SER exactament el mateix que CLASSES
# a entrenament_personalitzat.py. Si canvies l'ordre allà, canvia'l aquí.
ETIQUETES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', 'x', ':']

MODEL_PATH = 'model_matematic.keras'


def carregar_model():
    """Carrega el model entrenat des del disc. Es crida un sol cop a l'app."""
    return tf.keras.models.load_model(MODEL_PATH)


def resoldre_i_explicar(text_equacio):
    """
    Funcio de Tutor: Agafa el text (ex: '5+3', '9-4', '6x2', '12:4'),
    detecta l'operacio, la calcula i l'explica pas a pas.
    Retorna sempre un text (mai None).
    """
    text_net = text_equacio.replace(" ", "")

    operadors = {
        '+': ('sumar', lambda a, b: a + b, 'suma'),
        '-': ('restar', lambda a, b: a - b, 'resta'),
        'x': ('multiplicar', lambda a, b: a * b, 'multiplicacio'),
        ':': ('dividir', lambda a, b: a / b, 'divisio'),
    }

    operador_trobat = None
    for simbol in operadors:
        if simbol in text_net:
            operador_trobat = simbol
            break

    if operador_trobat is None:
        return f"Nomes he llegit caracters ('{text_equacio}'), pero no he detectat cap operador (+, -, x o :)."

    verb, funcio, nom_operacio = operadors[operador_trobat]
    parts = text_net.split(operador_trobat)

    if len(parts) != 2 or parts[0] == '' or parts[1] == '':
        return (f"Error: he detectat el signe '{operador_trobat}', pero l'expressio "
                f"'{text_equacio}' no te dos numeros clars al voltant.")

    try:
        num1 = float(parts[0])
        num2 = float(parts[1])

        if operador_trobat == ':' and num2 == 0:
            return "Error: no es pot dividir per zero."

        resultat = funcio(num1, num2)

        if num1.is_integer(): num1 = int(num1)
        if num2.is_integer(): num2 = int(num2)
        if isinstance(resultat, float) and resultat.is_integer():
            resultat = int(resultat)
        elif isinstance(resultat, float):
            resultat = round(resultat, 2)

        explicacio = "EXPLICACIO PAS A PAS:\n\n"
        explicacio += f"Pas 1: He llegit el simbol '{operador_trobat}', que significa que hem de {verb}.\n"
        explicacio += f"Pas 2: Els nombres de l'operacio son el {num1} i el {num2}.\n"
        explicacio += f"Pas 3: Fem la {nom_operacio}: {num1} {operador_trobat} {num2}.\n\n"
        explicacio += f"El resultat final es: {resultat}"
        return explicacio
    except ValueError:
        return (f"Error: He vist un '{operador_trobat}', pero hi ha un problema llegint "
                f"els numeros (potser he confos una lletra amb un numero).")


def _detectar_rectangles(binari):
    """Troba els rectangles de cada caracter, fusionant els simbols de dos punts (':')."""
    contorns, _ = cv2.findContours(binari, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidats = []
    for c in contorns:
        x, y, w, h = cv2.boundingRect(c)
        if h > 5:
            candidats.append([x, y, w, h])

    if candidats:
        alcada_ref = max(c[3] for c in candidats)

        def es_punt(rect):
            _, _, w, h = rect
            aspecte = w / float(h) if h > 0 else 0
            return h < alcada_ref * 0.35 and 0.5 < aspecte < 1.8

        usats = set()
        fusionats = []
        for i in range(len(candidats)):
            if i in usats or not es_punt(candidats[i]):
                continue
            for j in range(i + 1, len(candidats)):
                if j in usats or not es_punt(candidats[j]):
                    continue
                x1, y1, w1, h1 = candidats[i]
                x2, y2, w2, h2 = candidats[j]
                solapament_horitzontal = min(x1 + w1, x2 + w2) - max(x1, x2)
                amplada_mitjana = (w1 + w2) / 2
                gap_vertical = max(y1, y2) - min(y1 + h1, y2 + h2)
                if solapament_horitzontal > amplada_mitjana * 0.3 and gap_vertical < alcada_ref * 0.9:
                    x_min, y_min = min(x1, x2), min(y1, y2)
                    x_max, y_max = max(x1 + w1, x2 + w2), max(y1 + h1, y2 + h2)
                    fusionats.append([x_min, y_min, x_max - x_min, y_max - y_min])
                    usats.add(i)
                    usats.add(j)
                    break

        if fusionats:
            candidats = [c for idx, c in enumerate(candidats) if idx not in usats] + fusionats

    rectangles = []
    if candidats:
        alcada_maxima = max(c[3] for c in candidats)
        for x, y, w, h in candidats:
            aspecte = w / float(h) if h > 0 else 0
            prou_alt = h >= (alcada_maxima * 0.40)
            sembla_guio = (aspecte > 2.2) and (h >= 5) and (h < alcada_maxima * 0.40)
            if prou_alt or sembla_guio:
                rectangles.append((x, y, w, h))

    return sorted(rectangles, key=lambda r: r[0])


def analitzar_imatge(img_bgr, model):
    """
    Rep una imatge (array BGR d'OpenCV) i el model ja carregat.
    Retorna:
        img_anotada     -> copia de la imatge amb els requadres i etiquetes dibuixats (BGR)
        equacio_llegida -> text amb el que la IA ha llegit (ex: '12:4')
        explicacio      -> text amb la resolucio pas a pas
    """
    img_anotada = img_bgr.copy()

    gris = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    suau = cv2.GaussianBlur(gris, (7, 7), 0)
    _, binari = cv2.threshold(suau, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel_escombra = np.ones((2, 2), np.uint8)
    binari = cv2.morphologyEx(binari, cv2.MORPH_OPEN, kernel_escombra)

    kernel_corro = np.ones((5, 5), np.uint8)
    binari = cv2.morphologyEx(binari, cv2.MORPH_CLOSE, kernel_corro)

    rectangles = _detectar_rectangles(binari)

    equacio_llegida = ""
    for (x, y, w, h) in rectangles:
        roi = binari[y:y + h, x:x + w]
        h_roi, w_roi = roi.shape

        mida_max = max(w_roi, h_roi)
        pad_y = (mida_max - h_roi) // 2 + 4
        pad_x = (mida_max - w_roi) // 2 + 4

        quadrat = cv2.copyMakeBorder(roi, pad_y, pad_y, pad_x, pad_x, cv2.BORDER_CONSTANT, value=0)
        final_ia = cv2.resize(quadrat, (28, 28))
        ia_input = final_ia.reshape(1, 28, 28, 1).astype('float32') / 255

        prediccions = model.predict(ia_input, verbose=0)[0]
        millor_opcio = np.argmax(prediccions)
        confianca = prediccions[millor_opcio] * 100

        caracter_final = ETIQUETES[millor_opcio]
        equacio_llegida += caracter_final

        cv2.rectangle(img_anotada, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img_anotada, f"{caracter_final} ({confianca:.0f}%)", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    explicacio = resoldre_i_explicar(equacio_llegida) if equacio_llegida else \
        "No he detectat cap caracter a la imatge. Prova amb mes llum o mes a prop."

    return img_anotada, equacio_llegida, explicacio

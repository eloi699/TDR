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

import re

import cv2
import numpy as np
import tensorflow as tf

# ATENCIÓ: aquest ordre HA DE SER exactament el mateix que CLASSES
# a entrenament_personalitzat.py. Si canvies l'ordre allà, canvia'l aquí.
ETIQUETES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', 'x', ':', '=']

MODEL_PATH = 'model_matematic.keras'


def carregar_model():
    """Carrega el model entrenat des del disc. Es crida un sol cop a l'app."""
    return tf.keras.models.load_model(MODEL_PATH)


def _formatar_numero(n):
    """Converteix 5.0 -> 5, però deixa 5.5 tal qual."""
    if isinstance(n, float) and n.is_integer():
        return int(n)
    if isinstance(n, float):
        return round(n, 2)
    return n


def resoldre_equacio(text_net):
    """
    Resol una equació de primer grau amb una incògnita 'x' (per exemple
    'x+3=8', '5x=20' o '2x+3=11'). Aquí la 'x' NO vol dir multiplicar,
    sinó que és la incògnita: ho sabem perquè hi ha un signe '=' al text.
    """
    parts = text_net.split('=')
    if len(parts) != 2:
        return (f"Error: he detectat el signe '=', però l'expressió "
                f"'{text_net}' no té una equació clara a cada banda.")

    costat_x, costat_num = parts

    # Si la incògnita és al costat dret (per exemple '11=2x+3'), els girem
    if 'x' not in costat_x and 'x' in costat_num:
        costat_x, costat_num = costat_num, costat_x

    if 'x' not in costat_x or 'x' in costat_num:
        return (f"Error: per ara només sé resoldre equacions amb la incògnita "
                f"'x' a un únic costat (com '2x+3=11'). No he pogut interpretar "
                f"'{text_net}'.")

    coincidencia = re.fullmatch(r'(\d*)x([+-]\d+)?', costat_x)
    if not coincidencia:
        return (f"Error: l'equació '{text_net}' té una forma que encara no sé "
                f"resoldre (de moment: 'x+3=8', '5x=20' o '2x+3=11').")

    coef_text, const_text = coincidencia.groups()
    coeficient = int(coef_text) if coef_text else 1
    constant = int(const_text) if const_text else 0

    try:
        resultat_dreta = float(costat_num)
    except ValueError:
        return f"Error: '{costat_num}' no és un número vàlid a l'altra banda de l'equació."

    if coeficient == 0:
        return "Error: el coeficient de la x no pot ser 0."

    explicacio = "EXPLICACIÓ PAS A PAS (equació de primer grau):\n\n"
    explicacio += f"Tenim l'equació: {costat_x} = {_formatar_numero(resultat_dreta)}\n\n"

    pas = 1
    valor_actual = resultat_dreta

    if constant != 0:
        signe_original = '+' if constant > 0 else '-'
        signe_oposat = '-' if constant > 0 else '+'
        valor_actual = resultat_dreta - constant
        explicacio += (
            f"Pas {pas}: Passem el '{signe_original}{abs(constant)}' a l'altra banda "
            f"canviant-li el signe: {coeficient}x = {_formatar_numero(resultat_dreta)} "
            f"{signe_oposat} {abs(constant)} = {_formatar_numero(valor_actual)}.\n"
        )
        pas += 1

    if coeficient != 1:
        x_valor = valor_actual / coeficient
        explicacio += (
            f"Pas {pas}: Aïllem la x dividint els dos costats pel coeficient "
            f"{coeficient}: x = {_formatar_numero(valor_actual)} / {coeficient} "
            f"= {_formatar_numero(x_valor)}.\n"
        )
    else:
        x_valor = valor_actual
        if pas == 1:
            explicacio += "Pas 1: La incògnita ja està sola en un costat de l'equació.\n"

    explicacio += f"\nEl valor de la incògnita és: x = {_formatar_numero(x_valor)}"
    return explicacio


def resoldre_i_explicar(text_equacio):
    """
    Funció de Tutor: Agafa el text (ex: '5+3', '9-4', '6x2', '12:4', '2x+3=11'),
    detecta si és una equació (hi ha un '=') o una operació normal, la
    resol i n'explica el procediment pas a pas. Retorna sempre un text.
    """
    text_net = text_equacio.replace(" ", "")

    # Si hi ha un '=', és una equació: aquí la 'x' vol dir incògnita, no multiplicar.
    if '=' in text_net:
        return resoldre_equacio(text_net)

    operadors = {
        '+': ('sumar', lambda a, b: a + b, 'suma'),
        '-': ('restar', lambda a, b: a - b, 'resta'),
        'x': ('multiplicar', lambda a, b: a * b, 'multiplicació'),
        ':': ('dividir', lambda a, b: a / b, 'divisió'),
    }

    operador_trobat = None
    for simbol in operadors:
        if simbol in text_net:
            operador_trobat = simbol
            break

    if operador_trobat is None:
        return f"Només he llegit caràcters ('{text_equacio}'), però no he detectat cap operador (+, -, x o :)."

    verb, funcio, nom_operacio = operadors[operador_trobat]
    parts = text_net.split(operador_trobat)

    if len(parts) != 2 or parts[0] == '' or parts[1] == '':
        return (f"Error: he detectat el signe '{operador_trobat}', però l'expressió "
                f"'{text_equacio}' no té dos números clars al voltant.")

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

        explicacio = "EXPLICACIÓ PAS A PAS:\n\n"
        explicacio += f"Pas 1: He llegit el símbol '{operador_trobat}', que significa que hem de {verb}.\n"
        explicacio += f"Pas 2: Els nombres de l'operació són el {num1} i el {num2}.\n"
        explicacio += f"Pas 3: Fem la {nom_operacio}: {num1} {operador_trobat} {num2}.\n\n"
        explicacio += f"El resultat final és: {resultat}"
        return explicacio
    except ValueError:
        return (f"Error: He vist un '{operador_trobat}', però hi ha un problema llegint "
                f"els números (potser he confós una lletra amb un número).")


def _detectar_rectangles(binari):
    """Troba els rectangles de cada caràcter, fusionant els símbols de dos traços (':' i '=')."""
    contorns, _ = cv2.findContours(binari, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidats = []
    for c in contorns:
        x, y, w, h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        # Abans el MORPH_OPEN eliminava el soroll petit, però també trencava
        # traços prims com el '+'. Ara filtrem soroll aquí, per àrea, sense
        # malmetre la forma dels símbols.
        if h > 5 and area > 8:
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

    # --- FUSIÓ DE LES DUES RATLLES (pel símbol '=') ---
    # El signe d'igual es pot detectar com DUES ratlles amples i primes,
    # una a sobre de l'altra (semblants al guió de la resta, però en parella).
    if candidats:
        alcada_ref2 = max(c[3] for c in candidats)
        amplada_imatge2 = binari.shape[1]

        def es_ratlla(rect):
            _, _, w, h = rect
            aspecte = w / float(h) if h > 0 else 0
            return (
                aspecte > 2.2
                and 5 <= h < alcada_ref2 * 0.4
                and w < amplada_imatge2 * 0.5
                and w < alcada_ref2 * 4
            )

        usats2 = set()
        fusionats2 = []
        for i in range(len(candidats)):
            if i in usats2 or not es_ratlla(candidats[i]):
                continue
            for j in range(i + 1, len(candidats)):
                if j in usats2 or not es_ratlla(candidats[j]):
                    continue
                x1, y1, w1, h1 = candidats[i]
                x2, y2, w2, h2 = candidats[j]
                solapament_horitzontal = min(x1 + w1, x2 + w2) - max(x1, x2)
                amplada_mitjana = (w1 + w2) / 2
                gap_vertical = max(y1, y2) - min(y1 + h1, y2 + h2)
                if solapament_horitzontal > amplada_mitjana * 0.5 and 0 <= gap_vertical < alcada_ref2 * 0.6:
                    x_min, y_min = min(x1, x2), min(y1, y2)
                    x_max, y_max = max(x1 + w1, x2 + w2), max(y1 + h1, y2 + h2)
                    fusionats2.append([x_min, y_min, x_max - x_min, y_max - y_min])
                    usats2.add(i)
                    usats2.add(j)
                    break

        if fusionats2:
            candidats = [c for idx, c in enumerate(candidats) if idx not in usats2] + fusionats2

    # --- FUSIÓ DEL '+' TRENCAT EN DOS TROSSOS ---
    # Si el traç horitzontal i el vertical del '+' han quedat com a
    # contorns separats, els ajuntem. Però NOMÉS quan un tros és
    # clarament horitzontal (ample i prim) i l'altre clarament vertical
    # (alt i estret) — no qualsevol parell de trossos petits — i quan el
    # resultat final no sigui més gran que un sol caràcter. Així evitem
    # que es fusionin dígits sencers entre ells per error.
    if candidats:
        alcada_ref3 = max(c[3] for c in candidats)

        def es_barra_horitzontal(rect):
            _, _, w, h = rect
            aspecte = w / float(h) if h > 0 else 0
            return aspecte > 1.3 and h < alcada_ref3 * 0.55

        def es_barra_vertical(rect):
            _, _, w, h = rect
            aspecte = w / float(h) if h > 0 else 0
            return aspecte < 0.75 and w < alcada_ref3 * 0.55

        usats3 = set()
        fusionats3 = []
        for i in range(len(candidats)):
            if i in usats3 or not es_barra_horitzontal(candidats[i]):
                continue
            for j in range(len(candidats)):
                if j == i or j in usats3 or not es_barra_vertical(candidats[j]):
                    continue
                x1, y1, w1, h1 = candidats[i]
                x2, y2, w2, h2 = candidats[j]
                es_toquen = not (x1 + w1 < x2 - 3 or x2 + w2 < x1 - 3 or
                                  y1 + h1 < y2 - 3 or y2 + h2 < y1 - 3)
                x_min, y_min = min(x1, x2), min(y1, y2)
                x_max, y_max = max(x1 + w1, x2 + w2), max(y1 + h1, y2 + h2)
                mida_ok = (x_max - x_min) < alcada_ref3 * 1.2 and (y_max - y_min) < alcada_ref3 * 1.2
                if es_toquen and mida_ok:
                    fusionats3.append([x_min, y_min, x_max - x_min, y_max - y_min])
                    usats3.add(i)
                    usats3.add(j)
                    break

        if fusionats3:
            candidats = [c for idx, c in enumerate(candidats) if idx not in usats3] + fusionats3

    rectangles = []
    if candidats:
        alcada_maxima = max(c[3] for c in candidats)
        amplada_imatge = binari.shape[1]
        for x, y, w, h in candidats:
            aspecte = w / float(h) if h > 0 else 0
            prou_alt = h >= (alcada_maxima * 0.40)
            # Un guió de veritat (el signe '-') mai serà tan ample com mig
            # full de la imatge, ni gaire més ample que l'alçada dels altres
            # caràcters. Si ho és, és molt més probable que sigui una ratlla
            # del quadern o un altre artefacte de la foto, no un signe.
            sembla_guio = (
                aspecte > 2.2
                and (h >= 5)
                and (h < alcada_maxima * 0.40)
                and (w < amplada_imatge * 0.5)
                and (w < alcada_maxima * 4)
            )
            if prou_alt or sembla_guio:
                rectangles.append((x, y, w, h))

    # --- XARXA DE SEGURETAT: DIVIDIR BLOCS MASSA AMPLES ---
    # Si tot i les correccions anteriors un requadre segueix sent molt més
    # ample que alt (senyal que en realitat conté diversos caràcters que
    # es toquen), busquem "valls" (columnes gairebé sense tinta) per
    # partir-lo en trossos més petits.
    rectangles_finals = []
    if rectangles:
        alcada_ref4 = max(r[3] for r in rectangles)
        for (x, y, w, h) in rectangles:
            aspecte = w / float(h) if h > 0 else 0
            if aspecte > 1.6 and h >= alcada_ref4 * 0.4:
                roi = binari[y:y + h, x:x + w]
                densitat = (roi > 0).sum(axis=0)
                llindar = max(1, int(roi.shape[0] * 0.06))
                buida = densitat <= llindar

                trossos = []
                inici = None
                for i, es_buida in enumerate(buida):
                    if not es_buida and inici is None:
                        inici = i
                    elif es_buida and inici is not None:
                        trossos.append((inici, i))
                        inici = None
                if inici is not None:
                    trossos.append((inici, len(buida)))

                trossos = [t for t in trossos if (t[1] - t[0]) > 3]

                if len(trossos) > 1:
                    for (ini, fi) in trossos:
                        rectangles_finals.append((x + ini, y, fi - ini, h))
                    continue

            rectangles_finals.append((x, y, w, h))

    return sorted(rectangles_finals, key=lambda r: r[0])


def _girar_imatge(img, angle_graus):
    """Gira la imatge 90 graus en un sentit o l'altre. angle_graus=0 la deixa igual."""
    if angle_graus == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle_graus == -90:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


def _processar_una_orientacio(img_bgr, model):
    """
    Fa tot el procés (binaritzar, detectar caràcters, llegir-los amb la IA)
    per a UNA orientació concreta de la imatge. Es fa servir per poder
    comparar diverses orientacions i triar la millor.
    """
    img_anotada = img_bgr.copy()

    # --- PREPROCESSAMENT ---
    gris = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    suau = cv2.GaussianBlur(gris, (7, 7), 0)

    # Llindar ADAPTATIU: per a cada píxel, es compara només amb els píxels
    # del seu voltant, no amb tota la imatge. Així una ombra suau al full
    # no es confon amb tinta (a diferència d'un llindar global com Otsu).
    mida_bloc = 41
    constant_c = 15
    binari = cv2.adaptiveThreshold(
        suau, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        mida_bloc,
        constant_c,
    )

    # Kernel de 3x1 (només vertical): tanca petits forats dins d'un mateix
    # caràcter sense poder mai unir dos caràcters veïns.
    kernel_corro = np.ones((3, 1), np.uint8)
    binari = cv2.morphologyEx(binari, cv2.MORPH_CLOSE, kernel_corro)

    # --- DETECCIÓ ---
    rectangles = _detectar_rectangles(binari)

    # Comprovació GEOMÈTRICA (abans de llegir res amb la IA): els caràcters
    # d'una equació normal estan repartits en una línia horitzontal (varien
    # molt en X, poc en Y). Si en aquesta orientació estan repartits més
    # aviat en vertical (un sota l'altre), és un senyal molt fiable que la
    # foto encara està de costat — molt més fiable que mirar si la IA ha
    # llegit "alguna cosa que sembla una equació", perquè uns dígits girats
    # poden confondre el model i, per pura casualitat, generar un text que
    # es pugui resoldre igualment sense tenir cap sentit real.
    if len(rectangles) >= 2:
        centres_x = [x + w / 2 for (x, y, w, h) in rectangles]
        centres_y = [y + h / 2 for (x, y, w, h) in rectangles]
        dispersio_x = max(centres_x) - min(centres_x)
        dispersio_y = max(centres_y) - min(centres_y)
        ben_alineat_horitzontalment = dispersio_x >= dispersio_y
    else:
        # Amb 0 o 1 caràcters no podem saber com estan repartits.
        ben_alineat_horitzontalment = True

    # --- LECTURA IA ---
    equacio_llegida = ""
    confiances = []
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
        confiances.append(confianca)

        caracter_final = ETIQUETES[millor_opcio]
        equacio_llegida += caracter_final

        cv2.rectangle(img_anotada, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img_anotada, f"{caracter_final} ({confianca:.0f}%)", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    conf_mitjana = sum(confiances) / len(confiances) if confiances else 0

    # Puntuació per decidir si aquesta orientació és bona:
    #
    # 1r factor (el més important, amb diferència): si els caràcters estan
    #    repartits en horitzontal, com una línia normal d'escriptura. Això
    #    es comprova de manera geomètrica, sense dependre de la IA.
    # 2n factor: si l'equació llegida es pot RESOLDRE de veritat (dos
    #    números vàlids amb un operador entre ells) — però només fa de
    #    desempat ENTRE orientacions ja ben alineades, mai pot compensar
    #    una orientació que geomètricament ja sabem que és incorrecta.
    # 3r factor: confiança mitjana i longitud del text llegit.
    explicacio_prova = resoldre_i_explicar(equacio_llegida) if equacio_llegida else ""
    es_equacio_valida = bool(equacio_llegida) and not explicacio_prova.startswith(("Error", "Només"))

    bonus_alineacio = 2000 if ben_alineat_horitzontalment else 0
    bonus_validesa = 1000 if es_equacio_valida else 0
    puntuacio = bonus_alineacio + bonus_validesa + conf_mitjana + (len(equacio_llegida) * 2)

    return {
        "img_anotada": img_anotada,
        "equacio_llegida": equacio_llegida,
        "binari": binari,
        "puntuacio": puntuacio,
        "ben_alineat": ben_alineat_horitzontalment,
    }


def analitzar_imatge(img_bgr, model):
    """
    Rep una imatge (array BGR d'OpenCV) i el model ja carregat.
    Prova la imatge en 3 orientacions (normal, girada 90° a la dreta i
    girada 90° a l'esquerra) i es queda amb la que dona un resultat més
    fiable, per no dependre de com s'ha sostingut el mòbil en fer la foto.

    Retorna:
        img_anotada   -> còpia de la imatge (ja orientada correctament) amb
                         els requadres i etiquetes dibuixats (BGR)
        equacio_llegida -> text amb el que la IA ha llegit (ex: '12:4')
        explicacio    -> text amb la resolució pas a pas
        binari        -> imatge en blanc i negre de l'orientació triada (útil per depurar)
        info_depuracio -> llista amb un resum de les 3 orientacions provades
                           (angle, text llegit, puntuació, binari), útil per
                           entendre per què s'ha triat una orientació o una altra
    """
    candidats = []
    for angle in (0, 90, -90):
        img_girada = _girar_imatge(img_bgr, angle)
        resultat = _processar_una_orientacio(img_girada, model)
        resultat["angle"] = angle
        candidats.append(resultat)

    millor = max(candidats, key=lambda r: r["puntuacio"])

    img_anotada = millor["img_anotada"]
    equacio_llegida = millor["equacio_llegida"]
    binari = millor["binari"]

    info_depuracio = [
        {
            "angle": c["angle"],
            "equacio_llegida": c["equacio_llegida"],
            "puntuacio": round(c["puntuacio"], 1),
            "binari": c["binari"],
            "ben_alineat": c["ben_alineat"],
            "triada": c is millor,
        }
        for c in candidats
    ]

    explicacio = resoldre_i_explicar(equacio_llegida) if equacio_llegida else \
        "No he detectat cap caràcter a la imatge. Prova amb més llum o més a prop."

    return img_anotada, equacio_llegida, explicacio, binari, info_depuracio

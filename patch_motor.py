NEW_HELPER = '''
def _classificar_roi(roi, model):
    """Classifica un ROI binaritzat. Retorna (caracter, confianca 0-100)."""
    h_roi, w_roi = roi.shape
    if h_roi == 0 or w_roi == 0:
        return "", 0.0
    mida_max = max(w_roi, h_roi)
    pad_y = (mida_max - h_roi) // 2 + 4
    pad_x = (mida_max - w_roi) // 2 + 4
    quadrat = cv2.copyMakeBorder(roi, pad_y, pad_y, pad_x, pad_x, cv2.BORDER_CONSTANT, value=0)
    final_ia = cv2.resize(quadrat, (28, 28))
    ia_input = final_ia.reshape(1, 28, 28, 1).astype('float32') / 255
    prediccions = model.predict(ia_input, verbose=0)[0]
    idx = int(np.argmax(prediccions))
    return ETIQUETES[idx], prediccions[idx] * 100


'''

NEW_FUNC = '''def _processar_una_orientacio(img_bgr, model):
    img_anotada = img_bgr.copy()

    gris = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    suau = cv2.GaussianBlur(gris, (7, 7), 0)
    mida_bloc = 41
    constant_c = 15
    binari = cv2.adaptiveThreshold(
        suau, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        mida_bloc,
        constant_c,
    )
    kernel_corro = np.ones((3, 1), np.uint8)
    binari = cv2.morphologyEx(binari, cv2.MORPH_CLOSE, kernel_corro)

    rectangles = _detectar_rectangles(binari)

    if rectangles:
        alcada_max_rects = max(h for (_, _, _, h) in rectangles)
        rects_per_alineacio = [r for r in rectangles if r[3] >= alcada_max_rects * 0.5]
    else:
        rects_per_alineacio = []

    if len(rects_per_alineacio) >= 2:
        centres_x = [x + w / 2 for (x, y, w, h) in rects_per_alineacio]
        centres_y = [y + h / 2 for (x, y, w, h) in rects_per_alineacio]
        dispersio_x = max(centres_x) - min(centres_x)
        dispersio_y = max(centres_y) - min(centres_y)
        ben_alineat_horitzontalment = dispersio_x >= dispersio_y
    else:
        ben_alineat_horitzontalment = True

    # Interpretacio A: multi-caracter
    equacio_multi = ""
    conf_multi_list = []
    boxes_multi = []
    for (x, y, w, h) in rectangles:
        roi = binari[y:y + h, x:x + w]
        car, conf = _classificar_roi(roi, model)
        equacio_multi += car
        conf_multi_list.append(conf)
        boxes_multi.append((x, y, w, h, car, conf))
    conf_mitjana_multi = sum(conf_multi_list) / len(conf_multi_list) if conf_multi_list else 0

    # Interpretacio B: un sol caracter (bounding box de TOTS els contorns)
    contorns, _ = cv2.findContours(binari, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contorns_valids = [c for c in contorns if cv2.contourArea(c) > 5]
    equacio_single = ""
    conf_single = 0.0
    box_single = None
    if contorns_valids:
        caixes = [cv2.boundingRect(c) for c in contorns_valids]
        x_min = min(cx for cx, cy, cw, ch in caixes)
        y_min = min(cy for cx, cy, cw, ch in caixes)
        x_max = max(cx + cw for cx, cy, cw, ch in caixes)
        y_max = max(cy + ch for cx, cy, cw, ch in caixes)
        roi_single = binari[y_min:y_max, x_min:x_max]
        if roi_single.size > 0:
            equacio_single, conf_single = _classificar_roi(roi_single, model)
            box_single = (x_min, y_min, x_max, y_max, equacio_single, conf_single)

    # Decisio: si tenim 0-1 rectangles -> single. Si single te molta mes confianca -> single.
    if len(rectangles) <= 1:
        usar_single = True
    elif conf_single > conf_mitjana_multi + 15 and conf_single > 75 and len(equacio_single) == 1:
        usar_single = True
    else:
        usar_single = False

    if usar_single and box_single is not None:
        equacio_llegida = equacio_single
        conf_mitjana = conf_single
        x1, y1, x2, y2, car, conf = box_single
        cv2.rectangle(img_anotada, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img_anotada, f"{car} ({conf:.0f}%)", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        equacio_llegida = equacio_multi
        conf_mitjana = conf_mitjana_multi
        for (x, y, w, h, car, conf) in boxes_multi:
            cv2.rectangle(img_anotada, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img_anotada, f"{car} ({conf:.0f}%)", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

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
'''

with open('motor.py', 'r', encoding='utf-8') as f:
    src = f.read()

start_marker = 'def _processar_una_orientacio(img_bgr, model):'
end_marker = 'def analitzar_imatge(img_bgr, model):'

i = src.index(start_marker)
j = src.index(end_marker)
src = src[:i] + NEW_HELPER + NEW_FUNC + '\n\n' + src[j:]

with open('motor.py', 'w', encoding='utf-8') as f:
    f.write(src)

print("OK! motor.py actualitzat.")

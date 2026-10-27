"""
preprocessar.py
===============
Preprocessament UNIFICAT. Aquesta funcio l'han de fer servir TANT l'app
(motor.py) COM l'entrenament (entrenament_final.py). Aixi el model veu
exactament el mateix a l'entrenament i a l'app real (fi del domain shift).
"""
import cv2
import numpy as np


def binaritzar(img):
    """Converteix una imatge (BGR o gris) a binari: TINTA = BLANC (255), FONS = NEGRE (0)."""
    if len(img.shape) == 3:
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gris = img

    suau = cv2.GaussianBlur(gris, (7, 7), 0)

    binari = cv2.adaptiveThreshold(
        suau, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        41,   # mida_bloc
        15,   # constant_c
    )

    kernel = np.ones((3, 1), np.uint8)
    binari = cv2.morphologyEx(binari, cv2.MORPH_CLOSE, kernel)
    return binari


def retallar_a_28x28(binari):
    """Retalla la tinta i la redimensiona a 28x28 (quadrat + padding)."""
    contorns, _ = cv2.findContours(binari, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contorns_valids = [c for c in contorns if cv2.contourArea(c) > 5]
    if not contorns_valids:
        return np.zeros((28, 28), dtype=np.uint8)

    caixes = [cv2.boundingRect(c) for c in contorns_valids]
    x = min(cx for cx, cy, cw, ch in caixes)
    y = min(cy for cx, cy, cw, ch in caixes)
    x_max = max(cx + cw for cx, cy, cw, ch in caixes)
    y_max = max(cy + ch for cx, cy, cw, ch in caixes)
    w, h = x_max - x, y_max - y

    retall = binari[y:y + h, x:x + w]
    mida_max = max(w, h)
    pad_y = (mida_max - h) // 2 + 4
    pad_x = (mida_max - w) // 2 + 4
    quadrat = cv2.copyMakeBorder(retall, pad_y, pad_y, pad_x, pad_x,
                                 cv2.BORDER_CONSTANT, value=0)
    return cv2.resize(quadrat, (28, 28))


def preprocessar_caracter(img):
    """Pipeline complet per UNA imatge d'un sol caracter. Retorna 28x28 uint8."""
    return retallar_a_28x28(binaritzar(img))

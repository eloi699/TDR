"""
entrenament_final.py (v6)
=========================
Afegeix EMNIST carregat manualment (evita el bug de tensorflow_datasets).
"""
import glob
import os
import random

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import (Conv2D, Dense, Dropout, Flatten,
                                     MaxPooling2D)
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from preprocessar import preprocessar_caracter
from carregar_emnist import carregar_emnist_digits

random.seed(42)
np.random.seed(42)
tf.random.set_seed(42)

CLASSES = ['0','1','2','3','4','5','6','7','8','9','+','-','x',':','=']
NUM_CLASSES = len(CLASSES)

N_MNIST_PER_CLASSE  = 500
N_EMNIST_PER_CLASSE = 500

FONTS = [
    {
        'path': os.path.expanduser('~/Desktop/python 3/dades_eloi'),
        'mapping': {
            '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9',
            '+':'+','-':'-','x':'x','=':'=',
        },
        'repetir_max': 20,
    },
    {
        'path': os.path.expanduser('~/Desktop/TDR-github/dades_hasy'),
        'mapping': {
            '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9',
            '+':'+','-':'-','x':'x',
            'div':':',
        },
        'repetir_max': 1,
    },
    {
        'path': os.path.expanduser('~/Desktop/TDR-github/dades_sintetiques'),
        'mapping': {'=':'=', 'div':':'},
        'repetir_max': 1,
    },
]

print("Carregant les meves imatges...")
X, y = [], []
for font in FONTS:
    base = font['path']
    if not os.path.isdir(base):
        continue
    for carpeta, classe in font['mapping'].items():
        ruta = os.path.join(base, carpeta)
        if not os.path.isdir(ruta):
            continue
        idx = CLASSES.index(classe)
        fitxers = sorted(glob.glob(os.path.join(ruta, '*')))
        fitxers = [f for f in fitxers if f.lower().endswith(('.png','.jpg','.jpeg'))]
        imgs = []
        for f in fitxers:
            img = cv2.imread(f)
            if img is None:
                continue
            imgs.append(preprocessar_caracter(img))
        n = len(imgs)
        if n == 0:
            continue
        reps = min(font.get('repetir_max', 1), max(1, 100 // n)) if n < 100 else 1
        for img in imgs:
            for _ in range(reps):
                X.append(img)
                y.append(idx)
        print(f"  {os.path.basename(base)}/{carpeta}: {n} x{reps}")

# ============================================================
# MNIST
# ============================================================
print("\nCarregant MNIST...")
(x_mnist, y_mnist), _ = tf.keras.datasets.mnist.load_data()
x_mnist = x_mnist.astype('float32') / 255.0

for digit in range(10):
    ids = np.where(y_mnist == digit)[0]
    np.random.shuffle(ids)
    triats = ids[:N_MNIST_PER_CLASSE]
    for i in triats:
        X.append((x_mnist[i] * 255).astype(np.uint8))
        y.append(digit)
print(f"  MNIST: {N_MNIST_PER_CLASSE} per digit x 10 = {N_MNIST_PER_CLASSE*10}")

# ============================================================
# EMNIST (carregat manualment)
# ============================================================
print("\nCarregant EMNIST (manual)...")
try:
    x_emnist, y_emnist = carregar_emnist_digits('gzip')
    print(f"  EMNIST carregat: {len(x_emnist)} imatges")
    for digit in range(10):
        ids = np.where(y_emnist == digit)[0]
        np.random.shuffle(ids)
        triats = ids[:N_EMNIST_PER_CLASSE]
        for i in triats:
            X.append(x_emnist[i])
            y.append(digit)
    print(f"  EMNIST: {N_EMNIST_PER_CLASSE} per digit x 10 = {N_EMNIST_PER_CLASSE*10}")
except Exception as e:
    print(f"  AVIS EMNIST: {e}")

X = np.array(X, dtype=np.float32) / 255.0
y = np.array(y, dtype=np.int64)
X = X.reshape(-1, 28, 28, 1)

print(f"\nTotal mostres: {len(X)}")
for i, c in enumerate(CLASSES):
    print(f"  {c!r:4}: {int((y==i).sum())}")

idx_train, idx_val = [], []
for i in range(NUM_CLASSES):
    ids = np.where(y == i)[0]
    np.random.shuffle(ids)
    tall = int(0.85 * len(ids))
    idx_train.extend(ids[:tall])
    idx_val.extend(ids[tall:])

X_train, y_train = X[idx_train], y[idx_train]
X_val, y_val = X[idx_val], y[idx_val]

counts = np.bincount(y_train, minlength=NUM_CLASSES).astype(np.float64)
counts = np.maximum(counts, 1)
total = counts.sum()
class_weights = {i: total / (NUM_CLASSES * counts[i]) for i in range(NUM_CLASSES)}
print("\nPesos:", {CLASSES[i]: round(w, 2) for i, w in class_weights.items()})

datagen = ImageDataGenerator(
    rotation_range=12,
    zoom_range=0.15,
    width_shift_range=0.12,
    height_shift_range=0.12,
    shear_range=0.1,
    fill_mode='constant', cval=0,
)

model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(NUM_CLASSES, activation='softmax'),
])
model.compile(
    optimizer=tf.keras.optimizers.Adam(0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy'],
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=6,
                                     restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                         patience=3, min_lr=1e-5),
]

print("\nEntrenant...")
model.fit(
    datagen.flow(X_train, y_train, batch_size=128),
    validation_data=(X_val, y_val),
    epochs=40,
    class_weight=class_weights,
    callbacks=callbacks,
)

model.save('model_matematic.keras')
print("\nModel guardat!")

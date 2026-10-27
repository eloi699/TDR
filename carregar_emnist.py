"""
carregar_emnist.py
Carrega EMNIST digits directament dels fitxers IDX (sense tensorflow_datasets).
"""
import gzip
import os

import numpy as np


def _llegir_idx_imatges(path):
    with gzip.open(path, 'rb') as f:
        magic = int.from_bytes(f.read(4), 'big')
        n = int.from_bytes(f.read(4), 'big')
        files = int.from_bytes(f.read(4), 'big')
        cols = int.from_bytes(f.read(4), 'big')
        assert magic == 2051, f"Magic incorrecte: {magic}"
        buf = f.read(n * files * cols)
        data = np.frombuffer(buf, dtype=np.uint8).reshape(n, files, cols)
        # EMNIST ve transposat: files i columnes estan al revés
        data = np.transpose(data, (0, 2, 1))
        return data


def _llegir_idx_labels(path):
    with gzip.open(path, 'rb') as f:
        magic = int.from_bytes(f.read(4), 'big')
        n = int.from_bytes(f.read(4), 'big')
        assert magic == 2049, f"Magic incorrecte: {magic}"
        buf = f.read(n)
        return np.frombuffer(buf, dtype=np.uint8)


def carregar_emnist_digits(base_dir='gzip'):
    """Retorna (x_train, y_train) d'EMNIST digits."""
    x_path = os.path.join(base_dir, 'emnist-digits-train-images-idx3-ubyte.gz')
    y_path = os.path.join(base_dir, 'emnist-digits-train-labels-idx1-ubyte.gz')
    print(f"  Llegint {os.path.basename(x_path)}...")
    x = _llegir_idx_imatges(x_path)
    y = _llegir_idx_labels(y_path)
    # Assegurem fons negre i tinta blanca (coherent amb preprocessar.py)
    # EMNIST ve amb fons negre i tinta blanca, igual que MNIST. OK.
    return x, y

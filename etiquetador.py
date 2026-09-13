"""
etiquetador.py
Mini-app Streamlit per classificar fotos rapidament.
Executa amb:  streamlit run etiquetador.py
"""
import os
import time

import streamlit as st
from PIL import Image, ImageOps

DESTI = os.path.expanduser('~/Desktop/TDR-github/dades_noves')
CLASSES = ['0','1','2','3','4','5','6','7','8','9','+','-','x','div','=']

st.set_page_config(page_title="Etiquetador", layout="centered")
st.title("Etiquetador rapid")
st.write("Fes una foto (o puja-ne varies) i prem el boto del caracter correcte.")

for c in CLASSES:
    os.makedirs(os.path.join(DESTI, c), exist_ok=True)

if 'comptador' not in st.session_state:
    st.session_state.comptador = {c: 0 for c in CLASSES}

img = st.camera_input("Webcam", label_visibility="collapsed")
if img is None:
    img = st.file_uploader("O puja una imatge", type=['jpg','jpeg','png'])

if img is not None:
    pil = ImageOps.exif_transpose(Image.open(img)).convert('RGB')
    st.image(pil, use_container_width=True)

    st.write("**Quin caracter es?**")
    cols = st.columns(8)
    for i, c in enumerate(CLASSES):
        with cols[i % 8]:
            if st.button(c, key=f"btn_{c}"):
                nom = f"{c}_{int(time.time()*1000)}.jpg"
                pil.save(os.path.join(DESTI, c, nom))
                st.session_state.comptador[c] += 1
                st.success(f"Guardat com a {c!r}!")

st.divider()
st.write("**Fotos noves per classe:**")
for c, n in st.session_state.comptador.items():
    if n > 0:
        st.write(f"  {c}: {n}")

"""
app.py
======
Aplicació visual del Tutor Matemàtic amb IA.
Executa-la en local amb:   streamlit run app.py
"""

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from motor import carregar_model, analitzar_imatge

st.set_page_config(page_title="Tutor Matemàtic IA", page_icon="🧮", layout="centered")


@st.cache_resource
def obtenir_model():
    # @st.cache_resource fa que el model NOMÉS es carregui un cop,
    # encara que molta gent faci servir l'app alhora.
    return carregar_model()


st.title("🧮 Tutor Matemàtic amb IA")
st.write(
    "Escriu una operació a mà en un paper (suma **+**, resta **-**, "
    "multiplicació **x** o divisió **:**), fes-ne una foto i l'IA "
    "t'explicarà pas a pas com resoldre-la."
)

model = obtenir_model()

pestanya_foto, pestanya_pujar = st.tabs(["📷 Fer una foto", "📁 Pujar una imatge"])

imatge_pujada = None

with pestanya_foto:
    captura = st.camera_input("Fes la foto de l'operació")
    if captura is not None:
        imatge_pujada = captura

with pestanya_pujar:
    fitxer = st.file_uploader("Selecciona una imatge del teu dispositiu", type=["jpg", "jpeg", "png"])
    if fitxer is not None:
        imatge_pujada = fitxer

if imatge_pujada is not None:
    # Convertim la imatge (que ve com a bytes) al format que fa servir OpenCV (BGR)
    imatge_pil = Image.open(imatge_pujada).convert("RGB")
    imatge_np = np.array(imatge_pil)
    imatge_bgr = cv2.cvtColor(imatge_np, cv2.COLOR_RGB2BGR)

    with st.spinner("Analitzant la imatge..."):
        img_anotada, equacio, explicacio = analitzar_imatge(imatge_bgr, model)

    st.divider()
    st.subheader("Resultat")

    img_anotada_rgb = cv2.cvtColor(img_anotada, cv2.COLOR_BGR2RGB)
    st.image(img_anotada_rgb, caption=f"Operació detectada: {equacio or '(cap)'}",
             use_container_width=True)

    st.markdown(f"### {explicacio}".replace("\n", "  \n"))

else:
    st.info("Fes una foto o puja una imatge per començar.")

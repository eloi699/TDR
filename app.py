"""
app.py
======
Aplicació visual del Tutor Matemàtic amb IA.
Executa-la en local amb:   streamlit run app.py

L'estil visual (colors, tipografia, targetes arrodonides) està inspirat
en la referència "EduLens AI" que en Eloi va compartir.
"""

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from motor import carregar_model, analitzar_imatge

st.set_page_config(page_title="Tutor Matemàtic IA", page_icon="🧮", layout="centered")


# =========================================================
# ESTIL VISUAL (paleta i tipografia inspirades en EduLens AI)
# =========================================================
PRIMARY = "#2b8cee"
BACKGROUND = "#f6f7f8"
CARD = "#ffffff"
TEXT = "#101922"
TEXT_MUTED = "#5b6b7a"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Lexend', sans-serif;
    }}

    .stApp {{
        background-color: {BACKGROUND};
    }}

    /* Capçalera personalitzada, estil "Dashboard" de la referència */
    .capsalera-app {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 8px 0 20px 0;
    }}
    .capsalera-icona {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 56px;
        height: 56px;
        min-width: 56px;
        border-radius: 16px;
        background-color: rgba(43, 140, 238, 0.12);
        font-size: 28px;
    }}
    .capsalera-text h1 {{
        font-size: 22px;
        font-weight: 700;
        color: {TEXT};
        margin: 0;
        line-height: 1.2;
    }}
    .capsalera-text p {{
        font-size: 14px;
        color: {TEXT_MUTED};
        margin: 2px 0 0 0;
        font-weight: 500;
    }}

    /* Targetes arrodonides amb ombra suau */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {CARD};
        border-radius: 20px;
        border: 1px solid rgba(16, 25, 34, 0.06);
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08);
        padding: 4px;
    }}

    /* Pestanyes com a "pills" */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background-color: rgba(16, 25, 34, 0.04);
        padding: 4px;
        border-radius: 999px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 999px;
        padding: 8px 20px;
        font-weight: 600;
        color: {TEXT_MUTED};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {PRIMARY} !important;
        color: white !important;
    }}
    /* Amaga la ratlla d'indicador per defecte (xocava amb el nostre disseny de "pill") */
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* Reforç: assegura contrast de text encara que el navegador prefereixi mode fosc */
    .stApp, .stApp p, .stApp li, .stApp span {{
        color: {TEXT};
    }}

    /* Botons amb el blau principal */
    .stButton button, .stCameraInput button, .stFileUploader button {{
        border-radius: 999px !important;
        font-weight: 600 !important;
        border: none !important;
    }}
    .stButton button[kind="primary"] {{
        background-color: {PRIMARY} !important;
    }}

    /* Targeta del resultat */
    .targeta-resultat {{
        background-color: {CARD};
        border-radius: 20px;
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08);
        border: 1px solid rgba(16, 25, 34, 0.06);
        padding: 24px;
        margin-top: 12px;
    }}
    .targeta-resultat h3 {{
        color: {TEXT};
        font-weight: 700;
        margin-top: 0;
    }}
    .etiqueta-operacio {{
        display: inline-block;
        background-color: rgba(43, 140, 238, 0.12);
        color: {PRIMARY};
        font-weight: 700;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 14px;
        margin-bottom: 12px;
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def obtenir_model():
    # @st.cache_resource fa que el model NOMÉS es carregui un cop,
    # encara que molta gent faci servir l'app alhora.
    return carregar_model()


# ---------------------------------------------------------
# CAPÇALERA
# ---------------------------------------------------------
st.markdown("""
<div class="capsalera-app">
    <div class="capsalera-icona">🧮</div>
    <div class="capsalera-text">
        <h1>Tutor Matemàtic amb IA</h1>
        <p>Fes una foto d'una operació i te l'explico pas a pas</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.write(
    "Escriu una operació a mà en un paper (suma **+**, resta **-**, "
    "multiplicació **x** o divisió **:**), fes-ne una foto i l'IA "
    "t'explicarà pas a pas com resoldre-la."
)

model = obtenir_model()

mode_depuracio = st.checkbox(
    "🔍 Mode depuració (mostra la imatge en blanc i negre que fa servir l'IA)"
)

with st.container(border=True):
    pestanya_foto, pestanya_pujar = st.tabs(["📷  Fer una foto", "📁  Pujar una imatge"])

    imatge_pujada = None

    with pestanya_foto:
        captura = st.camera_input("Fes la foto de l'operació", label_visibility="collapsed")
        if captura is not None:
            imatge_pujada = captura

    with pestanya_pujar:
        fitxer = st.file_uploader("Selecciona una imatge del teu dispositiu", type=["jpg", "jpeg", "png"],
                                   label_visibility="collapsed")
        if fitxer is not None:
            imatge_pujada = fitxer

if imatge_pujada is not None:
    # Convertim la imatge (que ve com a bytes) al format que fa servir OpenCV (BGR)
    imatge_pil = Image.open(imatge_pujada).convert("RGB")
    imatge_np = np.array(imatge_pil)
    imatge_bgr = cv2.cvtColor(imatge_np, cv2.COLOR_RGB2BGR)

    with st.spinner("Analitzant la imatge..."):
        img_anotada, equacio, explicacio, binari = analitzar_imatge(imatge_bgr, model)

    img_anotada_rgb = cv2.cvtColor(img_anotada, cv2.COLOR_BGR2RGB)

    if mode_depuracio:
        st.markdown("**Imatge binaritzada (el que veu realment l'algorisme):**")
        st.image(binari, use_container_width=True)
        st.caption(
            "El blanc és tinta detectada, el negre és fons. Si els números "
            "estan tocant-se o hi ha taques blanques dins del fons, aquí ho veuràs."
        )

    st.markdown('<div class="targeta-resultat">', unsafe_allow_html=True)
    st.markdown(f'<span class="etiqueta-operacio">Operació detectada: {equacio or "(cap)"}</span>',
                unsafe_allow_html=True)
    st.image(img_anotada_rgb, use_container_width=True)
    st.markdown(f"### {explicacio}".replace("\n", "  \n"))
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Fes una foto o puja una imatge per començar.")

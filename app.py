"""
app.py
======
Aplicacio visual del Tutor Matematic amb IA + Horari d'examens compartit.
Executa-la en local amb:   streamlit run app.py

L'estil visual (colors, tipografia, targetes arrodonides) esta inspirat
en la referencia "EduLens AI" que en Eloi va compartir.
"""

import json
import os
import uuid
from datetime import date, datetime

import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageOps

from motor import carregar_model, analitzar_imatge

st.set_page_config(page_title="Tutor Matematic IA", layout="centered")


PRIMARY = "#2b8cee"
BACKGROUND = "#101922"
CARD = "#1c2630"
TEXT = "#ffffff"
TEXT_MUTED = "#94a3b8"

EXAMENS_PATH = "dades/examens.json"

DIES_CA = ["dilluns", "dimarts", "dimecres", "dijous", "divendres", "dissabte", "diumenge"]
MESOS_CA = ["gener", "febrer", "marc", "abril", "maig", "juny",
            "juliol", "agost", "setembre", "octubre", "novembre", "desembre"]


def formatar_data_ca(d: date) -> str:
    return f"{DIES_CA[d.weekday()].capitalize()}, {d.day} {MESOS_CA[d.month - 1]} {d.year}"


def carregar_examens():
    if not os.path.exists(EXAMENS_PATH):
        return []
    try:
        with open(EXAMENS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def desar_examens(examens):
    os.makedirs(os.path.dirname(EXAMENS_PATH), exist_ok=True)
    with open(EXAMENS_PATH, "w", encoding="utf-8") as f:
        json.dump(examens, f, ensure_ascii=False, indent=2)


def eliminar_examen(id_examen):
    examens = carregar_examens()
    examens = [e for e in examens if e["id"] != id_examen]
    desar_examens(examens)


def afegir_examen(assignatura, data_examen, hora, descripcio):
    examens = carregar_examens()
    examens.append({
        "id": uuid.uuid4().hex,
        "assignatura": assignatura.strip(),
        "data": data_examen.isoformat(),
        "hora": hora.strip(),
        "descripcio": descripcio.strip(),
        "creat": datetime.now().isoformat(),
    })
    desar_examens(examens)


st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Lexend', sans-serif;
    }}

    .material-symbols-outlined {{
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        line-height: 1;
        vertical-align: middle;
    }}

    .stApp {{
        background-color: {BACKGROUND};
    }}

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
    .capsalera-icona .material-symbols-outlined {{
        font-size: 30px;
        color: {PRIMARY};
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

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {CARD};
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.4);
        padding: 4px;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background-color: rgba(255, 255, 255, 0.06);
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
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}
    .stApp, .stApp p, .stApp li, .stApp span {{
        color: {TEXT};
    }}

    .stButton button, .stCameraInput button, .stFileUploader button {{
        border-radius: 999px !important;
        font-weight: 600 !important;
        border: none !important;
    }}
    .stButton button[kind="primary"] {{
        background-color: {PRIMARY} !important;
        box-shadow: 0 10px 20px -6px rgba(43, 140, 238, 0.4) !important;
    }}

    .targeta-resultat {{
        background-color: {CARD};
        border-radius: 24px;
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
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

    .targeta-examen {{
        display: flex;
        gap: 16px;
        align-items: flex-start;
        background-color: {CARD};
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 16px 18px;
        margin-bottom: 12px;
    }}
    .targeta-examen-data {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: rgba(43, 140, 238, 0.14);
        color: {PRIMARY};
        border-radius: 14px;
        min-width: 56px;
        padding: 8px 6px;
        font-weight: 700;
        line-height: 1.1;
    }}
    .targeta-examen-data .dia {{
        font-size: 20px;
    }}
    .targeta-examen-data .mes {{
        font-size: 11px;
        text-transform: uppercase;
    }}
    .targeta-examen-cos h4 {{
        margin: 0 0 2px 0;
        color: {TEXT};
        font-size: 16px;
        font-weight: 700;
    }}
    .targeta-examen-cos p {{
        margin: 0;
        color: {TEXT_MUTED};
        font-size: 13px;
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def obtenir_model():
    return carregar_model()


tab_tutor, tab_horari = st.tabs(["🧮  Tutor Matematic", "📅  Horari d'examens"])


# ------------------------------------------------------------------
# SECCIO: TUTOR MATEMATIC
# ------------------------------------------------------------------
with tab_tutor:
    st.markdown("""
    <div class="capsalera-app">
        <div class="capsalera-icona"><span class="material-symbols-outlined">calculate</span></div>
        <div class="capsalera-text">
            <h1>Tutor Matematic amb IA</h1>
            <p>Fes una foto d'una operacio i te l'explico pas a pas</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write(
        "Escriu una operacio a ma en un paper (suma **+**, resta **-**, "
        "multiplicacio **x** o divisio **:**), fes-ne una foto i l'IA "
        "t'explicara pas a pas com resoldre-la."
    )

    model = obtenir_model()

    mode_depuracio = st.checkbox(
        "🔍 Mode depuracio (mostra la imatge en blanc i negre que fa servir l'IA)"
    )

    with st.container(border=True):
        pestanya_foto, pestanya_pujar = st.tabs(["📷  Fer una foto", "📁  Pujar una imatge"])

        imatge_pujada = None

        with pestanya_foto:
            captura = st.camera_input("Fes la foto de l'operacio", label_visibility="collapsed")
            if captura is not None:
                imatge_pujada = captura

        with pestanya_pujar:
            fitxer = st.file_uploader("Selecciona una imatge del teu dispositiu", type=["jpg", "jpeg", "png"],
                                       label_visibility="collapsed")
            if fitxer is not None:
                imatge_pujada = fitxer

    if imatge_pujada is not None:
        imatge_pil = ImageOps.exif_transpose(Image.open(imatge_pujada)).convert("RGB")
        imatge_np = np.array(imatge_pil)
        imatge_bgr = cv2.cvtColor(imatge_np, cv2.COLOR_RGB2BGR)

        with st.spinner("Analitzant la imatge..."):
            img_anotada, equacio, explicacio, binari = analitzar_imatge(imatge_bgr, model)

        img_anotada_rgb = cv2.cvtColor(img_anotada, cv2.COLOR_BGR2RGB)

        if mode_depuracio:
            st.markdown("**Imatge binaritzada (el que veu realment l'algorisme):**")
            st.image(binari, use_container_width=True)
            st.caption(
                "El blanc es tinta detectada, el negre es fons. Si els numeros "
                "estan tocant-se o hi ha taques blanques dins del fons, aqui ho veuras."
            )

        st.markdown('<div class="targeta-resultat">', unsafe_allow_html=True)
        st.markdown(f'<span class="etiqueta-operacio">Operacio detectada: {equacio or "(cap)"}</span>',
                    unsafe_allow_html=True)
        st.image(img_anotada_rgb, use_container_width=True)
        st.markdown(f"### {explicacio}".replace("\n", "  \n"))
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Fes una foto o puja una imatge per comencar.")


# ------------------------------------------------------------------
# SECCIO: HORARI D'EXAMENS COMPARTIT
# ------------------------------------------------------------------
with tab_horari:
    st.markdown("""
    <div class="capsalera-app">
        <div class="capsalera-icona"><span class="material-symbols-outlined">calendar_month</span></div>
        <div class="capsalera-text">
            <h1>Horari d'examens</h1>
            <p>Tota la classe pot afegir i veure les properes proves</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### Afegeix un examen")
        with st.form("nou_examen", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                assignatura = st.text_input("Assignatura *", placeholder="Matematiques")
            with col2:
                data_examen = st.date_input("Data *", value=date.today(), format="DD/MM/YYYY")

            hora = st.text_input("Hora (opcional)", placeholder="10:00")
            descripcio = st.text_input("Detalls (opcional)", placeholder="Temes 3 i 4, portar calculadora")

            enviat = st.form_submit_button("Afegeix a l'horari", type="primary", use_container_width=True)

            if enviat:
                if not assignatura.strip():
                    st.error("Cal omplir com a minim l'assignatura.")
                else:
                    afegir_examen(assignatura, data_examen, hora, descripcio)
                    st.success("Examen afegit! Ja el veu tota la classe.")
                    st.rerun()

    examens = carregar_examens()
    for e in examens:
        e["_data_obj"] = date.fromisoformat(e["data"])
    examens.sort(key=lambda e: e["_data_obj"])

    avui = date.today()
    propers = [e for e in examens if e["_data_obj"] >= avui]
    passats = [e for e in examens if e["_data_obj"] < avui]

    st.markdown("#### Propers examens")
    if not propers:
        st.info("Encara no hi ha cap examen apuntat. Sigues el primer a afegir-ne un!")
    else:
        for e in propers:
            d = e["_data_obj"]
            hora_txt = f" · {e['hora']}" if e.get("hora") else ""
            descripcio_txt = f"<p>{e['descripcio']}</p>" if e.get("descripcio") else ""
            html_targeta = (
                '<div class="targeta-examen">'
                '<div class="targeta-examen-data">'
                f'<span class="dia">{d.day}</span>'
                f'<span class="mes">{MESOS_CA[d.month - 1][:3]}</span>'
                '</div>'
                '<div class="targeta-examen-cos">'
                f'<h4>{e["assignatura"]}{hora_txt}</h4>'
                f'<p>{formatar_data_ca(d)}</p>'
                f'{descripcio_txt}'
                '</div>'
                '</div>'
            )
            confirmar_key = f"confirmar_esborrar_{e['id']}"

            col_targeta, col_accio = st.columns([6, 1])
            with col_targeta:
                st.markdown(html_targeta, unsafe_allow_html=True)
            with col_accio:
                if st.session_state.get(confirmar_key):
                    if st.button("Si", key=f"si_{e['id']}", help="Confirma l'esborrat", use_container_width=True):
                        eliminar_examen(e["id"])
                        st.session_state.pop(confirmar_key, None)
                        st.rerun()
                    if st.button("No", key=f"no_{e['id']}", help="Cancel·la", use_container_width=True):
                        st.session_state.pop(confirmar_key, None)
                        st.rerun()
                else:
                    if st.button("🗑️", key=f"del_{e['id']}", help="Esborra aquest examen", use_container_width=True):
                        st.session_state[confirmar_key] = True
                        st.rerun()

    if passats:
        with st.expander(f"Examens passats ({len(passats)})"):
            for e in reversed(passats):
                d = e["_data_obj"]
                col_text, col_del = st.columns([6, 1])
                with col_text:
                    st.markdown(f"**{e['assignatura']}** — {formatar_data_ca(d)}")
                with col_del:
                    if st.button("🗑️", key=f"del_passat_{e['id']}", help="Esborra aquest examen",
                                 use_container_width=True):
                        eliminar_examen(e["id"])
                        st.rerun()

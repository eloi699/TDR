"""
app.py
======
Aplicacio visual del Tutor Matematic amb IA + Horari d'examens compartit.
Executa-la en local amb:   streamlit run app.py
"""

import json
import os
import uuid
from datetime import date, datetime

import cv2
import numpy as np
import streamlit as st
import auth
from PIL import Image, ImageOps
from streamlit_cropper import st_cropper

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


def afegir_examen(assignatura, data_examen, hora, descripcio, classe):
    examens = carregar_examens()
    examens.append({
        "id": uuid.uuid4().hex,
        "assignatura": assignatura.strip(),
        "data": data_examen.isoformat(),
        "hora": hora.strip(),
        "descripcio": descripcio.strip(),
        "classe": classe,
        "creat": datetime.now().isoformat(),
    })
    desar_examens(examens)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    * { box-sizing: border-box; }

    html, body, [class*="css"] {
        font-family: 'Lexend', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        line-height: 1;
        vertical-align: middle;
    }

    /* Fons amb gradient radial subtil */
    .stApp {
        background: radial-gradient(ellipse at top, #18222d 0%, #101922 50%, #0c141b 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* Capcalera */
    .capsalera-app {
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 12px 0 28px 0;
    }
    .capsalera-icona {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        min-width: 60px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(43, 140, 238, 0.18) 0%, rgba(43, 140, 238, 0.06) 100%);
        border: 1px solid rgba(43, 140, 238, 0.25);
        box-shadow: 0 8px 24px -8px rgba(43, 140, 238, 0.4);
    }
    .capsalera-icona .material-symbols-outlined {
        font-size: 30px;
        color: #2b8cee;
    }
    .capsalera-text h1 {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    .capsalera-text p {
        font-size: 14px;
        color: #94a3b8;
        margin: 4px 0 0 0;
        font-weight: 400;
    }

    /* Targetes amb estil glass */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(135deg, rgba(28, 38, 48, 0.9) 0%, rgba(22, 30, 40, 0.9) 100%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 12px 32px -12px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        padding: 6px;
    }

    /* Pestanyes - estil pill */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255, 255, 255, 0.04);
        padding: 6px;
        border-radius: 999px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 10px 22px;
        font-weight: 600;
        font-size: 14px;
        color: #94a3b8;
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background: rgba(255, 255, 255, 0.04);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2b8cee 0%, #1e6fbf 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px -2px rgba(43, 140, 238, 0.5);
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    /* Text */
    .stApp, .stApp p, .stApp li, .stApp span, .stApp label {
        color: #e2e8f0;
    }

    /* Botons moderns */
    .stButton button,
    .stCameraInput button,
    .stFileUploader button,
    .stFormSubmitButton button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background: rgba(255, 255, 255, 0.03) !important;
        color: #ffffff !important;
        transition: all 0.25s ease !important;
        padding: 10px 20px !important;
    }
    .stButton button:hover,
    .stCameraInput button:hover,
    .stFileUploader button:hover,
    .stFormSubmitButton button:hover {
        transform: translateY(-2px);
        border-color: rgba(43, 140, 238, 0.5) !important;
        background: rgba(43, 140, 238, 0.1) !important;
        box-shadow: 0 8px 20px -8px rgba(43, 140, 238, 0.4);
    }
    .stButton button[kind="primary"],
    .stFormSubmitButton button[kind="primary"] {
        background: linear-gradient(135deg, #2b8cee 0%, #1e6fbf 100%) !important;
        border: none !important;
        box-shadow: 0 8px 20px -6px rgba(43, 140, 238, 0.5) !important;
    }
    .stButton button[kind="primary"]:hover,
    .stFormSubmitButton button[kind="primary"]:hover {
        box-shadow: 0 12px 28px -6px rgba(43, 140, 238, 0.7) !important;
    }

    /* Inputs */
    .stTextInput input,
    .stDateInput input,
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease;
    }
    .stTextInput input:focus,
    .stDateInput input:focus {
        border-color: #2b8cee !important;
        box-shadow: 0 0 0 3px rgba(43, 140, 238, 0.15) !important;
    }
    .stTextInput label, .stDateInput label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }

    /* Targeta de resultat */
    .targeta-resultat {
        background: linear-gradient(135deg, #1c2630 0%, #16202b 100%);
        border-radius: 20px;
        border: 1px solid rgba(43, 140, 238, 0.15);
        box-shadow: 0 12px 40px -12px rgba(43, 140, 238, 0.2), 0 4px 12px rgba(0, 0, 0, 0.3);
        padding: 28px;
        margin-top: 16px;
        animation: fadeInUp 0.5s ease-out;
    }
    .targeta-resultat h3 {
        color: #ffffff;
        font-weight: 700;
        margin-top: 0;
        font-size: 20px;
        letter-spacing: -0.01em;
    }
    .etiqueta-operacio {
        display: inline-block;
        background: linear-gradient(135deg, rgba(43, 140, 238, 0.2) 0%, rgba(43, 140, 238, 0.1) 100%);
        color: #58a9f5;
        font-weight: 600;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 13px;
        margin-bottom: 16px;
        border: 1px solid rgba(43, 140, 238, 0.25);
    }

    /* Targetes d'examens */
    .targeta-examen {
        display: flex;
        gap: 16px;
        align-items: flex-start;
        background: linear-gradient(135deg, #1c2630 0%, #16202b 100%);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: all 0.25s ease;
    }
    .targeta-examen:hover {
        border-color: rgba(43, 140, 238, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.4);
    }
    .targeta-examen-data {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(43, 140, 238, 0.2) 0%, rgba(43, 140, 238, 0.08) 100%);
        color: #58a9f5;
        border-radius: 14px;
        min-width: 58px;
        padding: 10px 8px;
        font-weight: 700;
        line-height: 1.1;
        border: 1px solid rgba(43, 140, 238, 0.2);
    }
    .targeta-examen-data .dia { font-size: 22px; letter-spacing: -0.02em; }
    .targeta-examen-data .mes { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }
    .targeta-examen-cos h4 {
        margin: 0 0 4px 0;
        color: #ffffff;
        font-size: 16px;
        font-weight: 600;
    }
    .targeta-examen-cos p {
        margin: 0;
        color: #94a3b8;
        font-size: 13px;
        line-height: 1.5;
    }

    /* Animacions */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Alertes */
    .stAlert {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Imatges */
    .stImage img {
        border-radius: 12px;
    }

    /* Separador */
    hr {
        border-color: rgba(255, 255, 255, 0.08);
        margin: 24px 0;
    }

    /* Checkbox */
    .stCheckbox label { color: #e2e8f0 !important; font-weight: 500 !important; }

    /* Amagar menu i footer per netedat */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def obtenir_model():
    return carregar_model()


# ------------------------------------------------------------------
# PORTADA D'ENTRADA
# ------------------------------------------------------------------
auth.requerir_login()



tab_tutor, tab_horari, tab_perfil = st.tabs(["🧮  Tutor Matematic", "📅  Horari d'examens", "👤  Perfil"])


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
        "Veure el que veu la IA"
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
        if "girar_180" not in st.session_state:
            st.session_state.girar_180 = False

        imatge_pil = ImageOps.exif_transpose(Image.open(imatge_pujada)).convert("RGB")

        # --- RETALLADOR: l'usuari pot ajustar la zona abans d'analitzar ---
        st.write("**Ajusta el requadre** perque nomes quedi l'operacio.")
        imatge_pil = st_cropper(
            imatge_pil,
            realtime_update=True,
            box_color="#2b8cee",
            aspect_ratio=None,
            return_type="image",
        )

        # --- NORMALITZAR LA MIDA DE LA IMATGE ---
        # La càmera del mòbil pot donar imatges molt grans (3000+ px) o molt
        # petites, i els filtres del motor.py estan calibrats per a una mida
        # concreta. Redimensionem a una amplada fixa perquè tot funcioni igual.
        AMPLADA_OBJECTIU = 900
        if imatge_pil.width > AMPLADA_OBJECTIU:
            ratio = AMPLADA_OBJECTIU / imatge_pil.width
            nova_alcada = int(imatge_pil.height * ratio)
            imatge_pil = imatge_pil.resize((AMPLADA_OBJECTIU, nova_alcada), Image.LANCZOS)
        elif imatge_pil.width < 500:
            ratio = 700 / imatge_pil.width
            nova_alcada = int(imatge_pil.height * ratio)
            imatge_pil = imatge_pil.resize((700, nova_alcada), Image.LANCZOS)

        imatge_np = np.array(imatge_pil)
        imatge_bgr = cv2.cvtColor(imatge_np, cv2.COLOR_RGB2BGR)

        if st.session_state.girar_180:
            imatge_bgr = cv2.rotate(imatge_bgr, cv2.ROTATE_180)

        with st.spinner("Analitzant la imatge..."):
            img_anotada, equacio, explicacio, binari, info_depuracio = analitzar_imatge(imatge_bgr, model)

        img_anotada_rgb = cv2.cvtColor(img_anotada, cv2.COLOR_BGR2RGB)

        st.write(
            "El resultat surt de cap per avall o al reves? "
            "L'aplicacio pot girar automaticament una foto de costat, "
            "pero no sempre sap distingir 'de cap per avall' de 'be'."
        )
        if st.button("🔄 Gira la imatge 180° i torna-ho a provar"):
            st.session_state.girar_180 = not st.session_state.girar_180
            st.rerun()

        if mode_depuracio:
            st.markdown("**Comparativa de les 3 orientacions provades:**")
            st.caption(
                "El blanc es tinta detectada, el negre es fons. L'orientacio "
                "marcada amb ✅ es la que s'ha fet servir per donar la resposta."
            )
            cols = st.columns(3)
            noms_angle = {0: "Normal (0°)", 90: "Girada dreta (90°)", -90: "Girada esquerra (-90°)"}
            for col, info in zip(cols, info_depuracio):
                with col:
                    marca = "✅ " if info["triada"] else ""
                    st.markdown(f"**{marca}{noms_angle[info['angle']]}**")
                    st.image(info["binari"], use_container_width=True)
                    alineat_txt = "↔️ horitzontal" if info["ben_alineat"] else "↕️ vertical"
                    st.caption(
                        f"Llegit: `{info['equacio_llegida'] or '(res)'}`  \n"
                        f"Puntuacio: {info['puntuacio']}  \n"
                        f"Alineacio: {alineat_txt}"
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
        st.caption(f"Aquest examen s'afegirà a la classe: **{st.session_state.usuari['classe']}**")
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
                    afegir_examen(assignatura, data_examen, hora, descripcio, st.session_state.usuari['classe'])
                    st.success("Examen afegit! Ja el veu tota la classe.")
                    st.rerun()

    tots_examens = carregar_examens()
    classe_usuari = st.session_state.usuari["classe"]
    examens = [e for e in tots_examens if e.get("classe") == classe_usuari]
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


with tab_perfil:
    auth.mostrar_perfil()

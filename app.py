"""
app.py
======
Aquesta és l'aplicació principal del Tutor Matemàtic.

Estructura:
    1. Imports i configuració inicial
    2. Funcions auxiliars (formatar dates)
    3. Aplicar estils CSS (des de estils.py)
    4. Comprovar login
    5. Crear les pestanyes
    6. Contingut de cada pestanya

Per executar-ho: streamlit run app.py
"""

# --- Imports estàndard de Python ---
import json
import os
import uuid
from datetime import date, datetime

# --- Llibreries externes ---
import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from streamlit_cropper import st_cropper

# --- Mòduls propis del projecte ---
import auth     # Gestiona usuaris, login i exàmens
import estils   # Conté tot el CSS personalitzat
from motor import carregar_model, analitzar_imatge  # IA: llegir operacions


# ==============================================================
# CONFIGURACIÓ INICIAL
# ==============================================================
st.set_page_config(page_title="Tutor Matematic IA", layout="centered")

# Noms dels dies i mesos en català (per formatar dates)
DIES_CA = ["dilluns", "dimarts", "dimecres", "dijous", "divendres", "dissabte", "diumenge"]
MESOS_CA = ["gener", "febrer", "marc", "abril", "maig", "juny",
            "juliol", "agost", "setembre", "octubre", "novembre", "desembre"]


# ==============================================================
# FUNCIONS AUXILIARS
# ==============================================================
def formatar_data_ca(d: date) -> str:
    """Converteix una data (2026-09-28) a text català (Dilluns, 28 setembre 2026)."""
    return f"{DIES_CA[d.weekday()].capitalize()}, {d.day} {MESOS_CA[d.month - 1]} {d.year}"


# ==============================================================
# APLICAR ESTILS I COMPROVAR LOGIN
# ==============================================================
# 1. Carregar els estils CSS personalitzats (definits a estils.py)
estils.aplicar()

# 2. Comprovar si l'usuari ha iniciat sessió. Si no, atura l'app
#    i mostra la pantalla de login. (definit a auth.py)
auth.requerir_login()


@st.cache_resource
def obtenir_model():
    return carregar_model()






# Determinar si l'usuari es admin
ADMINS = ["eloi"]
es_admin = st.session_state.usuari.get("username") in ADMINS

if es_admin:
    tab_tutor, tab_horari, tab_perfil, tab_admin = st.tabs([
        "🧮  Tutor Matematic",
        "📅  Horari d'examens",
        "👤  Perfil",
        "⚙️  Admin",
    ])
else:
    tab_tutor, tab_horari, tab_perfil = st.tabs([
        "🧮  Tutor Matematic",
        "📅  Horari d'examens",
        "👤  Perfil",
    ])
    tab_admin = None


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

        # --- PRESERVAR LA QUALITAT ORIGINAL ---
        # La camera del mobil pot donar imatges de 3000-4000 px d'amplada.
        # Si les reduim massa, perdem detall i la imatge mostrada queda
        # borrosa. Ara mantenim una amplada alta (2400 px) i apliquem
        # nomes una millora MOLT lleugera (nomes per ajudar al motor,
        # no per canviar l'aspecte visual).

        # Millora lleugera
        imatge_pil = imatge_pil.filter(
            ImageFilter.UnsharpMask(radius=1, percent=50, threshold=3)
        )
        imatge_pil = ImageEnhance.Contrast(imatge_pil).enhance(1.03)

        # Redimensionat menys agressiu per preservar el detall
        AMPLADA_OBJECTIU = 2400
        if imatge_pil.width > AMPLADA_OBJECTIU:
            ratio = AMPLADA_OBJECTIU / imatge_pil.width
            nova_alcada = int(imatge_pil.height * ratio)
            imatge_pil = imatge_pil.resize((AMPLADA_OBJECTIU, nova_alcada), Image.LANCZOS)
        elif imatge_pil.width < 800:
            ratio = 1200 / imatge_pil.width
            nova_alcada = int(imatge_pil.height * ratio)
            imatge_pil = imatge_pil.resize((1200, nova_alcada), Image.LANCZOS)

        # DEBUG TEMPORAL: mostrar la imatge que rep el motor
        st.markdown("##### 🔍 DEBUG: imatge que rep el motor")
        st.caption(f"Mida: {imatge_pil.size[0]} x {imatge_pil.size[1]} px · Mode: {imatge_pil.mode}")
        st.image(imatge_pil, caption="Aquesta es la imatge exacta que s'analitzara", use_container_width=True)

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
                    auth.afegir_examen(assignatura, data_examen, hora, descripcio, st.session_state.usuari['classe'])
                    st.success("Examen afegit! Ja el veu tota la classe.")
                    st.rerun()

    tots_examens = auth.carregar_examens()
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
                        auth.esborrar_examen(e["id"])
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
                        auth.esborrar_examen(e["id"])
                        st.rerun()


with tab_perfil:
    auth.mostrar_perfil()


if tab_admin is not None:
    with tab_admin:
        auth.mostrar_admin()

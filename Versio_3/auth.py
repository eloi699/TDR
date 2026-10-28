"""
auth.py
=======
Aquest fitxer gestiona TOT el que té a veure amb usuaris i dades.
"""

import base64
import glob
import hashlib
import json
import os
import uuid
from datetime import date, datetime

import streamlit as st

# CONSTANTS
RUTA_USUARIS = "dades/usuaris.json"
RUTA_EXAMENS = "dades/exàmens.json"

CLASSES = [
    "1r ESO", "2n ESO", "3r ESO", "4t ESO",
    "1r Batxillerat", "2n Batxillerat",
    "Altres",
]

ADMINS = ["eloi"]

def _llegir_json(ruta):
    es_usuaris = "usuaris" in ruta
    if not os.path.exists(ruta):
        return {} if es_usuaris else []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {} if es_usuaris else []

def _escriure_json(ruta, dades):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(dades, f, ensure_ascii=False, indent=2)

def _hash_contrasenya(usuari, contrasenya):
    text = f"tdr_tutor_matemàtic::{usuari.lower()}::{contrasenya}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def carregar_usuaris():
    return _llegir_json(RUTA_USUARIS)

def desar_usuaris(usuaris):
    _escriure_json(RUTA_USUARIS, usuaris)

def registrar_usuari(usuari, contrasenya, classe):
    usuari = usuari.strip().lower()
    if not usuari or not contrasenya or not classe:
        return False, "Cal omplir tots els camps."
    if len(usuari) < 3:
        return False, "El nom d'usuari ha de tenir almenys 3 caràcters."
    if len(contrasenya) < 4:
        return False, "La contrasenya ha de tenir almenys 4 caràcters."
    usuaris = carregar_usuaris()
    if usuari in usuaris:
        return False, "Aquest usuari ja existeix."
    usuaris[usuari] = {
        "password_hash": _hash_contrasenya(usuari, contrasenya),
        "classe": classe,
        "creat": datetime.now().isoformat(),
    }
    desar_usuaris(usuaris)
    return True, "Compte creat! Ara pots iniciar sessió."

def autenticar_usuari(usuari, contrasenya):
    usuari = usuari.strip().lower()
    usuaris = carregar_usuaris()
    if usuari not in usuaris:
        return False, "Usuari o contrasenya incorrectes."
    if usuaris[usuari]["password_hash"] != _hash_contrasenya(usuari, contrasenya):
        return False, "Usuari o contrasenya incorrectes."
    return True, ""

def canviar_contrasenya(usuari, contrasenya_vella, contrasenya_nova):
    ok, _ = autenticar_usuari(usuari, contrasenya_vella)
    if not ok:
        return False, "La contrasenya actual no és correcta."
    if len(contrasenya_nova) < 4:
        return False, "La nova contrasenya ha de tenir almenys 4 caràcters."
    usuaris = carregar_usuaris()
    usuaris[usuari]["password_hash"] = _hash_contrasenya(usuari, contrasenya_nova)
    desar_usuaris(usuaris)
    return True, "Contrasenya canviada correctament."

def canviar_classe(usuari, nova_classe):
    usuaris = carregar_usuaris()
    if usuari in usuaris:
        usuaris[usuari]["classe"] = nova_classe
        desar_usuaris(usuaris)
        st.session_state.usuari["classe"] = nova_classe

def es_admin(usuari):
    return usuari in ADMINS

def carregar_examens():
    return _llegir_json(RUTA_EXAMENS)

def desar_examens(examens):
    _escriure_json(RUTA_EXAMENS, examens)

def afegir_examen(assignatura, classe, data, hora, descripcio):
    examens = carregar_examens()
    examens.append({
        "id": uuid.uuid4().hex,
        "assignatura": assignatura.strip(),
        "classe": classe,
        "data": data.isoformat(),
        "hora": hora.strip(),
        "descripcio": descripcio.strip(),
        "creat": datetime.now().isoformat(),
    })
    desar_examens(examens)

def modificar_examen(id_examen, assignatura, classe, data, hora, descripcio):
    examens = carregar_examens()
    for e in examens:
        if e["id"] == id_examen:
            e["assignatura"] = assignatura.strip()
            e["classe"] = classe
            e["data"] = data.isoformat()
            e["hora"] = hora.strip()
            e["descripcio"] = descripcio.strip()
            break
    desar_examens(examens)

def esborrar_examen(id_examen):
    examens = carregar_examens()
    examens = [e for e in examens if e["id"] != id_examen]
    desar_examens(examens)

def examens_de_classe(classe):
    tots = carregar_examens()
    return [e for e in tots if e.get("classe") == classe]

def _generar_token(usuari):
    return hashlib.sha256(f"url_token::{usuari}".encode("utf-8")).hexdigest()[:16]

def guardar_sessio_url(usuari):
    st.query_params["u"] = usuari
    st.query_params["t"] = _generar_token(usuari)

def esborrar_sessio_url():
    try:
        del st.query_params["u"]
        del st.query_params["t"]
    except KeyError:
        pass

def restaurar_sessio_url():
    try:
        usuari = st.query_params.get("u")
        token = st.query_params.get("t")
    except Exception:
        return False
    if not usuari or not token:
        return False
    if token != _generar_token(usuari):
        return False
    usuaris = carregar_usuaris()
    if usuari in usuaris:
        st.session_state.usuari = {
            "username": usuari,
            "classe": usuaris[usuari]["classe"],
        }
        return True
    return False

def mostrar_login():
    fotos = []
    if os.path.isdir("assets"):
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            fotos.extend(sorted(glob.glob(os.path.join("assets", ext))))
    fotos = [f for f in fotos if not os.path.basename(f).startswith(".")]

    if fotos:
        fotos_dobles = fotos + fotos
        imgs_html = ""
        for f in fotos_dobles:
            try:
                with open(f, "rb") as img_file:
                    b64 = base64.b64encode(img_file.read()).decode()
                    ext = f.rsplit(".", 1)[-1].lower()
                    if ext == "jpg":
                        ext = "jpeg"
                    imgs_html += f'<img src="data:image/{ext};base64,{b64}" class="car-img">'
            except Exception:
                continue

    st.markdown("""
    <div style="text-align:center; padding:10px 20px 25px;">
        <h1 class="login-titol">Tutor <span>Matematic IA</span></h1>
    </div>
    """, unsafe_allow_html=True)

    col_esq, col_mig, col_dre = st.columns([1, 1.4, 1])
    with col_mig:
        tab_login, tab_registre = st.tabs(["Iniciar sessió", "Crear compte"])

        with tab_login:
            with st.form("form_login"):
                usuari_input = st.text_input("Nom d'usuari", placeholder="Escriu el teu nom d'usuari")
                pwd_input = st.text_input("Contrasenya", type="password", placeholder="Escriu la teva contrasenya")
                st.write("")
                enviat = st.form_submit_button("Entrar", type="primary", use_container_width=True)
                if enviat:
                    ok, err = autenticar_usuari(usuari_input, pwd_input)
                    if ok:
                        nom = usuari_input.strip().lower()
                        usuaris = carregar_usuaris()
                        st.session_state.usuari = {
                            "username": nom,
                            "classe": usuaris[nom]["classe"],
                        }
                        guardar_sessio_url(nom)
                        st.rerun()
                    else:
                        st.error(err)

        with tab_registre:
            with st.form("form_registre"):
                user2 = st.text_input("Nom d'usuari", placeholder="Tria un nom únic")
                pwd2 = st.text_input("Contrasenya", type="password", placeholder="Mínim 4 caràcters")
                classe = st.selectbox("Classe", CLASSES, index=None, placeholder="Selecciona la teva classe")
                st.write("")
                enviat2 = st.form_submit_button("Crear compte", type="primary", use_container_width=True)
                if enviat2:
                    ok, msg = registrar_usuari(user2, pwd2, classe or "")
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

def requerir_login():
    if st.session_state.get("usuari"):
        return
    if restaurar_sessio_url():
        return
    mostrar_login()
    st.stop()

def mostrar_perfil():
    usuari = st.session_state.usuari
    username = usuari["username"]
    classe = usuari["classe"]

    with st.container(border=True):
        st.markdown(f"### {username.capitalize()}")
        st.caption(f"Classe actual: **{classe}**")
        st.markdown("---")
        st.markdown("#### Canviar de classe")
        nova_classe = st.selectbox(
            "Nova classe", CLASSES,
            index=CLASSES.index(classe) if classe in CLASSES else 0,
            key="perfil_classe"
        )
        if st.button("Desar canvi de classe", use_container_width=True):
            canviar_classe(username, nova_classe)
            st.success(f"Classe actualitzada a {nova_classe}.")
            st.rerun()

        st.markdown("---")
        st.markdown("#### Canviar contrasenya")
        with st.form("form_canvi_pwd"):
            vella = st.text_input("Contrasenya actual", type="password")
            nova = st.text_input("Nova contrasenya", type="password")
            confirmar = st.text_input("Confirma la nova contrasenya", type="password")
            enviat = st.form_submit_button("Canviar contrasenya", type="primary", use_container_width=True)
            if enviat:
                if nova != confirmar:
                    st.error("Les contrasenyes noves no coincideixen.")
                else:
                    ok, msg = canviar_contrasenya(username, vella, nova)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

        st.markdown("---")
        if st.button("Tancar sessió", use_container_width=True):
            esborrar_sessio_url()
            st.session_state.usuari = None
            st.rerun()

def mostrar_admin():
    usuari = st.session_state.usuari
    username = usuari["username"]

    if not es_admin(username):
        st.error("No tens permís per accedir a aquesta secció.")
        return

    tab_usuaris, tab_examens = st.tabs(["Usuaris", "Exàmens"])

    with tab_usuaris:
        usuaris = carregar_usuaris()
        if not usuaris:
            st.info("Encara no hi ha cap usuari registrat.")
        else:
            st.markdown(f"**Total: {len(usuaris)} usuaris**")
            files = [
                {
                    "Usuari": u,
                    "Classe": info.get("classe", "-"),
                    "Creat": info.get("creat", "")[:16].replace("T", " "),
                }
                for u, info in sorted(usuaris.items())
            ]
            st.dataframe(files, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("##### Moure un usuari de classe")
            col1, col2 = st.columns(2)
            with col1:
                usuari_moure = st.selectbox("Usuari", options=[""] + sorted(usuaris.keys()), key="admin_user_moure")
            with col2:
                nova_classe = st.selectbox("Nova classe", CLASSES, key="admin_nova_classe")
            if usuari_moure and st.button("Moure usuari", type="primary", use_container_width=True, key="admin_btn_moure"):
                usuaris[usuari_moure]["classe"] = nova_classe
                desar_usuaris(usuaris)
                st.success(f"'{usuari_moure}' mogut a {nova_classe}.")
                st.rerun()

    with tab_examens:
        examens = carregar_examens()
        st.markdown("##### Afegir un examen nou")
        with st.form("admin_afegir_examen", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                assig = st.text_input("Assignatura *", placeholder="Matemàtiques")
            with col2:
                classe = st.selectbox("Classe *", CLASSES, key="admin_classe_nova")
            col3, col4 = st.columns(2)
            with col3:
                data_ex = st.date_input("Data *", value=date.today(), key="admin_data_nova")
            with col4:
                hora = st.text_input("Hora", placeholder="10:00", key="admin_hora_nova")
            desc = st.text_input("Detalls", placeholder="Temes 3 i 4", key="admin_desc_nova")
            if st.form_submit_button("Afegir examen", type="primary", use_container_width=True):
                if not assig.strip():
                    st.error("Cal omplir com a mínim l'assignatura.")
                else:
                    afegir_examen(assig, classe, data_ex, hora, desc)
                    st.success("Examen afegit!")
                    st.rerun()

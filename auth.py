"""
auth.py - Sistema d'autenticació simple amb fitxer JSON local.
"""
import hashlib
import json
import os
from datetime import datetime

import streamlit as st

USUARIS_PATH = "dades/usuaris.json"

CLASSES = [
    "1r ESO", "2n ESO", "3r ESO", "4t ESO",
    "1r Batxillerat", "2n Batxillerat",
    "Altres",
]


def _hash(password, username):
    base = f"tdr_tutor_matematic::{username.lower()}::{password}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def carregar_usuaris():
    if not os.path.exists(USUARIS_PATH):
        return {}
    try:
        with open(USUARIS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def desar_usuaris(usuaris):
    os.makedirs(os.path.dirname(USUARIS_PATH), exist_ok=True)
    with open(USUARIS_PATH, "w", encoding="utf-8") as f:
        json.dump(usuaris, f, ensure_ascii=False, indent=2)


def registrar(username, password, classe):
    username = username.strip().lower()
    if not username or not password or not classe:
        return False, "Cal omplir tots els camps."
    if len(username) < 3:
        return False, "El nom d'usuari ha de tenir almenys 3 caràcters."
    if len(password) < 4:
        return False, "La contrasenya ha de tenir almenys 4 caràcters."
    usuaris = carregar_usuaris()
    if username in usuaris:
        return False, "Aquest usuari ja existeix."
    usuaris[username] = {
        "password_hash": _hash(password, username),
        "classe": classe,
        "creat": datetime.now().isoformat(),
    }
    desar_usuaris(usuaris)
    return True, "Compte creat! Ara pots iniciar sessió."


def autenticar(username, password):
    username = username.strip().lower()
    usuaris = carregar_usuaris()
    if username not in usuaris:
        return False, "Usuari o contrasenya incorrectes."
    if usuaris[username]["password_hash"] != _hash(password, username):
        return False, "Usuari o contrasenya incorrectes."
    return True, ""


def canviar_contrasenya(username, vella, nova):
    ok, _ = autenticar(username, vella)
    if not ok:
        return False, "La contrasenya actual no és correcta."
    if len(nova) < 4:
        return False, "La nova contrasenya ha de tenir almenys 4 caràcters."
    usuaris = carregar_usuaris()
    usuaris[username]["password_hash"] = _hash(nova, username)
    desar_usuaris(usuaris)
    return True, "Contrasenya canviada correctament."


def canviar_classe(username, nova_classe):
    usuaris = carregar_usuaris()
    if username in usuaris:
        usuaris[username]["classe"] = nova_classe
        desar_usuaris(usuaris)
        st.session_state.usuari["classe"] = nova_classe


def mostrar_login():
    st.markdown("""
    <style>
        .login-hero {
            text-align: center;
            padding: 40px 20px 32px;
        }
        .login-titol {
            font-size: 38px;
            font-weight: 800;
            color: #ffffff;
            margin: 0 0 12px;
            letter-spacing: -0.02em;
            line-height: 1.15;
        }
        .login-titol span {
            background: linear-gradient(90deg, #ffffff 0%, #2b8cee 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .login-hero p.login-subtitol,
        div[data-testid="stMarkdownContainer"] .login-hero p.login-subtitol {
            color: #94a3b8 !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
            margin: 0 auto !important;
            max-width: 400px !important;
            text-align: center !important;
            width: 100% !important;
        }
        .login-hero {
            text-align: center !important;
        }

        /* Formulari net, sense caixes niuades */
        .login-form-wrap {
            max-width: 440px;
            margin: 0 auto;
        }

        /* Tabs mes compactes i clars */
        [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: rgba(255, 255, 255, 0.04);
            padding: 5px;
            border-radius: 999px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-bottom: 32px;
        }
        [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab"] {
            flex: 1;
            justify-content: center;
            padding: 10px 20px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 600;
            color: #94a3b8;
            transition: all 0.2s ease;
        }
        [data-testid="stAppViewContainer"] .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #2b8cee 0%, #1e6fbf 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px -2px rgba(43, 140, 238, 0.5);
        }
        [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab-highlight"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab-border"] {
            display: none !important;
        }

        /* Traurem el border del container si n'hi ha */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-hero">
        <h1 class="login-titol">Tutor <span>Matemàtic IA</span></h1>
        <p class="login-subtitol">
            Inicia sessió o crea un compte per accedir a l'aplicació.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_esq, col_mig, col_dre = st.columns([1, 1.4, 1])
    with col_mig:
        tab_login, tab_registre = st.tabs(["Iniciar sessió", "Crear compte"])

        with tab_login:
            with st.form("form_login", clear_on_submit=False):
                user = st.text_input("Nom d'usuari", placeholder="Escriu el teu nom d'usuari")
                pwd = st.text_input("Contrasenya", type="password", placeholder="Escriu la teva contrasenya")
                st.write("")
                enviat = st.form_submit_button("Entrar", type="primary", use_container_width=True)

                if enviat:
                    ok, err = autenticar(user, pwd)
                    if ok:
                        u = user.strip().lower()
                        usuaris = carregar_usuaris()
                        st.session_state.usuari = {
                            "username": u,
                            "classe": usuaris[u]["classe"],
                        }
                        st.rerun()
                    else:
                        st.error(err)

        with tab_registre:
            with st.form("form_registre", clear_on_submit=False):
                user2 = st.text_input("Nom d'usuari", placeholder="Nom i Cognoms")
                pwd2 = st.text_input("Contrasenya", type="password", placeholder="Mínim 4 caràcters")
                classe = st.selectbox("Classe", CLASSES, index=None,
                                      placeholder="Selecciona la teva classe")
                st.write("")
                enviat2 = st.form_submit_button("Crear compte", type="primary", use_container_width=True)

                if enviat2:
                    ok, msg = registrar(user2, pwd2, classe or "")
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)


def requerir_login():
    if "usuari" not in st.session_state or st.session_state.usuari is None:
        mostrar_login()
        st.stop()


def mostrar_perfil():
    usuari = st.session_state.usuari
    username = usuari["username"]
    classe = usuari["classe"]

    st.markdown(f"""
    <div class="capsalera-app">
        <div class="capsalera-icona"><span class="material-symbols-outlined">account_circle</span></div>
        <div class="capsalera-text">
            <h1>El meu perfil</h1>
            <p>Gestiona el teu compte</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"### 👤 {username.capitalize()}")
        st.caption(f"Classe actual: **{classe}**")

        st.markdown("---")
        st.markdown("#### Canviar de classe")
        nova_classe = st.selectbox("Nova classe", CLASSES,
                                    index=CLASSES.index(classe) if classe in CLASSES else 0,
                                    key="perfil_classe")
        if st.button("Desar canvi de classe", use_container_width=True):
            canviar_classe(username, nova_classe)
            st.success(f"Classe actualitzada a {nova_classe}.")
            st.rerun()

        st.markdown("---")
        st.markdown("#### Canviar contrasenya")
        with st.form("form_canvi_pwd"):
            vella = st.text_input("Contrasenya actual", type="password")
            nova = st.text_input("Nova contrasenya", type="password")
            conf = st.text_input("Confirma la nova contrasenya", type="password")
            enviat = st.form_submit_button("Canviar contrasenya", type="primary", use_container_width=True)
            if enviat:
                if nova != conf:
                    st.error("Les contrasenyes noves no coincideixen.")
                else:
                    ok, msg = canviar_contrasenya(username, vella, nova)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

        st.markdown("---")
        if st.button("🚪 Tancar sessió", use_container_width=True):
            st.session_state.usuari = None
            st.rerun()

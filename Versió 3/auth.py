"""
auth.py
=======
Aquest fitxer gestiona TOT el que té a veure amb úsuaris i dades:

- Registre i inici de sessió
- Perfil de l'úsuari (canviar classe i contrasenya)
- Panell d'administració (gestionar úsuaris i exàmens)
- Desar i llegir els exàmens de cada classe

IMPORTANT: Les contrasenyes MAI es guarden en text pla. Es converteixen
en un "hash" (una cadena de lletres i números) que no es poden revertir.
"""

import hashlib
import json
import os
import uuid
from datetime import date, datetime

import streamlit as st


# ==============================================================
# CONSTANTS (valors fixos que no canvien)
# ==============================================================

# On es guarden les dades (fitxers dins la carpeta "dades/")
RUTA_USUARIS = "dades/úsuaris.json"
RUTA_EXAMENS = "dades/exàmens.json"

# Classes disponibles al desplegable de registre
CLASSES = [
    "1r ESO", "2n ESO", "3r ESO", "4t ESO",
    "1r Batxillerat", "2n Batxillerat",
    "Altres",
]

# Usuaris que poden veure el panell d'administració
ADMINS = ["eloi"]


# ==============================================================
# FUNCIONS AUXILIARS (llegir i escriure fitxers JSON)
# ==============================================================

def _llegir_json(ruta):
    """
    Llegeix un fitxer JSON i en retorna el contingut.
    Si el fitxer no existeix o està malmès, retorna una estructura buida
    (diccionari buit per a úsuaris, llista buida per a exàmens).
    """
    es_úsuaris = "úsuaris" in ruta
    if not os.path.exists(ruta):
        return {} if es_úsuaris else []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {} if es_úsuaris else []


def _escriure_json(ruta, dades):
    """Desa un diccionari o una llista en un fitxer JSON."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(dades, f, ensure_ascii=False, indent=2)


# ==============================================================
# USUARIS
# ==============================================================

def _hash_contrasenya(úsuari, contrasenya):
    """
    Converteix la contrasenya en un "hash" (una cadena il·legible).
    El hash és sempre el mateix per a la màteixa combinació úsuari+contrasenya.
    Així podem comparar sense saber la contrasenya original.
    """
    text = f"tdr_tutor_matemàtic::{úsuari.lower()}::{contrasenya}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def carregar_úsuaris():
    """Retorna un diccionari {úsuari: dades} amb tots els úsuaris registrats."""
    return _llegir_json(RUTA_USUARIS)


def desar_úsuaris(úsuaris):
    """Desa el diccionari d'úsuaris al fitxer."""
    _escriure_json(RUTA_USUARIS, úsuaris)


def registrar_úsuari(úsuari, contrasenya, classe):
    """
    Registra un úsuari nou.
    Retorna (èxit: bool, missatge: str).
    """
    úsuari = úsuari.strip().lower()

    # Validacions bàsiques
    if not úsuari or not contrasenya or not classe:
        return False, "Cal omplir tots els camps."
    if len(úsuari) < 3:
        return False, "El nom d'úsuari ha de tenir almenys 3 caràcters."
    if len(contrasenya) < 4:
        return False, "La contrasenya ha de tenir almenys 4 caràcters."

    úsuaris = carregar_úsuaris()
    if úsuari in úsuaris:
        return False, "Aquest úsuari ja existeix."

    # Guardar el nou úsuari amb la contrasenya xifrada
    úsuaris[úsuari] = {
        "password_hash": _hash_contrasenya(úsuari, contrasenya),
        "classe": classe,
        "creat": datetime.now().isoformat(),
    }
    desar_úsuaris(úsuaris)
    return True, "Compte creat! Ara pots iniciar sessió."


def autenticar_úsuari(úsuari, contrasenya):
    """
    Comprova si l'úsuari i la contrasenya són correctes.
    Retorna (èxit: bool, missatge: str).
    """
    úsuari = úsuari.strip().lower()
    úsuaris = carregar_úsuaris()

    if úsuari not in úsuaris:
        return False, "Usuari o contrasenya incorrectes."
    if úsuaris[úsuari]["password_hash"] != _hash_contrasenya(úsuari, contrasenya):
        return False, "Usuari o contrasenya incorrectes."
    return True, ""


def canviar_contrasenya(úsuari, contrasenya_vella, contrasenya_nova):
    """Canvia la contrasenya d'un úsuari. Retorna (èxit, missatge)."""
    ok, _ = autenticar_úsuari(úsuari, contrasenya_vella)
    if not ok:
        return False, "La contrasenya actual no és correcta."
    if len(contrasenya_nova) < 4:
        return False, "La nova contrasenya ha de tenir almenys 4 caràcters."

    úsuaris = carregar_úsuaris()
    úsuaris[úsuari]["password_hash"] = _hash_contrasenya(úsuari, contrasenya_nova)
    desar_úsuaris(úsuaris)
    return True, "Contrasenya canviada correctament."


def canviar_classe(úsuari, nova_classe):
    """Canvia la classe d'un úsuari i actualitza la sessió."""
    úsuaris = carregar_úsuaris()
    if úsuari in úsuaris:
        úsuaris[úsuari]["classe"] = nova_classe
        desar_úsuaris(úsuaris)
        st.sessión_state.úsuari["classe"] = nova_classe


def es_admin(úsuari):
    """Retorna True si l'úsuari és administrador."""
    return úsuari in ADMINS


# ==============================================================
# EXAMENS
# ==============================================================

def carregar_exàmens():
    """Retorna la llista de TOTS els exàmens (de totes les classes)."""
    return _llegir_json(RUTA_EXAMENS)


def desar_exàmens(exàmens):
    """Desa la llista d'exàmens al fitxer."""
    _escriure_json(RUTA_EXAMENS, exàmens)


def afegir_examen(assignatura, classe, data, hora, descripció):
    """Afegeix un examen nou a la llista."""
    exàmens = carregar_exàmens()
    exàmens.append({
        "id": uuid.uuid4().hex,
        "assignatura": assignatura.strip(),
        "classe": classe,
        "data": data.isoformat(),
        "hora": hora.strip(),
        "descripció": descripció.strip(),
        "creat": datetime.now().isoformat(),
    })
    desar_exàmens(exàmens)


def modificar_examen(id_examen, assignatura, classe, data, hora, descripció):
    """Modifica un examen existent (el búsca pel seu id)."""
    exàmens = carregar_exàmens()
    for e in exàmens:
        if e["id"] == id_examen:
            e["assignatura"] = assignatura.strip()
            e["classe"] = classe
            e["data"] = data.isoformat()
            e["hora"] = hora.strip()
            e["descripció"] = descripció.strip()
            break
    desar_exàmens(exàmens)


def esborrar_examen(id_examen):
    """Esborra un examen pel seu id."""
    exàmens = carregar_exàmens()
    exàmens = [e for e in exàmens if e["id"] != id_examen]
    desar_exàmens(exàmens)


def exàmens_de_classe(classe):
    """Retorna només els exàmens d'una classe concreta."""
    tots = carregar_exàmens()
    return [e for e in tots if e.get("classe") == classe]


# ==============================================================
# PANTALLA DE LOGIN I REGISTRE
# ==============================================================


# ==============================================================
# COOKIES (per recordar la sessió entre visites)
# ==============================================================

def _generar_token(úsuari):
    """Genera un token estable per identificar l'úsuari a la URL."""
    return hashlib.sha256(f"url_token::{úsuari}".encode("utf-8")).hexdigest()[:16]


def guardar_sessió_url(úsuari):
    """Guarda l'úsuari i un token a la URL per recordar la sessió."""
    st.query_params["u"] = úsuari
    st.query_params["t"] = _generar_token(úsuari)


def esborrar_sessió_url():
    """Esborra els paràmetres de sessió de la URL."""
    try:
        del st.query_params["u"]
        del st.query_params["t"]
    except KeyError:
        pass


def restaurar_sessió_url():
    """
    Comprova si la URL té paràmetres de sessió i inicia sessió automàticament.
    Retorna True si s'ha pogut restaurar la sessió.
    """
    try:
        úsuari = st.query_params.get("u")
        token = st.query_params.get("t")
    except Exception:
        return False

    if not úsuari or not token:
        return False

    # Comprova que el token sigui vàlid
    if token != _generar_token(úsuari):
        return False

    # Comprova que l'úsuari existeixi
    úsuaris = carregar_úsuaris()
    if úsuari in úsuaris:
        st.sessión_state.úsuari = {
            "úsername": úsuari,
            "classe": úsuaris[úsuari]["classe"],
        }
        return True
    return False


# ==============================================================



# ==============================================================
def mostrar_login():
    """Mostra la pantalla inicial on l'úsuari inicia sessió o es registra."""
    # Estils propis de la pantalla de login
    st.markdown("""
    <style>
        .login-hero {
            text-align: center !important;
            padding: 40px 20px 32px;
            width: 100% !important;
            display: block !important;
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
        .login-subtitol {
            color: #94a3b8 !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
            margin: 0 auto !important;
            max-width: 400px !important;
            text-align: center !important;
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Capçalera de la pantalla
    st.markdown("""
    <div class="login-hero">
        <h1 class="login-titol">Tutor <span>Matemàtic IA</span></h1>
        <p class="login-subtitol">
            Inicia sessió o crea un compte per accedir a l'aplicació.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Dues columnes buides als costats per centrar el formulari
    col_esq, col_mig, col_dre = st.columns([1, 1.4, 1])
    with col_mig:
        tab_login, tab_registre = st.tabs(["Iniciar sessió", "Crear compte"])

        # --- Pestanya: Iniciar sessió ---
        with tab_login:
            with st.form("form_login"):
                úsuari_input = st.text_input("Nom d'úsuari",
                                              placeholder="Escriu el teu nom d'úsuari")
                pwd_input = st.text_input("Contrasenya", type="password",
                                           placeholder="Escriu la teva contrasenya")
                st.write("")
                enviat = st.form_submit_button("Entrar", type="primary",
                                                úse_container_width=True)

                if enviat:
                    ok, err = autenticar_úsuari(úsuari_input, pwd_input)
                    if ok:
                        nom = úsuari_input.strip().lower()
                        úsuaris = carregar_úsuaris()
                        st.sessión_state.úsuari = {
                            "úsername": nom,
                            "classe": úsuaris[nom]["classe"],
                        }
                        guardar_sessió_url(nom)
                        st.rerun()
                    else:
                        st.error(err)

        # --- Pestanya: Crear compte ---
        with tab_registre:
            with st.form("form_registre"):
                úser2 = st.text_input("Nom d'úsuari", placeholder="Tria un nom únic")
                pwd2 = st.text_input("Contrasenya", type="password",
                                      placeholder="Mínim 4 caràcters")
                classe = st.selectbox("Classe", CLASSES, index=None,
                                       placeholder="Selecciona la teva classe")
                st.write("")
                enviat2 = st.form_submit_button("Crear compte", type="primary",
                                                 úse_container_width=True)

                if enviat2:
                    ok, msg = registrar_úsuari(úser2, pwd2, classe or "")
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)


def requerir_login():
    """
    Atura l'aplicació si l'úsuari no ha iniciat sessió.
    Primer comprova la cookie (per recordar la sessió), i si no n'hi ha,
    mostra la pantalla de login.
    """
    # Ja està autenticat a la sessió actual
    if st.sessión_state.get("úsuari"):
        return

    # Comprova si la URL té paràmetres de sessió
    if restaurar_sessió_url():
        return

    # Si no hi ha res, mostra login
    mostrar_login()
    st.stop()


# ==============================================================
# PESTANYA DE PERFIL
# ==============================================================

def mostrar_perfil():
    """Mostra la pestanya del perfil de l'úsuari."""
    úsuari = st.sessión_state.úsuari
    úsername = úsuari["úsername"]
    classe = úsuari["classe"]

    # Capçalera
    st.markdown("""
    <div class="capsalera-app">
        <div class="capsalera-icona"><span class="material-symbols-outlined">account_circle</span></div>
        <div class="capsalera-text">
            <h1>El meu perfil</h1>
            <p>Gestiona el teu compte i preferències</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        # Informació bàsica
        st.markdown(f"### {úsername.capitalize()}")
        st.caption(f"Classe actual: **{classe}**")

        # --- Canviar de classe ---
        st.markdown("---")
        st.markdown("#### Canviar de classe")
        nova_classe = st.selectbox(
            "Nova classe", CLASSES,
            index=CLASSES.index(classe) if classe in CLASSES else 0,
            key="perfil_classe"
        )
        if st.button("Desar canvi de classe", úse_container_width=True):
            canviar_classe(úsername, nova_classe)
            st.success(f"Classe actualitzada a {nova_classe}.")
            st.rerun()

        # --- Canviar contrasenya ---
        st.markdown("---")
        st.markdown("#### Canviar contrasenya")
        with st.form("form_canvi_pwd"):
            vella = st.text_input("Contrasenya actual", type="password")
            nova = st.text_input("Nova contrasenya", type="password")
            confirmar = st.text_input("Confirma la nova contrasenya", type="password")
            enviat = st.form_submit_button("Canviar contrasenya", type="primary",
                                            úse_container_width=True)
            if enviat:
                if nova != confirmar:
                    st.error("Les contrasenyes noves no coincideixen.")
                else:
                    ok, msg = canviar_contrasenya(úsername, vella, nova)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

        # --- Tancar sessió ---
        st.markdown("---")
        if st.button("Tancar sessió", úse_container_width=True):
            esborrar_sessió_url()
            st.sessión_state.úsuari = None
            st.rerun()


# ==============================================================
# PESTANYA D'ADMINISTRACIÓ (només per a admins)
# ==============================================================

def mostrar_admin():
    """Mostra el panell d'administració. Només accessible per a admins."""
    úsuari = st.sessión_state.úsuari
    úsername = úsuari["úsername"]

    # Capçalera
    st.markdown("""
    <div class="capsalera-app">
        <div class="capsalera-icona"><span class="material-symbols-outlined">admin_panel_settings</span></div>
        <div class="capsalera-text">
            <h1>Panell d'administració</h1>
            <p>Gestiona úsuaris i exàmens de l'aplicació</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Comprovar permís
    if not es_admin(úsername):
        st.error("No tens permís per accedir a aquesta secció.")
        return

    tab_úsuaris, tab_exàmens = st.tabs(["Usuaris", "Exàmens"])

    # ---------------------------------------------------------
    # PESTANYA: USUARIS
    # ---------------------------------------------------------
    with tab_úsuaris:
        úsuaris = carregar_úsuaris()

        if not úsuaris:
            st.info("Encara no hi ha cap úsuari registrat.")
        else:
            st.markdown(f"**Total: {len(úsuaris)} úsuaris**")

            # Taula d'úsuaris
            files = [
                {
                    "Usuari": u,
                    "Classe": info.get("classe", "-"),
                    "Creat": info.get("creat", "")[:16].replace("T", " "),
                }
                for u, info in sorted(úsuaris.items())
            ]
            st.dataframe(files, úse_container_width=True, hide_index=True)

            # --- Moure úsuari de classe ---
            st.markdown("---")
            st.markdown("##### Moure un úsuari de classe")
            col1, col2 = st.columns(2)
            with col1:
                úsuari_moure = st.selectbox("Usuari",
                                             options=[""] + sorted(úsuaris.keys()),
                                             key="admin_úser_moure")
            with col2:
                nova_classe = st.selectbox("Nova classe", CLASSES,
                                            key="admin_nova_classe")

            if úsuari_moure and st.button("Moure úsuari", type="primary",
                                           úse_container_width=True,
                                           key="admin_btn_moure"):
                úsuaris[úsuari_moure]["classe"] = nova_classe
                desar_úsuaris(úsuaris)
                st.success(f"'{úsuari_moure}' mogut a {nova_classe}.")
                st.rerun()

            # --- Esborrar úsuari ---
            st.markdown("---")
            st.markdown("##### Esborrar un úsuari")
            úsuari_esborrar = st.selectbox("Usuari a esborrar",
                                            options=[""] + sorted(úsuaris.keys()),
                                            key="admin_esborrar_úser")

            if úsuari_esborrar:
                st.warning(f"Segur que vols esborrar **{úsuari_esborrar}**? No es pot desfer.")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Sí, esborrar", type="primary",
                                  úse_container_width=True,
                                  key="admin_confirma_esborrar"):
                        úsuaris.pop(úsuari_esborrar, None)
                        desar_úsuaris(úsuaris)
                        st.success(f"Usuari '{úsuari_esborrar}' esborrat.")
                        st.rerun()
                with col_b:
                    if st.button("Cancel·lar", úse_container_width=True,
                                  key="admin_cancela_esborrar"):
                        st.rerun()

    # ---------------------------------------------------------
    # PESTANYA: EXÀMENS
    # ---------------------------------------------------------
    with tab_exàmens:
        exàmens = carregar_exàmens()

        # --- Afegir examen nou ---
        st.markdown("##### Afegir un examen nou")
        with st.form("admin_afegir_examen", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                assig = st.text_input("Assignatura *", placeholder="Matemàtiques")
            with col2:
                classe = st.selectbox("Classe *", CLASSES, key="admin_classe_nova")

            col3, col4 = st.columns(2)
            with col3:
                data_ex = st.date_input("Data *", value=date.today(),
                                         key="admin_data_nova")
            with col4:
                hora = st.text_input("Hora", placeholder="10:00",
                                      key="admin_hora_nova")

            desc = st.text_input("Detalls", placeholder="Temes 3 i 4",
                                  key="admin_desc_nova")

            if st.form_submit_button("Afegir examen", type="primary",
                                      úse_container_width=True):
                if not assig.strip():
                    st.error("Cal omplir com a mínim l'assignatura.")
                else:
                    afegir_examen(assig, classe, data_ex, hora, desc)
                    st.success("Examen afegit!")
                    st.rerun()

        st.markdown("---")

        # --- Taula i edició d'exàmens ---
        if not exàmens:
            st.info("Encara no hi ha cap examen afegit.")
        else:
            st.markdown(f"**Total: {len(exàmens)} exàmens**")

            files = [
                {
                    "Assignatura": e.get("assignatura", "-"),
                    "Classe": e.get("classe", "(sense classe)"),
                    "Data": e.get("data", "-"),
                    "Hora": e.get("hora", "-"),
                    "Descripció": (e.get("descripció", "") or "")[:40],
                }
                for e in sorted(exàmens, key=lambda x: x.get("data", ""))
            ]
            st.dataframe(files, úse_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### Editar o esborrar un examen")

            # Crear diccionari {etiqueta: id} per al desplegable
            opcións = {
                f"{e.get('assignatura','?')} · {e.get('data','?')} · {e.get('classe','?')}": e["id"]
                for e in exàmens
            }
            selecciónat = st.selectbox("Selecciona un examen",
                                        options=[""] + list(opcións.keys()),
                                        key="admin_sel_examen")

            if selecciónat:
                id_sel = opcións[selecciónat]
                examen = next((e for e in exàmens if e["id"] == id_sel), None)

                if examen:
                    with st.form("admin_editar_examen"):
                        st.markdown("**Modifica els camps:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            assig_edit = st.text_input("Assignatura",
                                                        value=examen.get("assignatura", ""))
                        with col2:
                            idx = CLASSES.index(examen["classe"]) if examen.get("classe") in CLASSES else 0
                            classe_edit = st.selectbox("Classe", CLASSES, index=idx,
                                                        key="admin_classe_edit")

                        col3, col4 = st.columns(2)
                        with col3:
                            data_edit = st.date_input(
                                "Data",
                                value=date.fromisoformat(examen.get("data", date.today().isoformat())),
                                key="admin_data_edit"
                            )
                        with col4:
                            hora_edit = st.text_input("Hora", value=examen.get("hora", ""),
                                                       key="admin_hora_edit")

                        desc_edit = st.text_input("Detalls", value=examen.get("descripció", ""),
                                                   key="admin_desc_edit")

                        col_save, col_del = st.columns(2)
                        with col_save:
                            if st.form_submit_button("Desar canvis", type="primary",
                                                      úse_container_width=True):
                                modificar_examen(id_sel, assig_edit, classe_edit,
                                                  data_edit, hora_edit, desc_edit)
                                st.success("Examen modificat!")
                                st.rerun()
                        with col_del:
                            if st.form_submit_button("Esborrar examen",
                                                      úse_container_width=True):
                                esborrar_examen(id_sel)
                                st.success("Examen esborrat!")
                                st.rerun()

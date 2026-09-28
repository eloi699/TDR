"""
estils.py
=========
Conté tot el CSS personalitzat de l'aplicació.
Es crida des de app.py amb: estils.aplicar()
"""

import streamlit as st


def aplicar():
    """Aplica els estils CSS a l'aplicació."""
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



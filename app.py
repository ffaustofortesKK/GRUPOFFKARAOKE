import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from modulos.db import obter_prestadores

st.set_page_config(
    page_title="FFKaraoke — Sistema Principal",
    page_icon="🎤",
    layout="wide",
)

# --- CSS PARA ESCONDER A BARRA LATERAL (SIDEBAR) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    .main {
        background-color: #09090b;
        color: #fafafa;
    }
    .stButton>button {
        background-color: #eab308;
        color: #000000;
        font-weight: bold;
        border-radius: 6px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ca8a04;
        color: #ffffff;
    }
    h1, h2, h3 {
        color: #eab308 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA SESSÃO GLOBAL ---
if "logged" not in st.session_state:
    st.session_state.logged = False

# Carrega os prestadores diretamente da base de dados local (JSON)
st.session_state.prestadores = obter_prestadores()

if "reforcos" not in st.session_state:
    st.session_state.reforcos = []

if "historico" not in st.session_state:
    st.session_state.historico = [
        {"acao": "Sistema Iniciado", "detalhe": "Plataforma FFKaraoke carregada.", "data": "Hoje"}
    ]

# --- SISTEMA DE ROTAS POR PARÂMETRO DE URL ---
query_params = st.query_params
view = query_params.get("view", "admin")

# Carrega o módulo correspondente executando a respetiva função render()
if view == "admin":
    from modulos import admin
    admin.render()
elif view == "prestador":
    from modulos import prestador
    prestador.render()
elif view == "cliente":
    from modulos import cliente
    cliente.render()
elif view == "tela":
    from modulos import tela
    tela.render()
else:
    st.error("Página não encontrada.")

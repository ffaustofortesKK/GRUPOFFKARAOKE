import sys

import os

import importlib.util



# Garante que o diretório atual está no caminho do sistema

current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:

    sys.path.insert(0, current_dir)



import streamlit as st

from db import obter_prestadores



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



try:

    st.session_state.prestadores = obter_prestadores()

except Exception:

    st.session_state.prestadores = []



if "reforcos" not in st.session_state:

    st.session_state.reforcos = []



if "historico" not in st.session_state:

    st.session_state.historico = [

        {"acao": "Sistema Iniciado", "detalhe": "Plataforma FFKaraoke carregada.", "data": "Hoje"}

    ]



# Função auxiliar para carregar módulos locais com segurança total por caminho de ficheiro

def carregar_modulo(nome_ficheiro):

    caminho = os.path.join(current_dir, nome_ficheiro)

    spec = importlib.util.spec_from_file_location(nome_ficheiro.replace(".py", ""), caminho)

    modulo = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(modulo)

    return modulo



# --- SISTEMA DE ROTAS POR PARÂMETRO DE URL ---

query_params = st.query_params



# Suporta tanto ?view=... quanto ?page=... e define "prestador" como padrão inicial

view = query_params.get("view", query_params.get("page", "prestador"))



# Executa o módulo correspondente carregando-o diretamente pelo nome do ficheiro

try:

    if view == "admin":

        mod = carregar_modulo("admin.py")

        mod.render()

    elif view == "prestador":

        mod = carregar_modulo("prestador.py")

        mod.render()

    elif view == "cliente":

        mod = carregar_modulo("cliente.py")

        mod.render()

    elif view == "tela":

        mod = carregar_modulo("tela.py")

        mod.render()

    else:

        st.error("Página não encontrada.")

except Exception as e:

    st.error(f"Erro ao carregar o módulo '{view}': {e}") 

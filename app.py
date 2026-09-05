import importlib.util
import os
import sys
print("Caminho atual do ficheiro:", os.path.abspath(__file__))

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

# --- CSS PROFISSIONAL PARA A INTERFACE ---
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        .main {
            background-color: #0f0f11;
            color: #fafafa;
        }
        h1, h2, h3 {
            color: #eab308 !important;
        }
        
        /* Ajuste de Margens Gerais da Página */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }

        /* Container Estilizado Padrão */
        .box-container {
            background-color: #121214;
            border: 1px solid #27272a;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .box-title {
            color: #eab308;
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .box-content {
            color: #d4d4d8;
            font-size: 12px;
        }

        /* Cabeçalho superior */
        .header-box {
            background-color: #18181b;
            border: 1px solid #27272a;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        /* Estilização Geral de Botões Streamlit */
        .stButton button {
            border-radius: 6px !important;
            font-weight: bold !important;
            transition: all 0.2s ease-in-out !important;
        }
        .stButton button:hover {
            transform: translateY(-1px);
            opacity: 0.95;
        }
    </style>
""",
    unsafe_allow_html=True,
)

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
  st.session_state.historico = [{
      "acao": "Sistema Iniciado",
      "detalhe": "Plataforma FFKaraoke carregada.",
      "data": "Hoje",
  }]


# Função auxiliar para carregar módulos locais com segurança total por caminho de ficheiro
def carregar_modulo(nome_ficheiro):
  caminho = os.path.join(current_dir, nome_ficheiro)
  spec = importlib.util.spec_from_file_location(
      nome_ficheiro.replace(".py", ""), caminho
  )
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

import streamlit as st

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

# --- INICIALIZAÇÃO DA BASE DE DADOS GLOBAL EM SESSÃO ---
if "logged" not in st.session_state:
    st.session_state.logged = False

if "prestadores" not in st.session_state:
    st.session_state.prestadores = [
        {"token": "demo-111", "nome": "João Silva", "telefone": "921000000", "estabelecimento": "Bar Central", "plano": "1 Hora - 12 Mil Kwanzas", "approved": True, "segundos_restantes": 3600},
        {"token": "pend-222", "nome": "Carlos Mendes", "telefone": "923111222", "estabelecimento": "Restaurante O Kubico", "plano": "2 Horas - 17 Mil Kwanzas", "approved": False, "segundos_restantes": 7200}
    ]

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

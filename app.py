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
        {"token": "demo-token-1", "nome": "João Silva", "telefone": "921000000", "plano": "Standard", "approved": True, "segundos_restantes": 3600},
        {"token": "demo-token-2", "nome": "Maria Santos", "telefone": "923000000", "plano": "VIP", "approved": False, "segundos_restantes": 7200},
    ]

if "reforcos" not in st.session_state:
    st.session_state.reforcos = [
        {"id": "ref-1", "nome_prestador": "João Silva", "referencia": "REF12345", "plano": "1 Hora Extra", "provider_token": "demo-token-1"}
    ]

if "historico" not in st.session_state:
    st.session_state.historico = [
        {"acao": "Registo aprovado", "detalhe": "João Silva foi aprovado no sistema.", "data": "Hoje"}
    ]

# --- SISTEMA DE ROTAS POR PARÂMETRO DE URL ---
query_params = st.query_params
view = query_params.get("view", "admin")

# Carrega o módulo correspondente
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
    if st.button("Ir para Administração"):
        st.query_params["view"] = "admin"
        st.rerun()

import streamlit as st

# Configuração da página e visual Preto e Dourado
st.set_page_config(
    page_title="FFKaraoke — Painel do Administrador",
    page_icon="🎤",
    layout="wide",
)

# Palavra-passe de administrador definida diretamente aqui
ADMIN_PASSWORD = "admin"

# Inicializar o estado da sessão (simulando a base de dados em memória/sessão)
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

# Estilos CSS personalizados para simular o tema preto e dourado / Tailwind
st.markdown("""
    <style>
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

def formatarTempo(segundos: int) -> str:
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    secs = segundos % 60
    if horas > 0:
        return f"{horas}h {minutos}m"
    return f"{minutos}m {secs}s"

# --- CABEÇALHO ---
st.title("FFKaraoke · Administração")
st.caption("Gestão de acessos ao programa FFK")
st.divider()

# --- LÓGICA DE LOGIN / DASHBOARD ---
if not st.session_state.logged:
    st.subheader("🔒 Área restrita")
    with st.form("login_form"):
        password_input = st.text_input("Palavra-passe de administrador", type="password")
        submit_login = st.form_submit_button("Entrar")
        
        if submit_login:
            if password_input == ADMIN_PASSWORD:
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("Palavra-passe incorreta.")
                
    st.markdown("---")
    st.markdown("É prestador? [Faça aqui o seu registo](#)")

else:
    # Botão de Terminar Sessão
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("Terminar sessão"):
            st.session_state.logged = False
            st.rerun()

    pendentes = [p for p in st.session_state.prestadores if not p["approved"]]
    ativos = [p for p in st.session_state.prestadores if p["approved"]]

    # --- SEÇÃO: REGISTOS PENDENTES ---
    st.subheader(f"⏳ Registos pendentes ({len(pendentes)})")
    if not pendentes:
        st.info("Nenhum registo à espera de aprovação.")
    else:
        for p in pendentes:
            with st.container(border=True):
                st.markdown(f"**{p['nome']}**")
                st.caption(f"Telefone: {p['telefone']} · Plano: {p['plano']} · Token: {p['token']}")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Aprovar", key=f"aprov_{p['token']}"):
                        p["approved"] = True
                        st.rerun()
                with col_b:
                    if st.button("❌ Recusar", key=f"rec_{p['token']}"):
                        st.session_state.prestadores = [x for x in st.session_state.prestadores if x["token"] != p["token"]]
                        st.rerun()

    # --- SEÇÃO: REFORÇOS DE TEMPO ---
    st.subheader(f"⚡ Reforços de tempo pendentes ({len(st.session_state.reforcos)})")
    if not st.session_state.reforcos:
        st.info("Nenhum pedido de reforço neste momento.")
    else:
        for r in st.session_state.reforcos:
            with st.container(border=True):
                st.markdown(f"**{r['nome_prestador']}**")
                st.caption(f"Referência: {r['referencia']} · Duração: {r['plano']} · Token: {r['provider_token']}")
                col_c, col_d = st.columns(2)
                with col_c:
                    if st.button("✅ Aprovar reforço", key=f"ref_ok_{r['id']}"):
                        # Adiciona tempo ao prestador correspondente
                        for p in st.session_state.prestadores:
                            if p["token"] == r["provider_token"]:
                                p["segundos_restantes"] += 3600
                        st.session_state.reforcos = [x for x in st.session_state.reforcos if x["id"] != r["id"]]
                        st.rerun()
                with col_d:
                    if st.button("❌ Recusar", key=f"ref_no_{r['id']}"):
                        st.session_state.reforcos = [x for x in st.session_state.reforcos if x["id"] != r["id"]]
                        st.rerun()

    # --- SEÇÃO: PRESTADORES ATIVOS ---
    st.subheader(f"🎤 Prestadores ativos ({len(ativos)})")
    if not ativos:
        st.info("Ainda não há prestadores aprovados.")
    else:
        for p in ativos:
            with st.container(border=True):
                tempo_str = formatarTempo(p["segundos_restantes"])
                cor_tempo = "🔴" if p["segundos_restantes"] <= 1800 else "🟢"
                st.markdown(f"**{p['nome']}** — Plano: {p['plano']}")
                st.write(f"Tempo restante: {cor_tempo} **{tempo_str}**")
                
                col_e, col_f, col_g = st.columns(3)
                with col_e:
                    if st.button("Suspender", key=f"susp_{p['token']}"):
                        p["approved"] = False
                        st.rerun()
                with col_f:
                    if st.button("Apagar", key=f"del_{p['token']}"):
                        st.session_state.prestadores = [x for x in st.session_state.prestadores if x["token"] != p["token"]]
                        st.rerun()

# --- RODAPÉ MARQUEE ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #eab308; font-weight: bold;'>🎤 FF KARAOKE CLOUD · GESTÃO DE PRESTADORES · 921204050</p>", unsafe_allow_html=True)

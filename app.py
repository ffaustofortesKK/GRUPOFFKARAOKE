import streamlit as st
import uuid

# Configuração da página e visual Preto e Dourado
st.set_page_config(
    page_title="FFKaraoke — Gestão Completa",
    page_icon="🎤",
    layout="wide",
)

ADMIN_PASSWORD = "admin"

# --- INICIALIZAÇÃO DA BASE DE DADOS EM SESSÃO ---
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
        {"acao": "Registo aprovado", "detalhe": "João Silva foi aprovado no sistema.", "data": "2026-06-01"}
    ]

# --- ESTILOS CSS ---
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

# --- SISTEMA DE ROTAS / ABAS PRINCIPAIS ---
query_params = st.query_params
view = query_params.get("view", "admin")

st.sidebar.title("🎤 FFKaraoke Navigation")
escolha_menu = st.sidebar.radio("Ir para:", ["Administrador", "Prestador", "Cliente", "Tela"], index=0 if view=="admin" else (1 if view=="prestador" else (2 if view=="cliente" else 3)))

if escolha_menu == "Administrador":
    st.query_params["view"] = "admin"
    
    st.title("FFKaraoke · Administração")
    st.caption("Gestão de acessos e controlos do programa FFK")
    st.divider()

    # Login Logic
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
        if st.button("👉 Sou prestador / Quero registar-me"):
            st.query_params["view"] = "prestador"
            st.rerun()

    else:
        col_l1, col_l2 = st.columns([8, 2])
        with col_l2:
            if st.button("Terminar sessão"):
                st.session_state.logged = False
                st.rerun()

        # As 3 Abas do Administrador solicitadas
        aba1, aba2, aba3 = st.tabs(["1º Pedidos e Aprovação", "2º Gestão Online", "3º Controle de Gestão"])

        # ABA 1: Pedidos e Aprovação
        with aba1:
            pendentes = [p for p in st.session_state.prestadores if not p["approved"]]
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
                                st.session_state.historico.append({"acao": "Aprovação", "detalhe": f"Prestador {p['nome']} aprovado.", "data": "Hoje"})
                                st.rerun()
                        with col_b:
                            if st.button("❌ Recusar", key=f"rec_{p['token']}"):
                                st.session_state.prestadores = [x for x in st.session_state.prestadores if x["token"] != p["token"]]
                                st.session_state.historico.append({"acao": "Recusa", "detalhe": f"Prestador {p['nome']} foi recusado/removido.", "data": "Hoje"})
                                st.rerun()

            # Reforços de tempo pendentes também entram aqui
            st.markdown("---")
            st.subheader(f"⚡ Reforços de tempo pendentes ({len(st.session_state.reforcos)})")
            if not st.session_state.reforcos:
                st.info("Nenhum pedido de reforço neste momento.")
            else:
                for r in st.session_state.reforcos:
                    with st.container(border=True):
                        st.markdown(f"**{r['nome_prestador']}**")
                        st.caption(f"Referência: {r['referencia']} · Duração: {r['plano']}")
                        if st.button("✅ Aprovar reforço", key=f"ref_ok_{r['id']}"):
                            for p in st.session_state.prestadores:
                                if p["token"] == r["provider_token"]:
                                    p["segundos_restantes"] += 3600
                            st.session_state.reforcos = [x for x in st.session_state.reforcos if x["id"] != r["id"]]
                            st.rerun()

        # ABA 2: Gestão Online
        with aba2:
            ativos = [p for p in st.session_state.prestadores if p["approved"]]
            st.subheader(f"🟢 Prestadores Ativos / Online ({len(ativos)})")
            if not ativos:
                st.info("Nenhum prestador ativo no momento.")
            else:
                for p in ativos:
                    with st.container(border=True):
                        tempo_str = formatarTempo(p["segundos_restantes"])
                        st.markdown(f"**{p['nome']}** — Plano: {p['plano']}")
                        st.write(f"Tempo restante: **{tempo_str}** | Token: `{p['token']}`")
                        
                        col_e, col_f = st.columns(2)
                        with col_e:
                            if st.button("Suspender Acesso", key=f"susp_{p['token']}"):
                                p["approved"] = False
                                st.rerun()
                        with col_f:
                            if st.button("Apagar Definitivamente", key=f"del_{p['token']}"):
                                st.session_state.prestadores = [x for x in st.session_state.prestadores if x["token"] != p["token"]]
                                st.rerun()

        # ABA 3: Controle de Gestão
        with aba3:
            st.subheader("📊 Histórico e Informações Gerais")
            st.write("Registo de toda a atividade que passou pelo programa:")
            for h in st.session_state.historico:
                st.markdown(f"- **[{h['data']}] {h['acao']}**: {h['detalhe']}")

elif escolha_menu == "Prestador":
    st.query_params["view"] = "prestador"
    st.title("🎤 Área do Prestador - FFKaraoke")
    st.write("Inscreva-se ou aceda ao seu painel de controlo de prestador.")
    
    tab_reg, tab_painel = st.tabs(["📝 Novo Registo", "🔑 Aceder com Token"])
    
    with tab_reg:
        with st.form("form_registo_prestador"):
            nome_p = st.text_input("Nome Completo / Estabelecimento")
            tel_p = st.text_input("Telefone")
            plano_p = st.selectbox("Escolha o Plano", ["Standard (1h)", "VIP (2h)"])
            submit_reg = st.form_submit_button("Submeter Registo")
            
            if submit_reg and nome_p and tel_p:
                novo_token = str(uuid.uuid4())[:8]
                st.session_state.prestadores.append({
                    "token": novo_token,
                    "nome": nome_p,
                    "telefone": tel_p,
                    "plano": plano_p,
                    "approved": False,
                    "segundos_restantes": 3600
                })
                st.success(guardar_msg := f"Registo efetuado com sucesso! O seu token de acesso pendente é: **{novo_token}**. Aguarde a aprovação do Administrador.")

    with tab_painel:
        token_input = st.text_input("Introduza o seu Token de Prestador")
        if st.button("Entrar no Painel"):
            prestador_encontrado = next((p for p in st.session_state.prestadores if p["token"] == token_input), None)
            if prestador_encontrado:
                if not prestador_encontrado["approved"]:
                    st.warning("O seu registo ainda está pendente de aprovação pelo Administrador.")
                else:
                    st.success(f"Bem-vindo, {prestador_encontrado['nome']}!")
                    st.markdown("---")
                    st.subheader("🔗 Links Úteis para o seu Karaoke")
                    
                    # Links gerados dinamicamente para o prestador utilizar
                    link_cliente = f"http://localhost:8501/?view=cliente&token={prestador_encontrado['token']}"
                    link_tela = f"http://localhost:8501/?view=tela&token={prestador_encontrado['token']}"
                    
                    st.markdown(f"**Link para inscrição de Clientes:**")
                    st.code(link_cliente)
                    
                    fn_link = f"**Link da Tela (Apresentação/Fila):**"
                    st.markdown(fn_link)
                    st.code(link_tela)
            else:
                st.error("Token não encontrado.")

elif escolha_menu == "Cliente":
    st.query_params["view"] = "cliente"
    st.title("🎵 FFKaraoke · Inscrição do Cliente")
    token_prestador = query_params.get("token", "Nenhum")
    st.info(f机关=f"Sessão vinculada ao Prestador Token: `{token_prestador}`")
    
    with st.form("form_cliente"):
        cantor = st.text_input("O seu Nome")
        musica = st.text_input("Nome da Música / Artista")
        if st.form_submit_button("Pedir Música"):
            st.success(f"Obrigado {cantor}! A sua música '{musica}' foi adicionada à fila.")

elif escolha_menu == "Tela":
    st.query_params["view"] = "tela"
    st.title("📺 FFKaraoke · Tela de Exibição")
    st.write("Esta tela exibe as músicas a cantar em direto para o público.")
    st.info("A aguardar próxima atuação...")

# --- RODAPÉ ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #eab308; font-weight: bold;'>🎤 FF KARAOKE CLOUD · GESTÃO DE PRESTADORES · 921204050</p>", unsafe_allow_html=True)

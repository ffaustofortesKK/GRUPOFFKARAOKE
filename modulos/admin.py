import streamlit as st
from modulos.db import obter_prestadores, guardar_prestador

def formatarTempo(segundos: int) -> str:
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    secs = segundos % 60
    if horas > 0:
        return f"{horas}h {minutos}m"
    return f"{minutos}m {secs}s"

def render():
    st.title("FFKaraoke · Administração")
    st.caption("Gestão de acessos e controlos do programa FFK")
    st.divider()

    col_at1, col_at2 = st.columns([3, 7])
    with col_at1:
        if st.button("🎤 Ir para o Registo de Prestador"):
            st.query_params["view"] = "prestador"
            st.rerun()
            
    st.markdown("---")

    if not st.session_state.get("logged", False):
        st.subheader("🔒 Área restrita")
        with st.form("login_form"):
            password_input = st.text_input("Palavra-passe de administrador", type="password")
            submit_login = st.form_submit_button("Entrar")
            
            if submit_login:
                if password_input == "admin":
                    st.session_state.logged = True
                    st.rerun()
                else:
                    st.error("Palavra-passe incorreta.")
    else:
        col_l1, col_l2 = st.columns([8, 2])
        with col_l2:
            if st.button("Terminar sessão"):
                st.session_state.logged = False
                st.rerun()

        # Lê os dados mais recentes do ficheiro a cada ciclo
        prestadores_atuais = obter_prestadores()

        aba1, aba2, aba3 = st.tabs(["1º Pedidos e Aprovação", "2º Gestão Online", "3º Controle de Gestão"])

        with aba1:
            pendentes = [p for p in prestadores_atuais if p.get("status_str", "pendente") == "pendente"]
            st.subheader(f"⏳ Registos pendentes ({len(pendentes)})")
            
            if not pendentes:
                st.info("Nenhum registo à espera de aprovação.")
            else:
                for p in pendentes:
                    with st.container(border=True):
                        st.markdown(f"**{p['nome']}**")
                        st.caption(f"Telefone: {p['telefone']} · Estabelecimento: {p.get('estabelecimento', 'N/A')} · Plano: {p['plano']} · Token: {p['token']}")
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button("✅ Aprovar", key=f"aprov_{p['token']}"):
                                p["approved"] = True
                                p["status_str"] = "aprovado"
                                guardar_prestador(p)
                                if "historico" not in st.session_state:
                                    st.session_state.historico = []
                                st.session_state.historico.append({"acao": "Aprovação", "detalhe": f"Prestador {p['nome']} aprovado.", "data": "Hoje"})
                                st.rerun()
                                
                        with col_b:
                            if st.button("❌ Recusar", key=f"rec_{p['token']}"):
                                p["approved"] = False
                                p["status_str"] = "recusado"
                                guardar_prestador(p)
                                if "historico" not in st.session_state:
                                    st.session_state.historico = []
                                st.session_state.historico.append({"acao": "Recusa", "detalhe": f"Prestador {p['nome']} foi recusado.", "data": "Hoje"})
                                st.rerun()

        with aba2:
            ativos = [p for p in prestadores_atuais if p.get("status_str") == "aprovado"]
            st.subheader(f"🟢 Prestadores Ativos / Online ({len(ativos)})")
            if not ativos:
                st.info("Nenhum prestador ativo no momento.")
            else:
                for p in ativos:
                    with st.container(border=True):
                        tempo_str = formatarTempo(p.get("segundos_restantes", 0))
                        st.markdown(f"**{p['nome']}** — Estabelecimento: {p.get('estabelecimento', 'N/A')} — Plano: {p['plano']}")
                        st.write(f"Tempo restante: **{tempo_str}** | Token: `{p['token']}`")
                        if st.button("Suspender Acesso", key=f"susp_{p['token']}"):
                            p["approved"] = False
                            p["status_str"] = "suspenso"
                            guardar_prestador(p)
                            st.rerun()

        with aba3:
            st.subheader("📊 Histórico e Informações Gerais")
            if "historico" in st.session_state:
                for h in st.session_state.historico:
                    st.markdown(f"- **[{h['data']}] {h['acao']}**: {h['detalhe']}")

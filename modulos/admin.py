import streamlit as st

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

    # Atalho visual rápido no topo para mudar de módulo se necessário
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("👤 Ir para Área de Prestador"):
            st.query_params["view"] = "prestador"
            st.rerun()

    if not st.session_state.logged:
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

        # As 3 Abas do Administrador pedidas
        aba1, aba2, aba3 = st.tabs(["1º Pedidos e Aprovação", "2º Gestão Online", "3º Controle de Gestão"])

        # ABA 1
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
                                st.rerun()

        # ABA 2
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
                        if st.button("Suspender Acesso", key=f"susp_{p['token']}"):
                            p["approved"] = False
                            st.rerun()

        # ABA 3
        with aba3:
            st.subheader("📊 Histórico e Informações Gerais")
            for h in st.session_state.historico:
                st.markdown(f"- **[{h['data']}] {h['acao']}**: {h['detalhe']}")

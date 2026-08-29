import streamlit as st
from modulos.db import obter_prestadores, atualizar_estado_prestador, remover_prestador

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

    # --- BOTÃO DE ATALHO PARA O PRESTADOR ---
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

        # Obtém os dados atualizados diretamente da base de dados JSON
        prestadores_atuais = obter_prestadores()

        # As 3 Abas do Administrador
        aba1, aba2, aba3 = st.tabs(["1º Pedidos e Aprovação", "2º Gestão Online", "3º Controle de Gestão"])

        with aba1:
            pendentes = [p for p in prestadores_atuais if not p.get("approved", False)]
            st.subheader(f"⏳ Registos pendentes ({len(pendentes)})")
            
            if not pendentes:
                st.info("Nenhum registo à espera de aprovação.")
            else:
                for p in pendentes:
                    with st.container(border=True):
                        st.markdown(f"**{p.get('nome')}**")
                        st.caption(f"Telefone: {p.get('telefone')} · Estabelecimento: {p.get('estabelecimento', 'N/A')} · Plano: {p.get('plano')} · Token: `{p.get('token')}`")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✅ Aprovar", key=f"aprov_{p.get('token')}"):
                                atualizar_estado_prestador(p.get('token'), True)
                                st.success(f"Prestador {p.get('nome')} aprovado com sucesso!")
                                st.rerun()
                        with col_b:
                            if st.button("❌ Recusar", key=f"rec_{p.get('token')}"):
                                remover_prestador(p.get('token'))
                                st.warning(f"Pedido de {p.get('nome')} recusado.")
                                st.rerun()

        with aba2:
            ativos = [p for p in prestadores_atuais if p.get("approved", False)]
            st.subheader(f"🟢 Prestadores Ativos / Online ({len(ativos)})")
            if not ativos:
                st.info("Nenhum prestador ativo no momento.")
            else:
                for p in ativos:
                    with st.container(border=True):
                        tempo_restante = p.get("segundos_restantes", 0)
                        tempo_str = formatarTempo(tempo_restante)
                        st.markdown(f"**{p.get('nome')}** — Estabelecimento: {p.get('estabelecimento', 'N/A')} — Plano: {p.get('plano')}")
                        st.write(f"Tempo restante: **{tempo_str}** | Token: `{p.get('token')}`")
                        
                        if st.button("Suspender Acesso", key=f"susp_{p.get('token')}"):
                            atualizar_estado_prestador(p.get('token'), False)
                            st.rerun()

        with aba3:
            st.subheader("📊 Histórico e Informações Gerais")
            st.write(f"Total de registos na base de dados: **{len(prestadores_atuais)}**")
            st.write(f"Total aprovados: **{len([p for p in prestadores_atuais if p.get('approved')])}**")
            st.write(f"Total pendentes: **{len([p for p in prestadores_atuais if not p.get('approved')])}**")

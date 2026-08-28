import streamlit as st
import uuid

def render():
    st.title("🎤 Área do Prestador - FFKaraoke")
    st.write("Inscreva-se ou aceda ao seu painel de controlo de prestador.")
    
    if st.button("⬅️ Voltar para o Administrador"):
        st.query_params["view"] = "admin"
        st.rerun()
        
    st.divider()
    
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
                st.success(f"Registo efetuado com sucesso! O seu token pendente é: **{novo_token}**.")

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
                    st.subheader("🔗 Links Úteis")
                    
                    # Links dinâmicos apontando para os respetivos módulos
                    link_cliente = f"http://localhost:8501/?view=cliente&token={prestador_encontrado['token']}"
                    link_tela = f"http://localhost:8501/?view=tela&token={prestador_encontrado['token']}"
                    
                    st.markdown("**Link para Inscrição de Clientes:**")
                    st.code(link_cliente)
                    
                    st.markdown("**Link da Tela (Apresentação):**")
                    st.code(link_tela)
            else:
                st.error("Token não encontrado.")

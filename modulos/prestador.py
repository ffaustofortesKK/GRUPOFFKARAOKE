import streamlit as st
import uuid
import time

def render():
    st.title("🎤 Área do Prestador - FFKaraoke")
    st.write("Inscreva-se ou aceda ao seu painel de controlo.")
    st.divider()

    # Verifica se já existe um identificador guardado na sessão
    prestador_id = st.session_state.get("prestador_id_sessao", None)

    if prestador_id:
        # Procurar o prestador na base de dados pelo ID/token interno
        prestador = next((p for p in st.session_state.prestadores if p["token"] == prestador_id), None)
        
        if not prestador:
            # Se foi apagado ou recusado pelo admin
            st.session_state.prestador_id_sessao = None
            st.rerun()
        
        if not prestador["approved"]:
            # ESTADO DE ESPERA (LOADING COM CÍRCULO / SPINNER)
            st.markdown("---")
            with st.spinner("⏳ Pedido submetido com sucesso! A aguardar a aprovação do Administrador... Por favor, aguarde."):
                time.sleep(2)
            
            st.warning("⚠️ O seu pedido está a ser analisado pela administração.")
            
            col_bt1, col_bt2 = st.columns([2, 8])
            with col_bt1:
                if st.button("🔄 Atualizar Estado"):
                    st.rerun()
            with col_bt2:
                if st.button("❌ Cancelar / Voltar ao Registo"):
                    # Remove o pedido pendente para permitir novo registo
                    st.session_state.prestadores = [x for x in st.session_state.prestadores if x["token"] != prestador_id]
                    st.session_state.prestador_id_sessao = None
                    st.rerun()
                
        else:
            # APROVADO: Abre o campo de trabalho para o prestador
            st.success(f"🎉 Pedido Aprovado! Bem-vindo ao painel, {prestador['nome']}.")
            st.markdown("---")
            st.subheader("🔗 Os seus Links de Trabalho")
            
            link_cliente = f"http://localhost:8501/?view=cliente&token={prestador['token']}"
            link_tela = f"http://localhost:8501/?view=tela&token={prestador['token']}"
            
            st.markdown("**Link para Inscrição de Clientes:**")
            st.code(link_cliente)
            
            st.markdown("**Link da Tela de Exibição:**")
            st.code(link_tela)
            
            st.markdown("---")
            if st.button("🚪 Terminar Sessão"):
                st.session_state.prestador_id_sessao = None
                st.rerun()
                
    else:
        # APENAS O FORMULÁRIO DE REGISTO (SEM ABAS DE TOKEN)
        st.subheader("📝 Formulário de Inscrição de Prestador")
        
        with st.form("form_registo_prestador"):
            nome_p = st.text_input("Nome Completo")
            tel_p = st.text_input("Telefone")
            estabelecimento_p = st.text_input("Estabelecimento (Local onde vai prestar o serviço)")
            
            contrato_opcoes = {
                "1 Hora - 12 Mil Kwanzas": 3600,
                "2 Horas - 17 Mil Kwanzas": 7200,
                "3 Horas - 20 Mil Kwanzas": 10800
            }
            contrato_escolhido = st.selectbox("Escolha o Contrato", list(contrato_opcoes.keys()))
            
            submit_reg = st.form_submit_button("Submeter Pedido")
            
            if submit_reg:
                if nome_p and tel_p and estabelecimento_p:
                    novo_id = str(uuid.uuid4())[:8]
                    segundos_atribuidos = contrato_opcoes[contrato_escolhido]
                    
                    st.session_state.prestadores.append({
                        "token": novo_id,
                        "nome": nome_p,
                        "telefone": tel_p,
                        "estabelecimento": estabelecimento_p,
                        "plano": contrato_escolhido,
                        "approved": False,
                        "segundos_restantes": segundos_atribuidos
                    })
                    
                    # Guarda a sessão e força o ecrã a entrar no modo de espera (loading)
                    st.session_state.prestador_id_sessao = novo_id
                    st.success("Pedido submetido com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios.")

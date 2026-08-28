import streamlit as st
import uuid
import time

def render():
    st.title("🎤 Área do Prestador - FFKaraoke")
    st.write("Inscreva-se ou aceda ao seu painel de controlo de prestador.")
    st.divider()

    # Verifica se já existe um token guardado na sessão para este prestador
    token_atual = st.session_state.get("prestador_token_sessao", None)

    if token_atual:
        # Procurar o prestador na base de dados
        prestador = next((p for p in st.session_state.prestadores if p["token"] == token_atual), None)
        
        if not prestador:
            # Se foi apagado ou recusado
            st.session_state.prestador_token_sessao = None
            st.rerun()
        
        if not prestador["approved"]:
            # ESTADO DE ESPERA (LOADING)
            st.markdown("---")
            with st.spinner("⏳ Pedido submetido! A aguardar aprovação do Administrador... Por favor, aguarde."):
                time.sleep(2) # Simula atualização em tempo real
            st.info("O seu pedido está pendente de validação pela administração.")
            
            if st.button("🔄 Atualizar Estado"):
                st.rerun()
                
        else:
            # APROVADO: Abre o painel de trabalho
            st.success(f"🎉 Pedido Aprovado! Bem-vindo ao painel, {prestador['nome']}.")
            st.markdown("---")
            st.subheader("🔗 Links Úteis para o seu Karaoke")
            
            link_cliente = f"http://localhost:8501/?view=cliente&token={prestador['token']}"
            link_tela = f"http://localhost:8501/?view=tela&token={prestador['token']}"
            
            st.markdown("**Link para Inscrição de Clientes:**")
            st.code(link_cliente)
            
            st.markdown("**Link da Tela (Apresentação/Fila):**")
            st.code(link_tela)
            
            if st.button("🚪 Terminar Sessão / Sair"):
                st.session_state.prestador_token_sessao = None
                st.rerun()
                
    else:
        # FORMULÁRIO DE REGISTO
        tab_reg, tab_painel = st.tabs(["📝 Novo Registo", "🔑 Já tenho Token"])
        
        with tab_reg:
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
                        novo_token = str(uuid.uuid4())[:8]
                        segundos_atribuidos = contrato_opcoes[contrato_escolhido]
                        
                        st.session_state.prestadores.append({
                            "token": novo_token,
                            "nome": nome_p,
                            "telefone": tel_p,
                            "estabelecimento": estabelecimento_p,
                            "plano": contrato_escolhido,
                            "approved": False,
                            "segundos_restantes": segundos_atribuidos
                        })
                        
                        # Guarda o token na sessão para prender o utilizador na tela de loading
                        st.session_state.prestador_token_sessao = novo_token
                        st.success("Registo submetido com sucesso!")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha todos os campos obrigatórios.")

        with tab_painel:
            token_input = st.text_input("Introduza o seu Token de Acesso")
            if st.button("Aceder ao Painel"):
                prestador_encontrado = next((p for p in st.session_state.prestadores if p["token"] == token_input), None)
                if prestador_encontrado:
                    st.session_state.prestador_token_sessao = prestador_encontrado["token"]
                    st.rerun()
                else:
                    st.error("❌ Token não encontrado ou inválido.")

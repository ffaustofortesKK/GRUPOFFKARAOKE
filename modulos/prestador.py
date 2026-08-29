import streamlit as st
import uuid
from modulos.db import guardar_prestador, obter_prestadores

def render():
    st.markdown("""
        <style>
        .card-container {
            border: 2px solid #eab308;
            border-radius: 12px;
            padding: 40px;
            background-color: #09090b;
            text-align: center;
            color: #fafafa;
            margin-top: 20px;
        }
        .card-container-recusado {
            border: 2px solid #ef4444;
            border-radius: 12px;
            padding: 40px;
            background-color: #09090b;
            text-align: center;
            color: #fafafa;
            margin-top: 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .loader-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 30px 0;
        }
        .dashed-circle {
            width: 100px;
            height: 100px;
            border: 4px dashed #eab308;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            animation: spin 6s linear infinite;
        }
        .mic-icon {
            font-size: 40px;
            animation: spin 6s linear infinite reverse;
        }
        </style>
    """, unsafe_allow_html=True)

    # Lê os dados mais recentes diretamente do ficheiro JSON
    todos_prestadores = obter_prestadores()
    st.session_state.prestadores = todos_prestadores

    prestador_id = st.session_state.get("prestador_id_sessao", None)

    if prestador_id:
        # Encontra o prestador pelo token atual
        prestador = next((p for p in todos_prestadores if str(p["token"]) == str(prestador_id)), None)
        
        if not prestador:
            st.warning("O seu registo já não se encontra ativo no sistema.")
            if st.button("🔄 Voltar ao Início"):
                st.session_state.prestador_id_sessao = None
                st.rerun()
            return

        status = prestador.get("status_str", "pendente")

        if status == "recusado":
            # ECRÃ DE RECUSA
            st.markdown("""
                <div class="card-container-recusado">
                    <h1 style="color: #ef4444; font-size: 28px; margin-bottom: 10px;">Pedido Recusado</h1>
                    <p style="color: #d4d4d8; font-size: 16px; margin-top: 15px;">
                        Lamentamos informar que o seu pedido de registo foi recusado pelo Administrador.
                    </p>
                    <p style="color: #a1a1aa; font-size: 13px; margin-top: 10px;">
                        Pode submeter um novo pedido preenchendo os dados novamente.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            col_r1, col_r2, col_r3 = st.columns([3, 2, 3])
            with col_r2:
                if st.button("🔄 Tentar Novo Registo", use_container_width=True):
                    st.session_state.prestador_id_sessao = None
                    st.rerun()

        elif status == "pendente":
            # ECRÃ DE ESPERA
            st.markdown("""
                <div class="card-container">
                    <h1 style="color: #eab308; font-size: 28px; margin-bottom: 10px;">Cadastramento do Prestador</h1>
                    <p style="color: #a1a1aa; font-size: 14px; margin-bottom: 30px;">
                        Preencha os seus dados, indique o estabelecimento e escolha o tempo pretendido para solicitar o seu acesso.
                    </p>
                    <div class="loader-container">
                        <div class="dashed-circle">
                            <div class="mic-icon">🎤</div>
                        </div>
                    </div>
                    <h3 style="color: #fafafa; font-size: 20px; margin-top: 20px;">Aguardando Aprovação</h3>
                    <p style="color: #d4d4d8; font-size: 14px; margin-top: 10px;">
                        O seu registo foi enviado com sucesso e está a aguardar a validação do Administrador.
                    </p>
                    <p style="color: #71717a; font-size: 13px; margin-top: 5px; margin-bottom: 25px;">
                        Clique no botão abaixo para verificar se já foi aprovado.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            col_v1, col_v2, col_v3 = st.columns([3, 2, 3])
            with col_v2:
                if st.button("🔄 Atualizar Estado", use_container_width=True):
                    st.rerun()
                
        else:
            # ECRÃ DE APROVADO
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
        # FORMULÁRIO DE REGISTO INICIAL
        st.markdown("""
            <div style="text-align: center; margin-bottom: 25px;">
                <h1 style="color: #eab308; font-size: 28px;">Cadastramento do Prestador</h1>
                <p style="color: #a1a1aa; font-size: 14px;">
                    Preencha os seus dados, indique o estabelecimento e escolha o tempo pretendido para solicitar o seu acesso.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
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
                    
                    novo_registo = {
                        "token": novo_id,
                        "nome": nome_p,
                        "telefone": tel_p,
                        "estabelecimento": estabelecimento_p,
                        "plano": contrato_escolhido,
                        "approved": False,
                        "status_str": "pendente",
                        "segundos_restantes": segundos_atribuidos
                    }
                    
                    guardar_prestador(novo_registo)
                    st.session_state.prestador_id_sessao = novo_id
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios.")

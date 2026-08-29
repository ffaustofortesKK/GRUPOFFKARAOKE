import streamlit as st
import time
from datetime import datetime
from modulos.db import guardar_prestador, obter_prestadores

def render():
    # Inicializar estado de submissão se não existir
    if "pedido_submetido" not in st.session_state:
        st.session_state.pedido_submetido = False
        st.session_state.token_prestador = None
        st.session_state.estado_pedido = "pendente"

    # Se já submetido, verifica automaticamente o estado na base de dados (Auto-refresh)
    if st.session_state.pedido_submetido and st.session_state.token_prestador:
        prestadores = obter_prestadores()
        prestador_atual = next((p for p in prestadores if p.get("token") == st.session_state.token_prestador), None)
        
        if prestador_atual:
            status_atual = prestador_atual.get("status_str", "pendente")
            
            # Se foi aprovado pelo administrador
            if status_atual == "aprovado":
                st.session_state.aprovado = True
                st.rerun()
                
            # Se foi recusado pelo administrador, guarda o estado para mostrar o aviso
            elif status_atual == "recusado":
                st.session_state.estado_pedido = "recusado"

    # Se o pedido foi recusado pelo administrador
    if st.session_state.pedido_submetido and st.session_state.estado_pedido == "recusado":
        st.markdown("""
            <div style="background-color: #0f0f11; border: 2px solid #ef4444; padding: 40px 20px; text-align: center; border-radius: 12px; margin-top: 20px;">
                <div style="font-size: 50px; margin-bottom: 15px;">❌</div>
                <h2 style="color: #ef4444; font-weight: bold; margin-bottom: 15px;">Pedido Recusado</h2>
                <p style="color: #d4d4d8; font-size: 16px; max-width: 500px; margin: 0 auto 20px auto;">
                    Infelizmente o seu pedido de acesso foi recusado pelo Administrador.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Tentar Novamente / Novo Registo", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.rerun()

    # Se o pedido continua pendente (aguardando aprovação)
    elif st.session_state.pedido_submetido:
        st.markdown("""
            <style>
                @keyframes girarHorario {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                @keyframes girarAntiHorario {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(-360deg); }
                }
                .circulo-externo {
                    width: 140px;
                    height: 140px;
                    border-radius: 50%;
                    border: 2px dashed #ef4444;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    position: relative;
                    animation: girarHorario 10s linear infinite;
                }
                .circulo-interno {
                    width: 100px;
                    height: 100px;
                    border-radius: 50%;
                    border: 2px dashed #eab308;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    animation: girarAntiHorario 8s linear infinite;
                }
            </style>
            
            <div style="background-color: #0f0f11; padding: 40px 20px; text-align: center; border-radius: 12px; margin-top: 20px;">
                <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 25px;">
                    <div class="circulo-externo">
                        <div class="circulo-interno">
                            <span style="font-size: 42px;">🎤</span>
                        </div>
                    </div>
                </div>
                <h2 style="color: #ffffff; font-weight: bold; margin-bottom: 15px;">Aguardando Aprovação</h2>
                <p style="color: #d4d4d8; font-size: 16px; max-width: 500px; margin: 0 auto 10px auto;">
                    O seu registo foi enviado com sucesso e está a aguardar a validação do Administrador.
                </p>
                <p style="color: #a1a1aa; font-size: 14px;">
                    Assim que for aprovado, esta página atualizar-se-á automaticamente.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Faz o refresh automático a cada 5 segundos para detetar alterações (aprovação ou recusa)
        time.sleep(5)
        st.rerun()
                
    else:
        # Título limpo e formulário de registo
        st.markdown("<h2 style='text-align: center; color: #eab308;'>Cadastramento</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #a1a1aa; margin-bottom: 30px;'>Preencha os dados abaixo para submeter o seu pedido de acesso ao sistema.</p>", unsafe_allow_html=True)

        with st.form("form_registo_prestador"):
            nome = st.text_input("Nome Completo")
            telefone = st.text_input("Telefone")
            estabelecimento = st.text_input("Estabelecimento (Local onde vai prestar o serviço)")
            contrato = st.selectbox("Escolha o Contrato", [
                "1 Hora - 12 Mil Kwanzaas", 
                "3 Horas - 20 Mil Kwanzaas",
                "Personalizado / Noite Completa"
            ])
            
            submitted = st.form_submit_button("Submeter Pedido", use_container_width=True)
            
            if submitted:
                if nome.strip() and telefone.strip():
                    token_gerado = f"token_{int(time.time())}"
                    novo_prestador = {
                        "nome": nome.strip(),
                        "telefone": telefone.strip(),
                        "estabelecimento": estabelecimento.strip(),
                        "plano": contrato,
                        "contrato": contrato,
                        "status_str": "pendente",
                        "approved": False,
                        "token": token_gerado,
                        "segundos_restantes": 3600,
                        "data_pedido": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    
                    # Guarda na base de dados
                    guardar_prestador(novo_prestador)
                    
                    # Atualiza o estado para exibir a tela de espera animada
                    st.session_state.pedido_submetido = True
                    st.session_state.token_prestador = token_gerado
                    st.session_state.estado_pedido = "pendente"
                    st.rerun()
                else:
                    st.error("Por favor, preencha pelo menos o Nome Completo e o Telefone.")

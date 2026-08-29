import streamlit as st
import time
from datetime import datetime
from modulos.db import guardar_prestador, obter_prestadores

# Importe aqui a função do painel completo do prestador (ajuste o nome do módulo se necessário)
# Exemplo: from modulos.painel_prestador import render as render_painel_completo

def render():
    # Inicializar estado de sessão se não existir
    if "pedido_submetido" not in st.session_state:
        st.session_state.pedido_submetido = False
        st.session_state.token_prestador = None
        st.session_state.estado_pedido = "pendente"
    if "aprovado" not in st.session_state:
        st.session_state.aprovado = False

    # Se já submetido, verifica o estado atual na base de dados em cada ciclo
    if st.session_state.pedido_submetido and st.session_state.token_prestador:
        prestadores = obter_prestadores()
        prestador_atual = next((p for p in prestadores if p.get("token") == st.session_state.token_prestador), None)
        
        if prestador_atual:
            status_atual = prestador_atual.get("status_str", "pendente")
            st.session_state.estado_pedido = status_atual
            
            if status_atual == "aprovado":
                st.session_state.aprovado = True

    # SE JÁ ESTIVER APROVADO: Entra logo no perfil/painel completo do prestador
    if st.session_state.get("aprovado", False) or st.session_state.get("estado_pedido") == "aprovado":
        
        # Se tiver o painel completo modularizado, chame-o diretamente aqui:
        # render_painel_completo()
        
        # --- SE O PAINEL COMPLETO ESTIVER DIRETO OU ENQUANTO INTEGRA ---
        st.markdown("""
            <div style="border: 2px solid #eab308; background-color: #0f0f11; padding: 25px; border-radius: 12px;">
                <div style="text-align: right; margin-bottom: 15px;">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://grupoffkaraoke.streamlit.app" width="120" style="border: 2px solid #eab308; border-radius: 6px;">
                </div>
                <h2 style="color: #eab308; text-align: center;">Painel Operacional — FF Karaoke</h2>
                <hr style="border-color: #3f3f46;">
            </div>
        """, unsafe_allow_html=True)
        
        st.success("Acesso validado com sucesso! Bem-vindo ao seu painel de gestão de karaoke.")
        
        # Espaço para os controlos de fila e leitor
        col_f1, col_f2 = st.tabs(["🎵 Fila de Reprodução", "⚙️ Definições do Prestador"])
        with col_f1:
            st.info("O sistema está a escutar novos pedidos de música dos clientes em tempo real.")
            # Aqui renderiza os componentes da fila e leitor conforme a sua imagem 2
        with col_f2:
            if st.button("Terminar Sessão / Sair do Painel", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()
        return

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
                st.session_state.aprovado = False
                st.rerun()

    # Se o pedido continua pendente (aguardando aprovação com animação)
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
                    Esta página abrirá o seu painel automaticamente assim que o Administrador aprovar.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Intervalo de verificação automática a cada 3 segundos
        time.sleep(3)
        st.rerun()
                
    else:
        # Título e formulário com os 3 contratos configurados
        st.markdown("<h2 style='text-align: center; color: #eab308;'>Cadastramento</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #a1a1aa; margin-bottom: 30px;'>Preencha os dados abaixo para submeter o seu pedido de acesso ao sistema.</p>", unsafe_allow_html=True)

        with st.form("form_registo_prestador"):
            nome = st.text_input("Nome Completo")
            telefone = st.text_input("Telemóvel / Telefone")
            estabelecimento = st.text_input("Estabelecimento (Local onde vai prestar o serviço)")
            
            contrato = st.selectbox("Escolha o Contrato", [
                "1 Hora - 12 Mil Kwanzaas", 
                "2 Horas - 17 Mil Kwanzaas",
                "3 Horas - 20 Mil Kwanzaas"
            ])
            
            submitted = st.form_submit_button("Submeter Pedido", use_container_width=True)
            
            if submitted:
                if nome.strip() and telefone.strip():
                    token_gerado = f"token_{int(time.time())}"
                    
                    if "1 Hora" in contrato:
                        segundos_contrato = 3600
                    elif "2 Horas" in contrato:
                        segundos_contrato = 7200
                    else:
                        segundos_contrato = 10800

                    novo_prestador = {
                        "nome": nome.strip(),
                        "telefone": telefone.strip(),
                        "estabelecimento": estabelecimento.strip(),
                        "plano": contrato,
                        "contrato": contrato,
                        "status_str": "pendente",
                        "approved": False,
                        "token": token_gerado,
                        "segundos_restantes": segundos_contrato,
                        "data_pedido": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    
                    guardar_prestador(novo_prestador)
                    
                    st.session_state.pedido_submetido = True
                    st.session_state.token_prestador = token_gerado
                    st.session_state.estado_pedido = "pendente"
                    st.session_state.aprovado = False
                    st.rerun()
                else:
                    st.error("Por favor, preencha pelo menos o Nome Completo e o Telefone.")

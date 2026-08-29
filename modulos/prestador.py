import streamlit as st
import time
from datetime import datetime
from modulos.db import guardar_prestador

def render():
    # Inicializar estado de submissão se não existir
    if "pedido_submetido" not in st.session_state:
        st.session_state.pedido_submetido = False

    # Se o pedido já foi submetido, mostra o aviso de agendamento/aprovação limpo (sem a palavra "Prestador")
    if st.session_state.pedido_submetido:
        st.markdown("""
            <div style="background-color: #09090b; border: 2px solid #eab308; border-radius: 10px; padding: 30px; text-align: center; margin-bottom: 20px;">
                <h3 style="color: #eab308; margin-bottom: 10px;">Cadastramento</h3>
                <p style="color: #d4d4d8; font-size: 16px;">O seu pedido foi enviado com sucesso. Aguarde enquanto o Administrador valida o seu acesso.</p>
                <div style="font-size: 40px; margin: 20px 0;">🎙️</div>
                <p style="color: #facc15; font-weight: bold; font-size: 18px;">Aguardando Aprovação...</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_bt1, col_bt2, col_bt3 = st.columns([1, 2, 1])
        with col_bt2:
            if st.button("Submeter Novo Pedido", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.rerun()
                
    else:
        # Título limpo sem a palavra "Prestador"
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
                        "segundos_restantes": 3600, # Valor padrão inicial
                        "data_pedido": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    
                    # Guarda na base de dados
                    guardar_prestador(novo_prestador)
                    
                    # Atualiza o estado para alternar a vista
                    st.session_state.pedido_submetido = True
                    st.rerun()
                else:
                    st.error("Por favor, preencha pelo menos o Nome Completo e o Telefone.")

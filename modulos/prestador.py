import streamlit as st
from datetime import datetime
from modulos.db import obter_prestadores, guardar_prestador

def render():
    st.markdown("""
        <style>
        .main-header { font-size: 28px; font-weight: bold; color: #facc15; text-align: center; margin-bottom: 10px; }
        .sub-text { font-size: 15px; color: #d4d4d8; text-align: center; margin-bottom: 25px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">Portal do Prestador — FF Karaoke</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-text">Registe os seus dados para solicitar o acesso à prestação de serviços.</div>', unsafe_allow_html=True)

    # Verifica se já existe um token guardado na sessão deste navegador
    token_atual = st.session_state.get("prestador_token", None)
    
    prestador_registado = None
    if token_atual:
        prestadores = obter_prestadores()
        for p in prestadores:
            if p.get("token") == token_atual:
                prestador_registado = p
                break

    # Se já submeteu, verificamos o estado real na base de dados
    if prestador_registado:
        status = prestador_registado.get("status_str", "pendente")
        
        if status == "pendente":
            st.markdown("""
                <div style="background-color: #18181b; border: 2px solid #eab308; border-radius: 12px; padding: 30px; text-align: center; margin-top: 20px;">
                    <h3 style="color: #facc15; margin-bottom: 10px;">Cadastramento do Prestador</h3>
                    <p style="color: #d4d4d8; font-size: 16px;">O seu pedido foi enviado com sucesso. Aguarde enquanto o Administrador valida o seu acesso.</p>
                    <div style="font-size: 40px; margin: 20px 0;">⏳</div>
                    <p style="color: #eab308; font-weight: bold; font-size: 18px;">Aguardando Aprovação...</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Atualizar Estado"):
                st.rerun()
            return
            
        elif status == "aprovado":
            st.success("🎉 O seu pedido foi APROVADO pelo Administrador! O acesso ao sistema está liberado.")
            # Aqui pode limpar o token se quiser permitir novo registo ou avançar para a ferramenta
            if st.button("Entrar no Sistema"):
                st.session_state["acesso_liberado"] = True
                st.rerun()
            return
            
        elif status == "recusado":
            st.error("❌ O seu pedido foi recusado pelo Administrador.")
            if st.button("Fazer novo registo"):
                st.session_state.pop("prestador_token", None)
                st.rerun()
            return

    # Formulário de Registo caso não tenha submetido ou tenha reiniciado
    with st.form("form_registo_prestador"):
        nome = st.text_input("Nome Completo")
        telefone = st.text_input("Telefone")
        estabelecimento = st.text_input("Estabelecimento (Local onde vai prestar o serviço)")
        contrato = st.selectbox("Escolha o Contrato", ["1 Hora - 12 Mil Kwanzaas", "3 Horas - 20 Mil Kwanzaas", "Personalizado"])
        
        submeter = st.form_submit_button("Submeter Pedido")
        
        if submeter:
            if not nome or not telefone:
                st.error("Por favor, preencha o nome e o telefone.")
            else:
                import random
                token_novo = f"tok_{random.randint(1000, 9999)}"
                
                novo_registo = {
                    "nome": nome,
                    "telefone": telefone,
                    "estabelecimento": estabelecimento,
                    "plano": contrato,
                    "contrato": contrato,
                    "reforco": "N/A",
                    "token": token_novo,
                    "approved": False,
                    "status_str": "pendente",
                    "data_pedido": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "segundos_restantes": 3600 if "1 Hora" in contrato else 10800
                }
                
                guardar_prestador(novo_registo)
                st.session_state["prestador_token"] = token_novo
                st.success("Pedido submetido com sucesso!")
                st.rerun()

import streamlit as st
import uuid
from modulos.db import guardar_prestador, obter_prestadores

def render():
    # ... (mantenha todo o seu CSS igual até ao formulário) ...
    # No bloco do submissão do formulário do prestador:

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
                "segundos_restantes": segundos_atribuidos
            }
            
            # Guarda na base de dados persistente
            guardar_prestador(novo_registo)
            
            # Atualiza também a sessão local e define o ID ativo
            st.session_state.prestadores = obter_prestadores()
            st.session_state.prestador_id_sessao = novo_id
            st.rerun()
        else:
            st.error("Por favor, preencha todos os campos obrigatórios.")

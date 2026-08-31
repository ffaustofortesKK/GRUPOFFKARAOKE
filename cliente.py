import streamlit as st
from db import guardar_pedido_musica  # Vamos usar a função centralizada do seu db.py

def render():
    query_params = st.query_params
    token_prestador = query_params.get("token", "Nenhum")
    
    st.title("🎵 FFKaraoke · Inscrição do Cliente")
    st.info(f"Sessão vinculada ao Prestador Token: `{token_prestador}`")
    
    with st.form("form_cliente"):
        cantor = st.text_input("O seu Nome")
        musica = st.text_input("Nome da Música / Artista")
        
        submitted = st.form_submit_button("Pedir Música")
        
        if submitted:
            if cantor.strip() and musica.strip():
                # Chamar a função para guardar no Firebase associado ao token do prestador
                try:
                    guardar_pedido_musica({
                        "cantor": cantor.strip(),
                        "musica": musica.strip(),
                        "token_prestador": token_prestador,
                        "status": "pendente"
                    })
                    st.success(f"Obrigado {cantor}! A sua música '{musica}' foi adicionada à fila.")
                except Exception as e:
                    st.error(f"Erro ao enviar o pedido: {e}")
            else:
                st.error("Por favor preencha todos os campos.")

import streamlit as st

def render():
    query_params = st.query_params
    token_prestador = query_params.get("token", "Nenhum")
    
    st.title("🎵 FFKaraoke · Inscrição do Cliente")
    st.info(f"Sessão vinculada ao Prestador Token: `{token_prestador}`")
    
    with st.form("form_cliente"):
        cantor = st.text_input("O seu Nome")
        musica = st.text_input("Nome da Música / Artista")
        if st.form_submit_button("Pedir Música"):
            if cantor and musica:
                st.success(f"Obrigado {cantor}! A sua música '{musica}' foi adicionada à fila.")
            else:
                st.error("Por favor preencha todos os campos.")

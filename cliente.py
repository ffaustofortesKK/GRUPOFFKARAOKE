import streamlit as st
from db import guardar_pedido_musica

def render():
    query_params = st.query_params
    token_prestador = query_params.get("token", "Nenhum")
    
    # 1. Inicializa o estado do nome do cliente se não existir
    if "cliente_nome" not in st.session_state:
        st.session_state["cliente_nome"] = ""

    # ESTADO 1: Se o cliente ainda não inseriu o nome (Aparece a 1ª imagem)
    if not st.session_state["cliente_nome"]:
        st.markdown("### 🎤 Bem-vindo ao FF Karaoke")
        st.write("Insira o seu nome ou alcunha para começar:")
        
        with st.form(key="form_login_cliente"):
            cantor_input = st.text_input("O seu Nome / alcunha:", placeholder="Ex: João da Silva")
            submit_nome = st.form_submit_button("Entrar")
            
            if submit_nome:
                if cantor_input.strip():
                    st.session_state["cliente_nome"] = cantor_input.strip()
                    st.rerun()
                else:
                    st.error("Por favor, insira um nome ou alcunha válido.")
                    
    # ESTADO 2: Se o cliente já inseriu o nome (Aparece a 2ª imagem adaptada com o formulário de pedido)
    else:
        cantor = st.session_state["cliente_nome"]
        
        # Mensagem de Boas-Vindas personalizada e indicação de sessão
        st.markdown(f"### Benvindo {cantor}")
        st.success("✅ Já poderá enviar o seu pedido!")
        
        st.info(f"Sessão vinculada ao Prestador Token: `{token_prestador}`")
        
        # Formulário para o pedido da música
        with st.form("form_cliente", clear_on_submit=True):
            st.markdown("### 🔍 Pesquisar / Pedir Música")
            musica = st.text_input("Digite o nome da música ou artista:", placeholder="Ex: Landrick, Nani...")
            
            submitted = st.form_submit_button("Pedir Música")
            
            if submitted:
                if musica.strip():
                    try:
                        # Envia os dados para a base de dados unificada
                        guardar_pedido_musica({
                            "cantor": cantor,
                            "musica": musica.strip(),
                            "token_prestador": token_prestador,
                            "status": "pendente"
                        })
                        st.success(f"Obrigado {cantor}! A sua música '{musica}' foi adicionada à fila.")
                    except Exception as e:
                        st.error(f"Erro detalhado ao enviar o pedido: {e}")
                else:
                    st.error("Por favor, preencha o nome da música ou artista.")
        
        # Botão discreto caso o cliente queira sair ou alterar o nome inserido
        if st.button("🔄 Alterar Nome"):
            st.session_state["cliente_nome"] = ""
            st.rerun()

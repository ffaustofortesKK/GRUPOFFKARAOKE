import json
import os
import streamlit as st

# Inicialização segura do Firebase com exibição visual de erros
FIREBASE_ATIVO = False
try:
    import firebase_admin
    from firebase_admin import credentials, db
    
    if not firebase_admin._apps:
        # Verifica se o secret existe para dar uma mensagem clara caso falte
        if "firebase" not in st.secrets:
            raise Exception("A secção [firebase] não foi encontrada no ficheiro st.secrets ou nas configurações da nuvem.")
            
        firebase_secrets = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secrets)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://grupoffkaraoke-default-rtdb.firebaseio.com'
        })
    FIREBASE_ATIVO = True
except Exception as e:
    # Mostra o erro exato no ecrã para sabermos se o problema é a chave, o formato ou os secrets
    st.error(f"❌ ERRO CRÍTICO NO FIREBASE: {e}")
    FIREBASE_ATIVO = False

FICHEIRO_DB = "prestadores.json"
# ... (restante do código mantém-se igual)

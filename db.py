import json
import os
import streamlit as st

# Inicialização segura do Firebase com correção automática da chave privada
FIREBASE_ATIVO = False
try:
    import firebase_admin
    from firebase_admin import credentials, db
    
    if not firebase_admin._apps:
        if "firebase" not in st.secrets:
            raise Exception("A secção [firebase] não foi encontrada nos st.secrets.")
            
        # Converte os secrets num dicionário modificável
        firebase_secrets = dict(st.secrets["firebase"])
        
        # Garante que as quebras de linha da private_key são interpretadas corretamente
        if "private_key" in firebase_secrets:
            firebase_secrets["private_key"] = firebase_secrets["private_key"].replace("\\n", "\n")
            
        cred = credentials.Certificate(firebase_secrets)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://grupoffkaraoke-default-rtdb.firebaseio.com'
        })
    FIREBASE_ATIVO = True
except Exception as e:
    st.error(f"❌ ERRO CRÍTICO NO FIREBASE: {e}")
    FIREBASE_ATIVO = False

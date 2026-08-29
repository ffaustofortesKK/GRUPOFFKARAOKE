import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import json

def _inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # Verifica se os segredos estão configurados no painel do Streamlit Cloud
            if "firebase" in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                cred = credentials.Certificate(cred_dict)
            else:
                # Fallback para ambiente local se tiver o ficheiro json na máquina
                cred = credentials.Certificate("serviceAccountKey.json")

            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://grupoffkaraoke-default-rtdb.firebaseio.com/'
            })
        except Exception as e:
            st.error(f"Erro ao inicializar o Firebase. Detalhe: {e}")

def obter_prestadores():
    _inicializar_firebase()
    try:
        ref = db.reference('prestadores')
        data = ref.get()
        if data:
            return list(data.values())
    except Exception:
        pass
    return []

def guardar_prestador(prestador_dict):
    _inicializar_firebase()
    try:
        ref = db.reference('prestadores')
        ref.child(str(prestador_dict['token'])).set(prestador_dict)
    except Exception as e:
        st.error(f"Erro ao guardar no Firebase: {e}")

def atualizar_estado_prestador(token, approved):
    _inicializar_firebase()
    try:
        ref = db.reference(f'prestadores/{token}')
        ref.update({'approved': approved})
    except Exception as e:
        st.error(f"Erro ao atualizar no Firebase: {e}")

def remover_prestador(token):
    _inicializar_firebase()
    try:
        ref = db.reference(f'prestadores/{token}')
        ref.delete()
    except Exception as e:
        st.error(f"Erro ao remover do Firebase: {e}")

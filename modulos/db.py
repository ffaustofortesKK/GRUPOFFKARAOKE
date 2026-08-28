import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import base64
import json
import os

def _inicializar_firebase():
    if not firebase_admin._apps:
        try:
            if "firebase" in st.secrets and "b64_json" in st.secrets["firebase"]:
                # Descodifica a string Base64 diretamente para um dicionário JSON válido
                b64_str = st.secrets["firebase"]["b64_json"]
                json_bytes = base64.b64decode(b64_str)
                cred_dict = json.loads(json_bytes.decode('utf-8'))
                cred = credentials.Certificate(cred_dict)
            else:
                json_path = "serviceAccountKey.json"
                if not os.path.exists(json_path):
                    json_path = os.path.join(os.getcwd(), "serviceAccountKey.json")
                cred = credentials.Certificate(json_path)

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

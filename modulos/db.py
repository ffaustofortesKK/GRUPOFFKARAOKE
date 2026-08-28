import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import json
import os

def _inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # Opção 1: Ler dos Segredos do Streamlit (Ideal para nuvem)
            if "firebase" in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                cred = credentials.Certificate(cred_dict)
            else:
                # Opção 2: Ler do ficheiro local (Ideal para testes locais)
                json_path = "serviceAccountKey.json"
                if not os.path.exists(json_path):
                    json_path = os.path.join(os.getcwd(), "serviceAccountKey.json")
                cred = credentials.Certificate(json_path)

            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://grupoffkaraoke-default-rtdb.firebaseio.com/'
            })
        except Exception as e:
            st.error(f"Erro ao inicializar o Firebase. Configure os Segredos no Streamlit Cloud ou adicione o ficheiro 'serviceAccountKey.json'. Detalhe: {e}")

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

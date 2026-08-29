import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import os
import json

def _inicializar_firebase():
    if not firebase_admin._apps:
        try:
            json_path = "serviceAccountKey.json"
            if not os.path.exists(json_path):
                json_path = os.path.join(os.getcwd(), "serviceAccountKey.json")
                
            # Lê o JSON manualmente e corrige as quebras de linha da chave privada
            with open(json_path, "r", encoding="utf-8") as f:
                cred_dict = json.load(f)
            
            if "private_key" in cred_dict:
                # Garante que as quebras de linha literais "\n" são interpretadas corretamente
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")

            cred = credentials.Certificate(cred_dict)

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

import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

# Inicializa a ligação ao Firebase (evita inicializar duplicado)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://grupoffkaraoke-default-rtdb.firebaseio.com/'
        })
    except Exception as e:
        st.error(f"Erro ao ligar ao Firebase: {e}")

def obter_prestadores():
    ref = db.reference('prestadores')
    data = ref.get()
    if data:
        # Converte o dicionário do Firebase numa lista de dicionários
        return list(data.values())
    return []

def guardar_prestador(prestador_dict):
    ref = db.reference('prestadores')
    # Usa o token como chave única no Firebase
    ref.child(prestador_dict['token']).set(prestador_dict)

def atualizar_estado_prestador(token, approved):
    ref = db.reference(f'prestadores/{token}')
    ref.update({'approved': approved})

def remover_prestador(token):
    ref = db.reference(f'prestadores/{token}')
    ref.delete()

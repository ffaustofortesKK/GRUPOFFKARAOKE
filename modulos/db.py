import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

def _inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # Lê os valores individuais configurados no painel do Streamlit Secrets
            sec = st.secrets["Firebase"]
            
            # Reconstrói a chave privada garantindo que as quebras de linha "\n" funcionam perfeitamente
            private_key_raw = sec["private_key"]
            if "\\n" in private_key_raw:
                private_key_formatted = private_key_raw.replace("\\n", "\n")
            else:
                private_key_formatted = private_key_raw

            cred_dict = {
                "type": sec["type"],
                "project_id": sec["project_id"],
                "private_key_id": sec["private_key_id"],
                "private_key": private_key_formatted,
                "client_email": sec["client_email"],
                "client_id": sec["client_id"],
                "auth_uri": sec["auth_uri"],
                "token_uri": sec["token_uri"],
                "auth_provider_x509_cert_url": sec["auth_provider_x509_cert_url"],
                "client_x509_cert_url": sec["client_x509_cert_url"],
                "universe_domain": sec.get("universe_domain", "googleapis.com")
            }

            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': sec["databaseURL"]
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

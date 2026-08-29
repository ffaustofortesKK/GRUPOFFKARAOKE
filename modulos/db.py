import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

def _inicializar_firebase():
    if not firebase_admin._apps:
        try:
            sec = st.secrets["Firebase"]
            pk = sec["private_key"]
            
            # Limpa e formata corretamente a chave privada independentemente de como foi colada
            pk = pk.strip().strip('"').strip("'")
            if "\\n" in pk:
                pk = pk.replace("\\n", "\n")
            
            # Garante os headers do PEM caso tenham sido omitidos
            if not pk.startswith("-----BEGIN PRIVATE KEY-----"):
                pk = "-----BEGIN PRIVATE KEY-----\n" + pk
            if not pk.endswith("-----END PRIVATE KEY-----"):
                pk = pk + "\n-----END PRIVATE KEY-----"

            cred_dict = {
                "type": sec.get("type", "service_account"),
                "project_id": sec["project_id"],
                "private_key_id": sec["private_key_id"],
                "private_key": pk,
                "client_email": sec["client_email"],
                "client_id": sec["client_id"],
                "auth_uri": sec["auth_uri"],
                "token_uri": sec["token_uri"],
                "auth_provider_x509_cert_url": sec["auth_provider_x509_cert_url"],
                "client_x509_cert_url": sec["client_x509_cert_url"],
            }

            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': sec["databaseURL"]
            })
        except Exception as e:
            # Caso ocorra erro, exibe um aviso amigável para não quebrar a aplicação inteira
            st.warning(f"Modo Offline / Erro de Ligação: A funcionar temporariamente sem persistência remota. ({e})")

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
        st.error(f"Erro ao guardar dados: {e}")

def atualizar_estado_prestador(token, approved):
    _inicializar_firebase()
    try:
        ref = db.reference(f'prestadores/{token}')
        ref.update({'approved': approved})
    except Exception as e:
        st.error(f"Erro ao atualizar dados: {e}")

def remover_prestador(token):
    _inicializar_firebase()
    try:
        ref = db.reference(f'prestadores/{token}')
        ref.delete()
    except Exception as e:
        st.error(f"Erro ao remover dados: {e}")

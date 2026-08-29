import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

def _inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # Lista de linhas exatas da chave privada PEM original
            pem_lines = [
                "-----BEGIN PRIVATE KEY-----",
                "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCosuUNYyTituxRTMm6",
                "GV4atraNdqt153LQyAsyTD7+9HYr7e7rzO8wxkIycw+8RHzAv4k+qNMf1IISEG7ABHYJ",
                "HGGMsYATYIMoBBn50T0QPNMxY+FK1u88xX0VhfzT9997rELCO26/PxKqNVHBOqLZlz9Q",
                "215wsCRH41KVBR3TacBqw8H/zpzwp00f834GTgYG6dEyaUsaBPZIa4RmyA/eMk0ck7M",
                "HYzTaVyX9f9KZ9gt1SeDOj/Qe6YvwALj25DcoGleqfJevxcNUgk4in7/WnW1komeKawG",
                "TFxsDhbPSeV6V/gw3ZrmGN211OcqvkGpaL95J5eoAHUpovE5QFmHFAgMBAAECgf9ueLfz",
                "+gsbR2VU/JiLM1qjbN6Me6mn541avaUppla/DFcxtmc/AwcNRRCCHY35hN/j60CZbGKL",
                "9Ys322Zh6kDPSNjhyVrew0KN349sP4bPm05oiX+juYo6CtBeo00kXUAOYWR6zSeB8QKj",
                "c5BM5uIrds3Iyd7XfsqMkhmUfI5m9LcWLT9TLmziJNKSZbq1o9sauf+lU+RELdjA0bJK",
                "LDUQ8L8XPG0XTkHjZa7OvQBkFeirYqpYJQS0OXEksAUmTdE6c1VInf9GLsYRJbQ7ZrKH",
                "nRlDZqBjU88v46kWNIcyNAWXpJB9pS9Ng7mmCdK1+be8v8ylOOxQTn9C6S4bfk8CgYEA",
                "0BJVyl/Yj+EgH8Ec5YTrvam3B2+f7tEc8BLMdAjn1xBWbkGCR9+SiW1yiDf4CprWV/Dc",
                "WucND4HvUxNRwDvA2LlwtF5LbbhliOSzsHzZcWAE+rNBYJd8ZuYiw+H0ztaY6t3X9kBh",
                "xK/EuXuGXCnB6NYJsMazs62RLbJZXR3Rio8CgYEAz47OGRvC8uSOR6fNFR/aDoIMkEFA",
                "hc7aG7EPRTYLh4ThSICP65VMz49zuUXsbBEY6sGbJoyBW4S4Hh9ZUOT26qdowNOhaPWu",
                "6FujxYkJRwrmPabojtoiHRuUsiL4jxL5iKWSmDcNvdV9PZj8HoRefEhtIT0i8jRPUZ6H",
                "yjqDCGsCgYAu0rFzpTX6ytKL0s1J6SuTtsl1Zu06tNwqOlDAG/DwOMD6dst2mR1Ex9h",
                "qRw4OdOGfUJiF7FDIGJlevI49EDVJkBGIxV98BW7z62N0Z+QW22DDeetQbUaVncVyJcC",
                "PDGA+5asrao4pc1KEUjHOj8dGtL91mZpCx8nElM2lgxwEMiQKBgQClu+cwP220m/JMn1",
                "3wL0Xkbc3wZlpKPnkEwaZq4pPkO6PUS+wf9lCmMGr8lywIwsI9uijUaD9mv5xxWSDtql",
                "bL2q+XwaVSdVOb8IjeU+VXmAlvU1bBssaorXxXnfsR69nbVjKvXs6XNeDSjdVL3PDBlu",
                "elMfc0pbZsewT84yn8TwKBgQCZIZ0T00FxMQwTRPGZ3AKJneZz3Qq/1rUTdKlWV3WdwU",
                "729ExhR6xIMG2Q6fIrt+1OIIt8XgQdONh30CHfmSut/wwJYWYEMIP29bt1763U63F050",
                "hTzrweHHAFH3eo8mEat/pg11A64fZWsngIaa7aAwXLwZsvz3EQmPD6ZK4jWlg==",
                "-----END PRIVATE KEY-----"
            ]
            
            # Junta as linhas com quebras de linha reais do sistema
            private_key_formatted = "\n".join(pem_lines) + "\n"

            cred_dict = {
                "type": "service_account",
                "project_id": "grupoffkaraoke",
                "private_key_id": "fd6401fac635c511b593671f109f4fdc079042c7",
                "private_key": private_key_formatted,
                "client_email": "firebase-adminsdk-fbsvc@grupoffkaraoke.iam.gserviceaccount.com",
                "client_id": "117175888254174092695",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40grupoffkaraoke.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }

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

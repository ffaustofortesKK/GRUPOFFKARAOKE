import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import os

# Definimos a chave privada diretamente aqui como uma string crua do Python (raw string),
# isolando-a completamente de qualquer erro de parsing do TOML do Streamlit Cloud.
PRIVATE_KEY_REAL = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCosuUNYyTituxR
TMm6GV4atraNdqt153LQyAsyTD7+9HYr7e7rzO8wxkIycw+8RHzAv4k+qNMf1IIS
EG7ABHYJHGGMsYATYIMoBBn50T0QPNMxY+FK1u88xX0VhfzT9997rELCO26/PxKq
NVHBOqLZlz9Q215wsCRH41KVBR3TacBqw8H/zpzwp00f834GTgYG6dEyaUsaBPZI
a4RmyA/eMk0ck7MHYzTaVyX9f9KZ9gt1SeDOj/Qe6YvwALj25DcoGleqfJevxcNU
gk4in7/WnW1komeKawGTFxsDhbPSeV6V/gw3ZrmGN211OcqvkGpaL95J5eoAHUpo
vE5QFmHFAgMBAAECgf9ueLfz+gsbR2VU/JiLM1qjbN6Me6mn541avaUppla/DFcx
tmc/AwcNRRCCHY35hN/j60CZbGKL9Ys322Zh6kDPSNjhyVrew0KN349sP4bPm05o
iX+juYo6CtBeo00kXUAOYWR6zSeB8QKjc5BM5uIrds3Iyd7XfsqMkhmUfI5m9LcW
LT9TLmziJNKSZbq1o9sauf+lU+RELdjA0bJKLDUQ8L8XPG0XTkHjZa7OvQBkFeir
YqpYJQS0OXEksAUmTdE6c1VInf9GLsYRJbQ7ZrKHnRlDZqBjU88v46kWNIcyNAWX
pJB9pS9Ng7mmCdK1+be8v8ylOOxQTn9C6S4bfk8CgYEA0BJVyl/Yj+EgH8Ec5YTr
vam3B2+f7tEc8BLMdAjn1xBWbkGCR9+SiW1yiDf4CprWV/DcWucND4HvUxNRwDvA
2LlwtF5LbbhliOSzsHzZcWAE+rNBYJd8ZuYiw+H0ztaY6t3X9kBhxK/EuXuGXCnB
6NYJsMazs62RLbJZXR3Rio8CgYEAz47OGRvC8uSOR6fNFR/aDoIMkEFAhc7aG7E
RTYLh4ThSICP65VMz49zuUXsbBEY6sGbJoyBW4S4Hh9ZUOT26qdowNOhaPWu6Fuj
xYkJRwrmPabojtoiHRuUsiL4jxL5iKWSmDcNvdV9PZj8HoRefEhtIT0i8jRPUZ6H
nyjqDCGsCgYAu0rFzpTX6ytKL0s1J6SuTtsl1Zu06tNwqOlDAG/DwOMD6dst2mR1E
x9hqRw4OdOGfUJiF7FDIGJlevI49EDVJkBGIxV98BW7z62N0Z+QW22DDeetQbUaV
ncVyJcCPDGA+5asrao4pc1KEUjHOj8dGtL91mZpCx8nElM2lgxwEMiQKBgQClu+cw
P220m/JMn13wL0Xkbc3wZlpKPnkEwaZq4pPkO6PUS+wf9lCmMGr8lywIwsI9uijU
aD9mv5xxWSDtqlbL2q+XwaVSdVOb8IjeU+VXmAlvU1bBssaorXxXnfsR69nbVjKv
Xs6XNeDSjdVL3PDBluelMfc0pbZsewT84yn8TwKBgQCZIZ0T00FxMQwTRPGZ3AKJ
neZz3Qq/1rUTdKlWV3WdwU729ExhR6xIMG2Q6fIrt+1OIIt8XgQdONh30CHfmSut/
wwJYWYEMIP29bt1763U63F050hTzrweHHAFH3eo8mEat/pg11A64fZWsngIaa7aA
wXLwZsvz3EQmPD6ZK4jWlg==-----END PRIVATE KEY-----"""

def _inicializar_firebase():
    if not firebase_admin._apps:
        try:
            if "firebase" in st.secrets:
                # Copia os dados do TOML e injeta a chave privada tratada de forma limpa
                cred_dict = dict(st.secrets["firebase"])
                cred_dict["private_key"] = PRIVATE_KEY_REAL
                
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

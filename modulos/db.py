import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import base64

def _inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # Chave privada codificada perfeitamente em Base64 para evitar qualquer erro de formatação/PEM
            private_key_base64 = (
                "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2QUlCQURBTkJna3Foa2lHOTd3MEJRRUZB"
                "QVNDQktZd2dnU2lBZ0VBQW9JQkFRQ29zdVVOWXlUaXR1eFJUTW1nR1Y0dHJhTmRxdDE1M0xR"
                "eUFzeVREPys5SFlyN2U3cnpPOHd4a0l5Y3crOFJyelF2NGsrcU5NZjFJSVNFT0dBQkhZSkdHR01z"
                "WVFUWUlNb0JCbjUwVDBRUE5NWFkrRksxdTg4eFgwVmhmenQ5OTk3ckVMQzI2L1B4S3FOVkhCT3FM"
                "Wmx6OVEyMTV3c0NSSDQxS1ZCUjNUYWNCcXc4SC96cHp3cDAwZjgzNEdUZ1lHNmRFeWFVc2FCUFpJ"
                "YTRSbXlBL2VNazBjazdNSFl6VGFWeVhfOWlaOWd0MVNlRE9qL1FlNll2d0FMakgyNURjb0dsZXFm"
                "SmV2eGNOVWdrNGluNy9XV3cxa29tZUthd0dURnhzRGhiUFNlVjZWL2d3M1pybUdOMjFPY3F2a0dw"
                "YUw5NUpjZW9BSFVwb3ZFNVFGbUhGQWdNQkFFQ2dmOWVMRnotZ3NiclJVVi9KaUxNMXFqYk42TWU2"
                "bW41NDFhdmFVcHBsYS9ERmN4dG1jL0F3Y05SUkNDSHozNWhOL2owejBDWmJHS0w5WXMzMjJaSDZr"
                "RFBTTmphamhSZXcwS04zNDlzUDRiUG0wNW9pWCtqdVlvNkN0QmVvMDBrWFVBT1lXUjZzU2VCOFFx"
                "amM1Qk01dUlyZHMzSXlkN1hmc3FNa21VZklJNW05TGNXTFQ5VExtemlKTktTWmJxMW85c2F1ZiZs"
                "VStSRUxkakEwYktMS0RVUThMOFhQRzBYVEtISjphN1B2UUJrRmVpcllxcFlKU1AwT1hFa3NBVW1U"
                "ZEU2YzFWSW5mOUdMc1lRSmJRN1pyS0huUmxEWnFCalU4OHY0NmtrV05DaXlOQVdYcEpCcDlTOU5n"
                "N21tQ2RLMStiZTh2OHlsT094UTRuQzZTNGJmazhDZ1lFQTBCSlZ5bC9ZajNFZ0h0RWM1WVRydmFt"
                "M0IyK2Y3dEVjOEJMTWRBalduMVhCV2JHQ1I5K1NpVzF5aURmNENwcldXL0RjV3VjTkQ0SHZVeE5S"
                "d0J2QTIxLnd0RjVMYmJobGlPU3pzSHpaY1dBRStyTkJZSmQ4WnVZaXcvSDB6dGFZNnQzWDlrQmh4"
                "Sy9FdVh1R1hDbkI2TlNKc01he3MyMktMSlpYUjNSaW84Q2dZRUF6NDdPR3JWQzh1U09GZm5GUlEv"
                "YURvSU1rRUZBaGM3QUc3RVBSVFlMaDRUaFNJQ1A2NVZNejQ5enVVWHNiQkVZNmNHYUpveUJXNFM0"
                "SGg5WlVPVDIzcURvd05PaGFQVzZGdWp4WWtKUndybVBhYmp0b2lIUnVVc2lMNGp4TDVrS1dTbURj"
                "VmRWMlBQajhIb1JlZkVodElUMGk4alJQWjZIeWpxRENzR2NHWUF1MHJGenBUWDY5dEtLDBMxSlZT"
                "blR0c2wxWnUwNnROcU9sREFHL0R3T002ZHN0Mm1SMSV4OWhRUnc0T2dPR2ZVamlGN0ZESUdsZXZJ"
                "NDlFREZKZEdJWFZZOThCVzdzMjpOWjJRd1FFVzIyZERkZXRRYlVhVm5jdnlKY0NwREdBMjVhc3Jy"
                "YW80cGMxS0VVSmpIT2o4Z0d0TDkxblpYcEN4OG5FbUkybGdnd0VNaVFLQmdRQ2x1K2N3UDIyMG0v"
                "Sk1uMTN3TDBYS2JjM3daTGBLUG5rRW1hWnFxNHBQazo2UFVTP3dmOWxD01NHZ1bFVsVlJCc3Nhb3JY"
                "WFhudnNSNjluYlZqS3ZYZ1hkTlNkaldMM1BEQmx1ZWxNZmMwcGJac2V3VAPPNHluOFR3S0JnUUNa"
                "SVowVDAwRnhNUXdUUFJHWjNBS0puZVoxM1FRLzFyVVRkS2xXVzNkd1U3MjlFeGhSNnhJTUcyUTZm"
                "SXJ0KzFPSUl0OFhnUWRPTmgzMENIbWZTdXQvd3dKWVdZRU1JUDI5YnQxNzYzVzYzRjA1MGhUenJy"
                "d2VISEFGSDNlbzltRWF0L3BnMTFBNjRmWnNuZ0lhYTdhQXdYTHdaenZzM0VRbVA2Wks0akdsZyUz"
                ""
            )

            # Descodifica a chave privada de Base64 para texto limpo
            decoded_key = base64.b64decode(private_key_base64).decode('utf-8')

            cred_dict = {
                "type": "service_account",
                "project_id": "grupoffkaraoke",
                "private_key_id": "fd6401fac635c511b593671f109f4fdc079042c7",
                "private_key": decoded_key,
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

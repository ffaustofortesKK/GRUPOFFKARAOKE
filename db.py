import json
import os
import streamlit as st
from datetime import datetime

# Inicialização segura do Firebase
FIREBASE_ATIVO = False
try:
    import firebase_admin
    import firebase_admin.credentials as credentials
    from firebase_admin import db
    
    if not firebase_admin._apps:
        if "firebase" not in st.secrets:
            st.error("A secção [firebase] não foi encontrada nos st.secrets do Streamlit.")
            raise Exception("Falta st.secrets['firebase']")
            
        secrets_dict = dict(st.secrets["firebase"])
        pk = secrets_dict.get("private_key", "")
        if pk:
            pk = pk.strip().strip('"').strip("'")
            pk = pk.replace("\\n", "\n")
            secrets_dict["private_key"] = pk

        cred = credentials.Certificate(secrets_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://grupoffkaraoke-default-rtdb.firebaseio.com'
        })
    FIREBASE_ATIVO = True
except Exception as e:
    st.sidebar.error(f"Aviso Firebase Desligado: {e}")
    FIREBASE_ATIVO = False

FICHEIRO_DB = "prestadores.json"
FICHEIRO_PEDIDOS_LOCAL = "pedidos_locais.json"

def _carregar_dados():
    if FIREBASE_ATIVO:
        try:
            for no in ["providers", "prestadores", "prestadores_config"]:
                ref = db.reference(no)
                dados = ref.get()
                if dados:
                    if isinstance(dados, dict):
                        return list(dados.values())
                    elif isinstance(dados, list):
                        return [p for p in dados if p is not None]
            return []
        except Exception as e:
            print(f"Erro ao ler prestadores do Firebase: {e}")

    if not os.path.exists(FICHEIRO_DB):
        return []
    try:
        with open(FICHEIRO_DB, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            dados = json.loads(content)
            return dados if isinstance(dados, list) else []
    except Exception:
        return []

def _guardar_dados(lista_prestadores):
    if FIREBASE_ATIVO:
        try:
            ref = db.reference("providers")
            dados_dict = {}
            for p in lista_prestadores:
                token = str(p.get("token", f"token_{id(p)}"))
                dados_dict[token] = p
            ref.set(dados_dict)
            return
        except Exception as e:
            print(f"Erro ao guardar prestadores no Firebase: {e}")

    try:
        with open(FICHEIRO_DB, "w", encoding="utf-8") as f:
            json.dump(lista_prestadores, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao guardar dados localmente: {e}")

def obter_prestadores():
    return _carregar_dados()

def guardar_prestador(prestador_dict):
    prestadores = _carregar_dados()
    token_atual = str(prestador_dict.get("token"))
    prestadores = [p for p in prestadores if str(p.get("token")) != token_atual]
    prestadores.insert(0, prestador_dict)
    _guardar_dados(prestadores)

def remover_prestador(token):
    prestadores = _carregar_dados()
    prestadores = [p for p in prestadores if str(p.get("token")) != str(token)]
    _guardar_dados(prestadores)

def guardar_pedido_musica(dados_pedido):
    """Guarda o pedido de música garantindo persistência no Firebase (nó 'pedidos') e backup local"""
    lista_local = []
    if os.path.exists(FICHEIRO_PEDIDOS_LOCAL):
        try:
            with open(FICHEIRO_PEDIDOS_LOCAL, "r", encoding="utf-8") as f:
                lista_local = json.load(f)
                if not isinstance(lista_local, list):
                    lista_local = []
        except:
            lista_local = []
    
    lista_local.insert(0, dados_pedido)
    try:
        with open(FICHEIRO_PEDIDOS_LOCAL, "w", encoding="utf-8") as f:
            json.dump(lista_local, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar cache local de pedidos: {e}")

    if FIREBASE_ATIVO:
        try:
            ref = db.reference("pedidos")
            valor_atual = ref.get()
            if valor_atual == "" or not isinstance(valor_atual, (dict, list)):
                ref.set(None)
            
            ref.push(dados_pedido)
        except Exception as e:
            print(f"Erro ao escrever pedidos no Firebase: {e}")

def obter_pedidos_musicas():
    """Combina os pedidos do Firebase e do armazenamento local ordenados rigorosamente por data/hora real"""
    pedidos_dict = {}
    
    # 1. Carrega do Firebase
    if FIREBASE_ATIVO:
        try:
            ref = db.reference("pedidos")
            dados = ref.get()
            if dados:
                if isinstance(dados, dict):
                    for chave, valor in dados.items():
                        if isinstance(valor, dict):
                            valor["id"] = chave
                            cantor_val = str(valor.get('cantor', '')).strip().lower()
                            musica_val = str(valor.get('musica', '')).strip().lower()
                            ts_val = valor.get('timestamp', '')
                            chave_unica = f"{cantor_val}_{musica_val}_{ts_val}"
                            pedidos_dict[chave_unica] = valor
                elif isinstance(dados, list):
                    for idx, valor in enumerate(dados):
                        if isinstance(valor, dict):
                            valor["id"] = str(idx)
                            cantor_val = str(valor.get('cantor', '')).strip().lower()
                            musica_val = str(valor.get('musica', '')).strip().lower()
                            ts_val = valor.get('timestamp', '')
                            chave_unica = f"{cantor_val}_{musica_val}_{ts_val}"
                            pedidos_dict[chave_unica] = valor
        except Exception as e:
            print(f"Erro ao obter pedidos do Firebase: {e}")
    
    # 2. Carrega do ficheiro local e funde
    if os.path.exists(FICHEIRO_PEDIDOS_LOCAL):
        try:
            with open(FICHEIRO_PEDIDOS_LOCAL, "r", encoding="utf-8") as f:
                locais = json.load(f)
                if isinstance(locais, list):
                    for valor in locais:
                        if isinstance(valor, dict):
                            cantor_val = str(valor.get('cantor', '')).strip().lower()
                            musica_val = str(valor.get('musica', '')).strip().lower()
                            ts_val = valor.get('timestamp', '')
                            chave_unica = f"{cantor_val}_{musica_val}_{ts_val}"
                            if chave_unica not in pedidos_dict:
                                pedidos_dict[chave_unica] = valor
        except Exception as e:
            print(f"Erro ao ler cache local de pedidos: {e}")
            
    lista_pedidos = list(pedidos_dict.values())
    
    # 3. Ordenação cronológica rigorosa usando datetime
    def parse_timestamp(p):
        ts_str = p.get("timestamp", "")
        try:
            return datetime.strptime(ts_str, "%d/%m/%Y %H:%M:%S")
        except:
            return datetime.min

    lista_pedidos.sort(key=parse_timestamp)
    
    return lista_pedidos

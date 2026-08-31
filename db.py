import json
import os
import streamlit as st

# Inicialização segura do Firebase com diagnóstico detalhado de erros
FIREBASE_ATIVO = False
try:
    import firebase_admin
    from firebase_admin import credentials, db
    
    if not firebase_admin._apps:
        if "firebase" not in st.secrets:
            raise Exception("A secção [firebase] não foi encontrada nos st.secrets.")
            
        secrets_dict = dict(st.secrets["firebase"])
        
        # Limpeza e correção robusta da chave privada para evitar erros de PEM/framing
        pk = secrets_dict.get("private_key", "")
        if pk:
            pk = pk.strip('"').strip("'")
            pk = pk.replace("\\n", "\n")
            secrets_dict["private_key"] = pk

        cred = credentials.Certificate(secrets_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://grupoffkaraoke-default-rtdb.firebaseio.com'
        })
    FIREBASE_ATIVO = True
except Exception as e:
    # Mostra exatamente o erro que está a impedir a ativação do Firebase
    st.error(f"🔍 DIAGNÓSTICO FIREBASE: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
    FIREBASE_ATIVO = False

FICHEIRO_DB = "prestadores.json"

def _carregar_dados():
    """Lê os prestadores do Firebase ou do ficheiro local como alternativa"""
    if FIREBASE_ATIVO:
        try:
            ref = db.reference("prestadores")
            dados = ref.get()
            if not dados:
                return []
            if isinstance(dados, dict):
                return list(dados.values())
            elif isinstance(dados, list):
                return [p for p in dados if p is not None]
            return []
        except Exception as e:
            print(f"Erro ao ler do Firebase: {e}")

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
    """Guarda a lista de prestadores"""
    if FIREBASE_ATIVO:
        try:
            ref = db.reference("prestadores")
            dados_dict = {}
            for p in lista_prestadores:
                token = str(p.get("token", f"token_{id(p)}"))
                dados_dict[token] = p
            ref.set(dados_dict)
            return
        except Exception as e:
            print(f"Erro ao guardar no Firebase: {e}")

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
    """Guarda um novo pedido de música no Firebase usando .push() na árvore 'pedidos'"""
    if FIREBASE_ATIVO:
        ref = db.reference("pedidos")
        ref.push(dados_pedido)
    else:
        raise Exception("O Firebase não está ativo (FIREBASE_ATIVO = False). Verifique as credenciais no st.secrets.")

def obter_pedidos_musicas():
    """Vai buscar os pedidos de músicas diretamente à árvore 'pedidos' do Firebase"""
    if FIREBASE_ATIVO:
        try:
            ref = db.reference("pedidos")
            dados = ref.get()
            if not dados:
                return []
            
            lista_pedidos = []
            if isinstance(dados, dict):
                for chave, valor in dados.items():
                    if isinstance(valor, dict):
                        valor["id"] = chave
                        lista_pedidos.append(valor)
            elif isinstance(dados, list):
                for idx, valor in enumerate(dados):
                    if isinstance(valor, dict):
                        valor["id"] = str(idx)
                        lista_pedidos.append(valor)
            return lista_pedidos
        except Exception as e:
            print(f"Erro ao obter pedidos do Firebase: {e}")
    return []

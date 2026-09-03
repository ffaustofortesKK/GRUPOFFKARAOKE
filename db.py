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
    """Guarda o pedido de música adicionando-o ao FIM da fila (local e Firebase)"""
    
    # 1. Carregar cache local atual e adicionar no fim (append)
    lista_local = []
    if os.path.exists(FICHEIRO_PEDIDOS_LOCAL):
        try:
            with open(FICHEIRO_PEDIDOS_LOCAL, "r", encoding="utf-8") as f:
                lista_local = json.load(f)
                if not isinstance(lista_local, list):
                    lista_local = []
        except:
            lista_local = []
    
    lista_local.append(dados_pedido)
    try:
        with open(FICHEIRO_PEDIDOS_LOCAL, "w", encoding="utf-8") as f:
            json.dump(lista_local, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"❌ Erro ao salvar cache local: {e}")

    # 2. Enviar para o Firebase no nó explícito "pedidos"
    if FIREBASE_ATIVO:
        try:
            ref = db.reference("pedidos")
            valor_atual = ref.get()
            if valor_atual == "" or not isinstance(valor_atual, (dict, list)):
                ref.set(None)
            
            # Utiliza push para gerar ID único no Firebase (adiciona ao fim)
            ref.push(dados_pedido)
        except Exception as e:
            st.error(f"❌ ERRO CRÍTICO NO FIREBASE: {e}")

def guardar_pedidos_musicas(lista_pedidos):
    """Guarda ou atualiza a lista completa de pedidos de músicas na ordem correta (local e Firebase)."""
    try:
        with open(FICHEIRO_PEDIDOS_LOCAL, "w", encoding="utf-8") as f:
            json.dump(lista_pedidos, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao guardar pedidos locais: {e}")

    if FIREBASE_ATIVO:
        try:
            ref = db.reference("pedidos")
            dados_dict = {}
            for idx, p in enumerate(lista_pedidos):
                pid = str(p.get("id", f"pedido_{idx}"))
                dados_dict[pid] = p
            ref.set(dados_dict)
        except Exception as e:
            print(f"Erro ao atualizar pedidos no Firebase: {e}")

def apagar_pedido_musica(pedido_id):
    """Apaga um pedido de música específico pelo ID ou timestamp (Local e Firebase)."""
    pedido_id_str = str(pedido_id)
    
    if os.path.exists(FICHEIRO_PEDIDOS_LOCAL):
        try:
            with open(FICHEIRO_PEDIDOS_LOCAL, "r", encoding="utf-8") as f:
                lista_local = json.load(f)
                if isinstance(lista_local, list):
                    nova_lista = [
                        p for p in lista_local 
                        if str(p.get("id")) != pedido_id_str and str(p.get("timestamp")) != pedido_id_str
                    ]
                    with open(FICHEIRO_PEDIDOS_LOCAL, "w", encoding="utf-8") as f_out:
                        json.dump(nova_lista, f_out, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao apagar pedido local: {e}")

    if FIREBASE_ATIVO:
        try:
            ref = db.reference("pedidos")
            dados = ref.get()
            if isinstance(dados, dict):
                for chave, valor in dados.items():
                    if chave == pedido_id_str or str(valor.get("timestamp")) == pedido_id_str:
                        db.reference(f"pedidos/{chave}").delete()
                        break
        except Exception as e:
            print(f"Erro ao apagar pedido no Firebase: {e}")

def mover_pedido_cima(pedido_id):
    """Move um pedido uma posição acima na lista de pedidos."""
    lista = obter_pedidos_musicas()
    pedido_id_str = str(pedido_id)
    
    idx = -1
    for i, p in enumerate(lista):
        if str(p.get("id")) == pedido_id_str or str(p.get("timestamp")) == pedido_id_str:
            idx = i
            break
            
    if idx > 0:
        lista[idx], lista[idx - 1] = lista[idx - 1], lista[idx]
        guardar_pedidos_musicas(lista)

def mover_pedido_baixo(pedido_id):
    """Move um pedido uma posição abaixo na lista de pedidos."""
    lista = obter_pedidos_musicas()
    pedido_id_str = str(pedido_id)
    
    idx = -1
    for i, p in enumerate(lista):
        if str(p.get("id")) == pedido_id_str or str(p.get("timestamp")) == pedido_id_str:
            idx = i
            break
            
    if idx != -1 and idx < len(lista) - 1:
        lista[idx], lista[idx + 1] = lista[idx + 1], lista[idx]
        guardar_pedidos_musicas(lista)

def obter_pedidos_musicas():
    """Carrega os pedidos ordenando cronologicamente (o primeiro a pedir fica no topo, o mais recente entra no fim)."""
    pedidos_lista = []
    chaves_vistas = set()
    
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
                            ts_val = str(valor.get('timestamp', ''))
                            chave_unica = f"{cantor_val}_{musica_val}_{ts_val}"
                            if chave_unica not in chaves_vistas:
                                chaves_vistas.add(chave_unica)
                                pedidos_lista.append(valor)
                elif isinstance(dados, list):
                    for idx, valor in enumerate(dados):
                        if isinstance(valor, dict):
                            valor["id"] = str(idx)
                            cantor_val = str(valor.get('cantor', '')).strip().lower()
                            musica_val = str(valor.get('musica', '')).strip().lower()
                            ts_val = str(valor.get('timestamp', ''))
                            chave_unica = f"{cantor_val}_{musica_val}_{ts_val}"
                            if chave_unica not in chaves_vistas:
                                chaves_vistas.add(chave_unica)
                                pedidos_lista.append(valor)
        except Exception as e:
            print(f"Erro ao obter pedidos do Firebase: {e}")
    
    # 2. Carrega do ficheiro local e funde os em falta
    if os.path.exists(FICHEIRO_PEDIDOS_LOCAL):
        try:
            with open(FICHEIRO_PEDIDOS_LOCAL, "r", encoding="utf-8") as f:
                locais = json.load(f)
                if isinstance(locais, list):
                    for valor in locais:
                        if isinstance(valor, dict):
                            cantor_val = str(valor.get('cantor', '')).strip().lower()
                            musica_val = str(valor.get('musica', '')).strip().lower()
                            ts_val = str(valor.get('timestamp', ''))
                            chave_unica = f"{cantor_val}_{musica_val}_{ts_val}"
                            if chave_unica not in chaves_vistas:
                                chaves_vistas.add(chave_unica)
                                pedidos_lista.append(valor)
        except Exception as e:
            print(f"Erro ao ler cache local de pedidos: {e}")
            
    if not pedidos_lista:
        return []
        
    # Ordena por timestamp de forma CRESCENTE (reverse=False): o pedido mais antigo (primeiro feito) fica no topo (#1)
    try:
        pedidos_lista.sort(
            key=lambda x: datetime.strptime(str(x.get("timestamp", "")), "%d/%m/%Y %H:%M:%S") 
            if x.get("timestamp") else datetime.min, 
            reverse=False
        )
    except Exception:
        pass
        
    return pedidos_lista

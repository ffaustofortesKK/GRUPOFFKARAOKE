import json
import os
import streamlit as st

FICHEIRO_DB = "prestadores.json"

def _carregar_dados():
    if not os.path.exists(FICHEIRO_DB):
        dados_iniciais = []
        _guardar_dados(dados_iniciais)
        return dados_iniciais
    try:
        with open(FICHEIRO_DB, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception:
        return []

def _guardar_dados(lista_prestadores):
    try:
        with open(FICHEIRO_DB, "w", encoding="utf-8") as f:
            json.dump(lista_prestadores, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro ao salvar dados localmente: {e}")

def obter_prestadores():
    return _carregar_dados()

def guardar_prestador(prestador_dict):
    prestadores = _carregar_dados()
    # Remove se já existir o token para atualizar com os novos dados
    prestadores = [p for p in prestadores if p["token"] != prestador_dict["token"]]
    prestadores.append(prestador_dict)
    _guardar_dados(prestadores)

def atualizar_estado_prestador(token, approved):
    prestadores = _carregar_dados()
    for p in prestadores:
        if str(p["token"]) == str(token):
            p["approved"] = approved
    _guardar_dados(prestadores)

def remover_prestador(token):
    prestadores = _carregar_dados()
    prestadores = [p for p in prestadores if str(p["token"]) != str(token)]
    _guardar_dados(prestadores)

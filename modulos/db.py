import json
import os

FICHEIRO_DB = "prestadores.json"

def obter_prestadores():
    if not os.path.exists(FICHEIRO_DB):
        dados_iniciais = [
            {"token": "demo-111", "nome": "João Silva", "telefone": "921000000", "estabelecimento": "Bar Central", "plano": "1 Hora - 12 Mil Kwanzas", "approved": True, "segundos_restantes": 3600},
            {"token": "pend-222", "nome": "Carlos Mendes", "telefone": "923111222", "estabelecimento": "Restaurante O Kubico", "plano": "2 Horas - 17 Mil Kwanzas", "approved": False, "segundos_restantes": 7200}
        ]
        guardar_todos_prestadores(dados_iniciais)
        return dados_iniciais
    try:
        with open(FICHEIRO_DB, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception:
        return []

def guardar_todos_prestadores(lista_prestadores):
    try:
        with open(FICHEIRO_DB, "w", encoding="utf-8") as f:
            json.dump(lista_prestadores, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def guardar_prestador(prestador_dict):
    prestadores = obter_prestadores()
    prestadores = [p for p in prestadores if p["token"] != prestador_dict["token"]]
    prestadores.append(prestador_dict)
    guardar_todos_prestadores(prestadores)

import streamlit as st
from datetime import datetime
from db import guardar_pedido_musica, obter_pedidos_musicas, obter_prestadores

def render():
    query_params = st.query_params
    token_prestador = query_params.get("token", "").strip()
    
    # Se não veio token na URL ou veio "Nenhum", tenta encontrar o primeiro prestador aprovado disponível
    if not token_prestador or token_prestador.lower() == "nenhum":
        try:
            prestadores = obter_prestadores()
            prestador_ativo = next((p for p in prestadores if p.get("status_str") == "aprovado" or p.get("approved") == True), None)
            if prestador_ativo:
                token_prestador = prestador_ativo.get("token", "geral")
            else:
                token_prestador = "geral"
        except Exception:
            token_prestador = "geral"
    
    # 1. Inicializa o estado do nome do cliente se não existir
    if "cliente_nome" not in st.session_state:
        st.session_state["cliente_nome"] = ""

    # ESTADO 1: Inserir o Nome
    if not st.session_state["cliente_nome"]:
        st.markdown("### 🎤 Bem-vindo ao FF Karaoke")
        st.write("Insira o seu nome ou alcunha para começar:")
        
        with st.form(key="form_login_cliente"):
            cantor_input = st.text_input("O seu Nome / alcunha:", placeholder="Ex: João da Silva")
            submit_nome = st.form_submit_button("Entrar")
            
            if submit_nome:
                if cantor_input.strip():
                    st.session_state["cliente_nome"] = cantor_input.strip()
                    st.rerun()
                else:
                    st.error("Por favor, insira um nome ou alcunha válido.")
                    
    # ESTADO 2: Painel do Cliente
    else:
        cantor = st.session_state["cliente_nome"]
        
        st.markdown(f"### Bem-vindo {cantor}")
        st.info(f"Sessão vinculada ao Prestador / Sessão: `{token_prestador}`")
        
        # Obtém todos os pedidos da base de dados
        todos_pedidos = obter_pedidos_musicas()
        
        # Filtra estritamente todos os pedidos com status "pendente" para a fila geral
        pendentes_geral = [
            p for p in todos_pedidos 
            if str(p.get("status", "pendente")).strip().lower() == "pendente"
        ]
        
        # Filtra os pedidos específicos deste cantor na fila pendente
        pedidos_do_cliente = [
            p for p in pendentes_geral 
            if str(p.get("cantor", "")).strip().lower() == cantor.strip().lower()
        ]
        
        tem_pedido_ativo = len(pedidos_do_cliente) > 0
        
        if tem_pedido_ativo:
            primeiro_pedido_cliente = pedidos_do_cliente[0]
            
            # Encontra a posição exata (1-based index) na fila geral de pendentes
            posicao_real = -1
            for idx, p in enumerate(pendentes_geral):
                # Compara pelo ID ou pela combinação exata de cantor e música
                if p == primeiro_pedido_cliente or (
                    str(p.get("cantor", "")).strip().lower() == str(primeiro_pedido_cliente.get("cantor", "")).strip().lower() and 
                    str(p.get("musica", "")).strip().lower() == str(primeiro_pedido_cliente.get("musica", "")).strip().lower()
                ):
                    posicao_real = idx + 1
                    break
            
            # Caso de segurança se não encontrar por igualdade exata
            if posicao_real == -1:
                for idx, p in enumerate(pendentes_geral):
                    if str(p.get("cantor", "")).strip().lower() == cantor.strip().lower():
                        posicao_real = idx + 1
                        break

            musicas_acima = posicao_real - 1 if posicao_real > 0 else 0
            
            st.warning(f"🎵 O seu pedido (`{primeiro_pedido_cliente.get('musica', '')}`) está registado! Encontra-se atualmente na **posição {posicao_real}** da fila.")
            
            if musicas_acima > 4:
                st.error(f"⏳ **Aguarde!** Ainda tem {musicas_acima} músicas à sua frente. Só poderá enviar um novo pedido quando restarem 4 ou menos músicas para a sua vez.")
            else:
                st.success(f"🔔 **Pode enviar um novo pedido!** Faltam apenas {musicas_acima} músicas para a sua vez.")
                
                with st.form("form_cliente_novo"):
                    musica_novo = st.text_input("Digite o nome da próxima música ou artista:", placeholder="Ex: Landrick, Nani...")
                    submitted_novo = st.form_submit_button("Enviar Novo Pedido")
                    
                    if submitted_novo:
                        if musica_novo.strip():
                            dados_novo_pedido = {
                                "cantor": cantor,
                                "musica": musica_novo.strip(),
                                "token_prestador": token_prestador,
                                "status": "pendente",
                                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            }
                            guardar_pedido_musica(dados_novo_pedido)
                            st.success(f"Obrigado {cantor}! O seu novo pedido foi adicionado.")
                            st.rerun()
                        else:
                            st.error("Por favor, preencha o nome da música.")
        else:
            st.success("✅ Já poderá enviar o seu pedido!")
            
            with st.form("form_cliente"):
                st.markdown("### 🔍 Pesquisar / Pedir Música")
                musica_inicial = st.text_input("Digite o nome da música ou artista:", placeholder="Ex: Landrick, Nani...")
                submitted_inicial = st.form_submit_button("Pedir Música")
                
                if submitted_inicial:
                    if musica_inicial.strip():
                        dados_novo_pedido = {
                            "cantor": cantor,
                            "musica": musica_inicial.strip(),
                            "token_prestador": token_prestador,
                            "status": "pendente",
                            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        }
                        guardar_pedido_musica(dados_novo_pedido)
                        st.success(f"Obrigado {cantor}! A sua música foi adicionada à fila.")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o nome da música ou artista.")
        
        st.write("")
        if st.button("🔄 Alterar Nome"):
            st.session_state["cliente_nome"] = ""
            st.rerun()

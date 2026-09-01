import streamlit as st
from datetime import datetime
from db import guardar_pedido_musica, obter_pedidos_musicas, obter_prestadores

def render():
    query_params = st.query_params
    token_prestador = query_params.get("token", "").strip()
    
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
        
        # Filtra estritamente por status "pendente" E pelo token do prestador atual (se não for geral)
        pendentes_geral = []
        for p in todos_pedidos:
            status = str(p.get("status", "pendente")).strip().lower()
            t_ped = str(p.get("token_prestador", "geral")).strip()
            
            if status == "pendente":
                # Se a sessão for específica de um prestador, filtra por ele. Se for geral, aceita tudo ou o match correspondente.
                if token_prestador == "geral" or not t_ped or t_ped == token_prestador or t_ped == "geral":
                    pendentes_geral.append(p)
        
        # Filtra os pedidos específicos deste cantor exato (ignorando maiúsculas/minúsculas e espaços)
        pedidos_do_cliente = [
            p for p in pendentes_geral 
            if str(p.get("cantor", "")).strip().lower() == cantor.strip().lower()
        ]
        
        tem_pedido_ativo = len(pedidos_do_cliente) > 0
        
        if tem_pedido_ativo:
            # Pega no pedido mais recente ou no primeiro da lista do cliente
            primeiro_pedido_cliente = pedidos_do_cliente[0]
            
            # Encontra a posição real (1-based index) na fila global de pendentes deste prestador
            posicao_real = -1
            for idx, p in enumerate(pendentes_geral):
                if p == primeiro_pedido_cliente or (
                    str(p.get("cantor", "")).strip().lower() == cantor.strip().lower() and
                    str(p.get("musica", "")).strip().lower() == str(primeiro_pedido_cliente.get("musica", "")).strip().lower()
                ):
                    posicao_real = idx + 1
                    break
            
            if posicao_real == -1:
                posicao_real = 1

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
            for key in list(st.session_state.keys()):
                if key.startswith("form_") or key == "cliente_nome":
                    if key != "cliente_nome":
                        del st.session_state[key]
            st.session_state["cliente_nome"] = ""
            st.rerun()

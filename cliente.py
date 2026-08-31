import streamlit as st
from db import guardar_pedido_musica, obter_pedidos_musicas

def render():
    query_params = st.query_params
    token_prestador = query_params.get("token", "Nenhum")
    
    # 1. Inicializa o estado do nome do cliente se não existir
    if "cliente_nome" not in st.session_state:
        st.session_state["cliente_nome"] = ""

    # ESTADO 1: Inserir o Nome (1ª Imagem)
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
                    
    # ESTADO 2: Painel do Cliente (2ª Imagem com Gestão de Fila Real)
    else:
        cantor = st.session_state["cliente_nome"]
        
        st.markdown(f"### Benvindo {cantor}")
        st.info(f"Sessão vinculada ao Prestador Token: `{token_prestador}`")
        
        # Obtém todos os pedidos pendentes da base de dados filtrados para este prestador
        todos_pedidos = obter_pedidos_musicas()
        
        # Filtra apenas os pedidos pendentes do prestador atual
        pendentes_geral = [
            p for p in todos_pedidos 
            if p.get("status", "pendente") == "pendente" 
            and str(p.get("token_prestador", "")) == str(token_prestador)
        ]
        
        # Filtra os pedidos específicos deste cantor
        pedidos_do_cliente = [
            p for p in pendentes_geral 
            if str(p.get("cantor", "")).strip().lower() == cantor.strip().lower()
        ]
        
        tem_pedido_ativo = len(pedidos_do_cliente) > 0
        
        if tem_pedido_ativo:
            # Encontra a posição exata do PRIMEIRO pedido ativo deste cliente na fila geral do prestador
            primeiro_pedido_cliente = pedidos_do_cliente[0]
            
            posicao_real = -1
            for idx, p in enumerate(pendentes_geral):
                # Compara usando os dados únicos ou o ID se existir
                if p == primeiro_pedido_cliente or (str(p.get("cantor","")).strip().lower() == str(primeiro_pedido_cliente.get("cantor","")).strip().lower() and str(p.get("musica","")) == str(primeiro_pedido_cliente.get("musica","")) and str(p.get("timestamp","")) == str(primeiro_pedido_cliente.get("timestamp",""))):
                    posicao_real = idx + 1
                    break
            
            # Se por algum motivo não encontrar pelo objeto exato, pega pelo índice do primeiro match na lista geral
            if posicao_real == -1:
                for idx, p in enumerate(pendentes_geral):
                    if str(p.get("cantor", "")).strip().lower() == cantor.strip().lower():
                        posicao_real = idx + 1
                        break

            musicas_acima = posicao_real - 1 if posicao_real > 0 else 0
            
            # Alerta com a posição correta na fila
            st.warning(f"🎵 O seu pedido (`{primeiro_pedido_cliente.get('musica', '')}`) está registado! Encontra-se atualmente na **posição {posicao_real}** da fila.")
            
            # Regra: Só pode enviar novo pedido se houver 4 ou menos músicas à frente dele (ou seja, quando restarem 4 ou menos para a vez dele)
            if musicas_acima > 4:
                st.error(f"⏳ **Aguarde!** Ainda tem {musicas_acima} músicas à sua frente. Só poderá enviar um novo pedido quando restarem 4 ou menos músicas para a sua vez.")
            else:
                st.success(f"🔔 **Pode enviar um novo pedido!** Faltam apenas {musicas_acima} músicas para a sua vez.")
                
                # Formulário para enviar novo pedido
                with st.form("form_cliente_novo", clear_on_submit=True):
                    musica = st.text_input("Digite o nome da próxima música ou artista:", placeholder="Ex: Landrick, Nani...")
                    submitted = st.form_submit_button("Enviar Novo Pedido")
                    
                    if submitted:
                        if musica.strip():
                            try:
                                guardar_pedido_musica({
                                    "cantor": cantor,
                                    "musica": musica.strip(),
                                    "token_prestador": token_prestador,
                                    "status": "pendente"
                                })
                                st.success(f"Obrigado {cantor}! O seu novo pedido foi adicionado.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao enviar o pedido: {e}")
                        else:
                            st.error("Por favor, preencha o nome da música.")
        else:
            # Se não tem nenhum pedido pendente na fila, pode enviar livremente
            st.success("✅ Já poderá enviar o seu pedido!")
            
            with st.form("form_cliente", clear_on_submit=True):
                st.markdown("### 🔍 Pesquisar / Pedir Música")
                musica = st.text_input("Digite o nome da música ou artista:", placeholder="Ex: Landrick, Nani...")
                submitted = st.form_submit_button("Pedir Música")
                
                if submitted:
                    if musica.strip():
                        try:
                            guardar_pedido_musica({
                                "cantor": cantor,
                                "musica": musica.strip(),
                                "token_prestador": token_prestador,
                                "status": "pendente"
                            })
                            st.success(f"Obrigado {cantor}! A sua música '{musica}' foi adicionada à fila.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro detalhado ao enviar o pedido: {e}")
                    else:
                        st.error("Por favor, preencha o nome da música ou artista.")
        
        # Botão para alterar nome / reiniciar sessão
        if st.button("🔄 Alterar Nome"):
            st.session_state["cliente_nome"] = ""
            st.rerun()

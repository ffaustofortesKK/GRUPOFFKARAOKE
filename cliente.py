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
                    
    # ESTADO 2: Painel do Cliente (2ª Imagem com Gestão de Fila)
    else:
        cantor = st.session_state["cliente_nome"]
        
        st.markdown(f"### Benvindo {cantor}")
        st.info(f"Sessão vinculada ao Prestador Token: `{token_prestador}`")
        
        # Obtém todos os pedidos atuais da base de dados para calcular a fila
        todos_pedidos = obter_pedidos_musicas()
        
        # Filtra os pedidos que pertencem a este cantor específico e que estão pendentes/na fila
        pedidos_do_cliente = [
            p for p in todos_pedidos 
            if str(p.get("cantor", "")).strip().lower() == cantor.strip().lower() 
            and str(p.get("token_prestador", "")) == str(token_prestador)
            and p.get("status", "pendente") == "pendente"
        ]
        
        # Verifica se o cliente tem pedidos ativos na fila
        tem_pedido_ativo = len(pedidos_do_cliente) > 0
        
        if tem_pedido_ativo:
            # Encontra a posição exata do primeiro pedido deste cliente na fila geral
            posicao = -1
            pendentes_geral = [p for p in todos_pedidos if p.get("status", "pendente") == "pendente"]
            
            for idx, p in enumerate(pendentes_geral):
                if str(p.get("cantor", "")).strip().lower() == cantor.strip().lower():
                    posicao = idx + 1
                    break
            
            # Conta quantos pedidos faltam para o cliente (quantos estão à frente dele na fila)
            pedidos_a_frente = posicao - 1 if posicao > 0 else 0
            
            # Regra: Se houver 4 ou mais pedidos à frente, exibe aviso de restrição
            if pedidos_a_frente >= 4:
                st.warning(f"⏳ **Aguarde!** Tem uma música na fila (Posição: **{posicao}**). Faltam {pedidos_a_frente} músicas para a sua vez. Assim que restarem menos de 4 músicas à sua frente, poderá enviar novo pedido.")
            else:
                # Regra: Se tiver menos de 4 pedidos à frente, notifica que já pode enviar novo pedido, mas avisa do atual
                if pedidos_a_frente > 0:
                    st.success(f"🔔 **Pode enviar um novo pedido!** (A sua música anterior está na posição {posicao}, restam apenas {pedidos_a_frente} à frente).")
                else:
                    st.success(f"🎉 **A sua música é a próxima ou está a tocar!** Pode enviar um novo pedido.")

            # Formulário para envio de novo pedido (caso as condições permitam ou controlado)
            with st.form("form_cliente_novo", clear_on_submit=True):
                st.markdown("### 🔍 Pedir Outra Música")
                musica = st.text_input("Digite o nome da música ou artista:", placeholder="Ex: Landrick, Nani...")
                submitted = st.form_submit_button("Enviar Novo Pedido")
                
                if submitted:
                    if pedidos_a_frente >= 4:
                        st.error("❌ Ainda tem uma música por cantar e faltam mais de 4 músicas na fila. Aguarde a sua vez!")
                    elif musica.strip():
                        try:
                            guardar_pedido_musica({
                                "cantor": cantor,
                                "musica": musica.strip(),
                                "token_prestador": token_prestador,
                                "status": "pendente"
                            })
                            st.success(f"Obrigado {cantor}! O seu novo pedido '{musica}' foi adicionado.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao enviar o pedido: {e}")
                    else:
                        st.error("Por favor, preencha o nome da música.")
        else:
            # Se não tem nenhum pedido pendente, pode enviar livremente
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

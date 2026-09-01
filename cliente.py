import streamlit as st
from datetime import datetime
from db import guardar_pedido_musica, obter_pedidos_musicas, obter_prestadores

def render():
    # Estilização CSS Global Inspirada no FF Karaoke (Tema Escuro / Roxo Premium)
    st.markdown("""
        <style>
        .stApp {
            background-color: #0b0714;
            color: #ffffff;
        }
        /* Topo / Header Banner */
        .ff-header {
            background: linear-gradient(135deg, #1a1333 0%, #0b0714 100%);
            border: 1px solid rgba(138, 43, 226, 0.3);
            padding: 15px 25px;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }
        .ff-logo-title {
            font-size: 24px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .ff-badge-online {
            background-color: rgba(46, 204, 113, 0.15);
            color: #2ecc71;
            border: 1px solid rgba(46, 204, 113, 0.4);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        /* Blocos de Notificação Estilizados */
        .ff-card-status {
            background-color: #151026;
            border: 1px solid rgba(138, 43, 226, 0.25);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .ff-card-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .ff-icon-box {
            background: linear-gradient(135deg, #7b2cbf, #9d4edd);
            width: 45px;
            height: 45px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: white;
            box-shadow: 0 0 10px rgba(123, 44, 191, 0.5);
        }
        .ff-card-text h4 {
            margin: 0;
            font-size: 16px;
            color: #ffffff;
            font-weight: 600;
        }
        .ff-card-text p {
            margin: 4px 0 0 0;
            font-size: 13px;
            color: #b19cd9;
        }
        .ff-badge-circle {
            border: 2px solid #9d4edd;
            color: #ffffff;
            background: rgba(157, 78, 221, 0.1);
            min-width: 65px;
            height: 65px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            box-shadow: 0 0 12px rgba(157, 78, 221, 0.3);
        }
        .ff-badge-circle .number {
            font-size: 18px;
            font-weight: 800;
            line-height: 1;
            color: #ffffff;
        }
        .ff-badge-circle .label {
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #b19cd9;
            margin-top: 2px;
        }

        /* Caixa de Ação / Pedido */
        .ff-action-box {
            background-color: #120e21;
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 12px;
            padding: 25px;
            margin-top: 20px;
        }

        /* Secção Como Funciona */
        .ff-how-it-works-title {
            text-align: center;
            color: #b19cd9;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 35px 0 15px 0;
            font-weight: 600;
        }
        .ff-steps-container {
            display: flex;
            gap: 15px;
            justify-content: space-between;
            margin-bottom: 30px;
        }
        .ff-step-card {
            background-color: #120e21;
            border: 1px solid rgba(138, 43, 226, 0.2);
            border-radius: 10px;
            padding: 15px;
            flex: 1;
            text-align: left;
        }
        .ff-step-number {
            background: #7b2cbf;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .ff-step-card h5 {
            margin: 0 0 4px 0;
            font-size: 14px;
            color: #ffffff;
        }
        .ff-step-card p {
            margin: 0;
            font-size: 11px;
            color: #9a8c98;
            line-height: 1.4;
        }
        </style>
    """, unsafe_allow_html=True)

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

    # CABEÇALHO VISUAL DO TOPO
    st.markdown("""
        <div class="ff-header">
            <div class="ff-logo-title">🎵 FF KARAOKE <span style="font-size:11px; font-weight:400; color:#b19cd9; display:block;">FAZ A VOZ, FAZ A FESTA!</span></div>
            <div><span class="ff-badge-online">● Online</span></div>
        </div>
    """, unsafe_allow_html=True)

    # ESTADO 1: Inserir o Nome
    if not st.session_state["cliente_nome"]:
        st.markdown("### 🎤 Bem-vindo ao FF Karaoke")
        st.write("Insira o seu nome ou alcunha para começar:")
        
        with st.form(key="form_login_cliente", clear_on_submit=True):
            cantor_input = st.text_input("O seu Nome / alcunha:", placeholder="Ex: João da Silva")
            submit_nome = st.form_submit_button("Entrar no Sistema")
            
            if submit_nome:
                if cantor_input.strip():
                    st.session_state["cliente_nome"] = cantor_input.strip()
                    st.rerun()
                else:
                    st.error("Por favor, insira um nome ou alcunha válido.")
                    
    # ESTADO 2: Painel do Cliente
    else:
        cantor = st.session_state["cliente_nome"]
        
        st.caption(f"Sessão vinculada ao Prestador / Sessão: `{token_prestador}`")
        
        # 1. Obtém todos os pedidos da base de dados
        todos_pedidos = obter_pedidos_musicas()
        
        pendentes_geral = []
        for p in todos_pedidos:
            status = str(p.get("status", "pendente")).strip().lower()
            t_ped = str(p.get("token_prestador", "geral")).strip()
            
            if status == "pendente":
                if token_prestador == "geral" or not t_ped or t_ped == "geral" or t_ped == token_prestador:
                    pendentes_geral.append(p)
        
        # Identifica todos os pedidos deste cliente específico na fila
        pedidos_do_cliente = [
            p for p in pendentes_geral 
            if str(p.get("cantor", "")).strip().lower() == cantor.strip().lower()
        ]
        
        tem_pedido_ativo = len(pedidos_do_cliente) > 0
        
        if tem_pedido_ativo:
            primeiro_pedido_cliente = pedidos_do_cliente[0]
            
            # Calcula a posição real (1-based index)
            posicao_real = -1
            c_alvo = str(primeiro_pedido_cliente.get("cantor", "")).strip().lower()
            m_alvo = str(primeiro_pedido_cliente.get("musica", "")).strip().lower()
            
            for idx, p in enumerate(pendentes_geral):
                c_atual = str(p.get("cantor", "")).strip().lower()
                m_atual = str(p.get("musica", "")).strip().lower()
                
                if c_atual == c_alvo and m_atual == m_alvo:
                    posicao_real = idx + 1
                    break
            
            if posicao_real == -1:
                posicao_real = 1
                
            musicas_acima = posicao_real - 1 if posicao_real > 0 else 0
            
            # Bloco Visual 1: Posição do Pedido Atual
            musica_nome_atv = primeiro_pedido_cliente.get('musica', '')
            st.markdown(f"""
                <div class="ff-card-status">
                    <div class="ff-card-left">
                        <div class="ff-icon-box">🎵</div>
                        <div class="ff-card-text">
                            <h4>O seu pedido ({musica_nome_atv}) está registado!</h4>
                            <p>Encontra-se atualmente na <b>posição {posicao_real}</b> da fila.</p>
                        </div>
                    </div>
                    <div class="ff-badge-circle">
                        <span class="number">#{posicao_real}</span>
                        <span class="label">Na Fila</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if musicas_acima > 4:
                st.markdown(f"""
                    <div class="ff-card-status" style="border-color: rgba(231, 76, 60, 0.4);">
                        <div class="ff-card-left">
                            <div class="ff-icon-box" style="background: linear-gradient(135deg, #c0392b, #e74c3c);">⏳</div>
                            <div class="ff-card-text">
                                <h4>Aguarde a sua vez!</h4>
                                <p>Ainda tem {musicas_acima} músicas à sua frente. Poderá pedir nova música quando restarem 4 ou menos.</p>
                            </div>
                        </div>
                        <div class="ff-badge-circle" style="border-color: #e74c3c;">
                            <span class="number">{musicas_acima}</span>
                            <span class="label">Restam</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="ff-card-status" style="border-color: rgba(46, 204, 113, 0.4);">
                        <div class="ff-card-left">
                            <div class="ff-icon-box" style="background: linear-gradient(135deg, #27ae60, #2ecc71);">🔔</div>
                            <div class="ff-card-text">
                                <h4>Pode enviar um novo pedido!</h4>
                                <p>Faltam apenas {musicas_acima} músicas para a sua vez.</p>
                            </div>
                        </div>
                        <div class="ff-badge-circle" style="border-color: #2ecc71;">
                            <span class="number">{musicas_acima}</span>
                            <span class="label">Faltam</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="ff-action-box">', unsafe_allow_html=True)
                st.markdown("##### 🎤 PEÇA A SUA PRÓXIMA MÚSICA")
                with st.form("form_cliente_novo", clear_on_submit=True):
                    musica_novo = st.text_input("Digite o nome da próxima música ou artista:", placeholder="Ex: Landrick, Nani, Matias Damásio...")
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
                            st.success("Pedido enviado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Por favor, preencha o nome da música.")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            total_fila_geral = len(pendentes_geral)
            st.info(f"ℹ️ Atualmente existem **{total_fila_geral} músicas** na fila de espera global.")
            
            st.markdown('<div class="ff-action-box">', unsafe_allow_html=True)
            st.markdown("##### 🔍 PESQUISAR / PEDIR MÚSICA")
            with st.form("form_cliente", clear_on_submit=True):
                musica_inicial = st.text_input("Digite o nome da música ou artista:", placeholder="Ex: Kendrick Lamar, Bruno Mars, Matias Damásio...")
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
                        st.success("Pedido adicionado à fila!")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o nome da música ou artista.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        # SECÇÃO COMO FUNCIONA
        st.markdown('<div class="ff-how-it-works-title">🎧 COMO FUNCIONA?</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="ff-steps-container">
                <div class="ff-step-card">
                    <div class="ff-step-number">1</div>
                    <h5>Escolha</h5>
                    <p>Digite o nome da música ou do artista.</p>
                </div>
                <div class="ff-step-card">
                    <div class="ff-step-number">2</div>
                    <h5>Aguarde</h5>
                    <p>Acompanhe a sua posição na fila em tempo real.</p>
                </div>
                <div class="ff-step-card">
                    <div class="ff-step-number">3</div>
                    <h5>Cante</h5>
                    <p>Quando chegar a sua vez, é só dar o show!</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("🔄 Alterar Nome"):
            st.session_state["cliente_nome"] = ""
            for key in list(st.session_state.keys()):
                if key.startswith("form_") or key == "cliente_nome":
                    if key != "cliente_nome":
                        del st.session_state[key]
            st.session_state["cliente_nome"] = ""
            st.rerun()

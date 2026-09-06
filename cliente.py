from datetime import datetime
import time
import streamlit as st
from db import guardar_pedido_musica, obter_pedidos_musicas, obter_prestadores

def render():
    st.markdown("""
        <style>
        .stApp {
            background-color: #06040b;
            color: #ffffff;
        }
        
        header[data-testid="stHeader"] {
            background-color: #06040b !important;
        }
        
        .block-container {
            max-width: 780px !important;
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            background-color: #0b0714;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.8);
            border: 1px solid rgba(138, 43, 226, 0.25);
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .ff-header {
            background: linear-gradient(135deg, #1a1333 0%, #0b0714 100%);
            border: 1px solid rgba(138, 43, 226, 0.3);
            padding: 10px 14px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            box-shadow: 0 3px 15px rgba(0, 0, 0, 0.5);
        }
        .ff-logo-area {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .ff-logo-icon {
            background: linear-gradient(135deg, #7b2cbf, #9d4edd);
            width: 38px;
            height: 38px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 12px rgba(123, 44, 191, 0.7);
            flex-shrink: 0;
        }
        .ff-logo-text-group {
            display: flex;
            flex-direction: column;
        }
        .ff-logo-title {
            font-size: 16px;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: 1px;
            line-height: 1.1;
        }
        .ff-logo-subtitle {
            font-size: 8.5px;
            font-weight: 500;
            color: #b19cd9;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .ff-badge-online {
            background-color: rgba(46, 204, 113, 0.15);
            color: #2ecc71;
            border: 1px solid rgba(46, 204, 113, 0.4);
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 600;
        }
        
        .ff-cantor-box {
            background: linear-gradient(135deg, #151026, #1e133a);
            border: 1px solid rgba(138, 43, 226, 0.4);
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        }
        .ff-cantor-label {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #b19cd9;
            margin-bottom: 2px;
        }

        @keyframes wave-animation {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-4px); }
        }

        .ff-cantor-name {
            font-size: 34px;
            font-weight: 900;
            display: inline-flex;
            gap: 4px;
            text-shadow: 0 2px 12px rgba(157, 78, 221, 0.6);
            line-height: 1.1;
        }
        
        .ff-cantor-name span {
            display: inline-block;
            animation: wave-animation 1.5s infinite ease-in-out;
        }
        
        .ff-cantor-name span:nth-child(5n+1) { color: #ff007f; animation-delay: 0.0s; }
        .ff-cantor-name span:nth-child(5n+2) { color: #00f0ff; animation-delay: 0.2s; }
        .ff-cantor-name span:nth-child(5n+3) { color: #ffe600; animation-delay: 0.4s; }
        .ff-cantor-name span:nth-child(5n+4) { color: #b19cd9; animation-delay: 0.6s; }
        .ff-cantor-name span:nth-child(5n+5) { color: #2ecc71; animation-delay: 0.8s; }
        
        .ff-number-fixed {
            display: inline-block;
            font-size: 28px;
            font-weight: 900;
            color: #eab308;
            text-shadow: 0 0 15px rgba(234, 179, 8, 0.5);
            margin: 2px 0;
            line-height: 1;
        }

        .ff-card-status-centered {
            background-color: #120e21;
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .ff-card-title-yellow {
            font-size: 12px;
            color: #eab308;
            font-weight: 800;
            letter-spacing: 1px;
            margin-bottom: 2px;
            text-transform: uppercase;
        }
        .ff-card-title-orange {
            font-size: 12px;
            color: #e74c3c;
            font-weight: 800;
            letter-spacing: 1px;
            margin-bottom: 2px;
            text-transform: uppercase;
        }
        .ff-card-title-green {
            font-size: 12px;
            color: #2ecc71;
            font-weight: 800;
            letter-spacing: 1px;
            margin-bottom: 2px;
            text-transform: uppercase;
        }
        .ff-card-subtitle {
            font-size: 10px;
            color: #b19cd9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
            font-weight: 700;
        }
        .ff-card-main-text {
            font-size: 15px;
            color: #ffffff;
            font-weight: 700;
            margin: 2px 0 0 0;
        }

        .ff-fila-wrapper {
            background: linear-gradient(90deg, #18122c, #22183d, #18122c);
            border: 1px solid rgba(138, 43, 226, 0.4);
            border-radius: 8px;
            padding: 8px 0;
            width: 100%;
            box-sizing: border-box;
            text-align: left;
            box-shadow: inset 0 2px 6px rgba(0,0,0,0.5);
            margin-top: 10px;
            margin-bottom: 6px;
            overflow: hidden;
        }
        .ff-fila-header-title {
            font-size: 9.5px;
            color: #b19cd9;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 700;
            margin-bottom: 4px;
            text-align: center;
        }

        @keyframes marquee-anim {
            0% { transform: translateX(0%); }
            100% { transform: translateX(-50%); }
        }

        .ff-marquee-container {
            overflow: hidden;
            width: 100%;
            white-space: nowrap;
            position: relative;
        }

        .ff-marquee-content {
            display: inline-block;
            white-space: nowrap;
            animation: marquee-anim 12s linear infinite;
        }

        .ff-marquee-content:hover {
            animation-play-state: paused;
        }

        .fila-pos {
            color: #eab308;
            font-weight: 900;
        }
        .fila-cantor {
            color: #ffffff;
            font-weight: 800;
            text-shadow: 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 0 2px 4px rgba(0,0,0,0.9);
        }

        .ff-action-box {
            background-color: #120e21;
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 10px;
            padding: 10px;
            margin-top: 6px;
        }

        .ff-how-it-works-title {
            text-align: center;
            color: #b19cd9;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 8px 0 4px 0;
            font-weight: 600;
        }
        .ff-steps-container {
            display: flex;
            gap: 6px;
            justify-content: space-between;
            margin-bottom: 6px;
        }
        .ff-step-card {
            background-color: #120e21;
            border: 1px solid rgba(138, 43, 226, 0.2);
            border-radius: 8px;
            padding: 6px;
            flex: 1;
            text-align: left;
        }
        .ff-step-number {
            background: #7b2cbf;
            color: white;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 9px;
            font-weight: bold;
            margin-bottom: 2px;
        }
        .ff-step-card h5 {
            margin: 0 0 2px 0;
            font-size: 10px;
            color: #ffffff;
        }
        .ff-step-card p {
            margin: 0;
            font-size: 8px;
            color: #9a8c98;
            line-height: 1.1;
        }
        
        div.stButton > button {
            width: 100%;
            border-radius: 6px;
            font-weight: 600;
            background: linear-gradient(135deg, #7b2cbf, #5a189a);
            color: white;
            border: none;
            padding: 6px;
            font-size: 12px;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #9d4edd, #7b2cbf);
            border: none;
            color: white;
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
        
    if "meu_pedido_timestamp" not in st.session_state:
        st.session_state["meu_pedido_timestamp"] = None

    # CABEÇALHO COM LOGÓTIPO EMBUTIDO SEGURO (SVG Integrado - Nunca falha)
    st.markdown("""
        <div class="ff-header">
            <div class="ff-logo-area">
                <div class="ff-logo-icon">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v1a7 7 0 0 1-14 0v-1"></path>
                        <line x1="12" y1="19" x2="12" y2="22"></line>
                    </svg>
                </div>
                <div class="ff-logo-text-group">
                    <span class="ff-logo-title">FF KARAOKE</span>
                    <span class="ff-logo-subtitle">FAZ A VOZ, FAZ A FESTA!</span>
                </div>
            </div>
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
                    
    # ESTADO 2: Painel do Cliente com Fragmento Isolado
    else:
        cantor = st.session_state["cliente_nome"]
        
        letras_html = "".join([f"<span>{char}</span>" if char != " " else "<span>&nbsp;</span>" for char in cantor])
        
        st.markdown(f"""
            <div class="ff-cantor-box">
                <div class="ff-cantor-label">🎤 Cantor(a) em Sessão</div>
                <div class="ff-cantor-name">{letras_html}</div>
            </div>
        """, unsafe_allow_html=True)
        
        @st.fragment(run_every=5)
        def renderizar_painel_fila(cantor_atual, token_p):
            todos_pedidos = obter_pedidos_musicas()
            
            pendentes_geral = []
            vistos_timestamps = set()
            for p in todos_pedidos:
                status = str(p.get("status", "pendente")).strip().lower()
                t_ped = str(p.get("token_prestador", "geral")).strip()
                ts_id = str(p.get("timestamp", ""))
                
                if status == "pendente":
                    if token_p == "geral" or not t_ped or t_ped == "geral" or t_ped == token_p:
                        if ts_id not in vistos_timestamps:
                            vistos_timestamps.add(ts_id)
                            pendentes_geral.append(p)
            
            ts_ativo = st.session_state.get("meu_pedido_timestamp")
            pedido_ativo = None
            
            if ts_ativo:
                for p in pendentes_geral:
                    if str(p.get("timestamp", "")) == str(ts_ativo):
                        pedido_ativo = p
                        break
            
            if not pedido_ativo:
                pedidos_do_cantor = [
                    p for p in pendentes_geral 
                    if str(p.get("cantor", "")).strip().lower() == cantor_atual.strip().lower()
                ]
                if pedidos_do_cantor:
                    pedido_ativo = pedidos_do_cantor[0]
                    st.session_state["meu_pedido_timestamp"] = pedido_ativo.get("timestamp")

            lista_itens_fila = []
            for i, item in enumerate(pendentes_geral):
                pos_num = i + 1
                pos_str = f"{pos_num}º"
                nome_c = item.get('cantor', 'Cantor')
                lista_itens_fila.append(f'<span class="fila-pos">{pos_str}</span> — <span class="fila-cantor">{nome_c}</span>')

            texto_base = " &nbsp;&nbsp;&bull;&nbsp;&nbsp; ".join(lista_itens_fila) if lista_itens_fila else "A fila está vazia no momento."
            texto_fila_resumo = f"{texto_base} &nbsp;&nbsp;&bull;&nbsp;&nbsp; {texto_base}"

            html_rodape_fila = f"""
                <div class="ff-fila-wrapper">
                    <div class="ff-fila-header-title">🎶 Fila de Espera Atual 🎶</div>
                    <div class="ff-marquee-container">
                        <div class="ff-marquee-content" style="font-size: 11px;">{texto_fila_resumo}</div>
                    </div>
                </div>
            """
            
            if pedido_ativo:
                posicao_real = -1
                for idx, p in enumerate(pendentes_geral):
                    if str(p.get("timestamp", "")) == str(pedido_ativo.get("timestamp", "")):
                        posicao_real = idx + 1
                        break
                
                if posicao_real == -1:
                    posicao_real = 1
                    
                musicas_acima = posicao_real - 1 if posicao_real > 0 else 0
                musica_nome_atv = pedido_ativo.get('musica', '')
                
                cantor_acima = "Ninguém"
                if posicao_real > 1 and len(pendentes_geral) >= (posicao_real - 1):
                    cantor_acima = pendentes_geral[posicao_real - 2].get('cantor', 'outro cantor')

                st.markdown(f"""
                    <div class="ff-card-status-centered">
                        <div class="ff-card-title-yellow">A SUA POSIÇÃO ACTUAL É</div>
                        <div class="ff-number-fixed">#{posicao_real}</div>
                        <div class="ff-card-subtitle" style="margin-top: 2px;">Título da Música que escolheu</div>
                        <div class="ff-card-main-text">🎵 {musica_nome_atv}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if musicas_acima > 0:
                    html_cartao_espera = f'<div class="ff-card-status-centered" style="border-color: rgba(231, 76, 60, 0.4);"><div class="ff-card-title-orange">AGUARDE A SUA VEZ</div><div class="ff-card-main-text" style="font-size: 13px; color: #f1c40f; margin-bottom: 2px;">Assim que cantar o cantor <b>{cantor_acima}</b> será a sua vez!</div><div class="ff-card-subtitle" style="font-size: 9px; margin-bottom: 4px;">({musicas_acima} músicas à sua frente)</div>{html_rodape_fila}</div>'
                    st.markdown(html_cartao_espera, unsafe_allow_html=True)
                else:
                    html_cartao_vez = f'<div class="ff-card-status-centered" style="border-color: rgba(46, 204, 113, 0.4);"><div class="ff-card-title-green">É A SUA VEZ DE CANTAR!</div><div class="ff-card-main-text" style="color: #2ecc71; margin-bottom: 4px;">Prepare-se para subir ao palco agora.</div>{html_rodape_fila}</div>'
                    st.markdown(html_cartao_vez, unsafe_allow_html=True)
            else:
                if st.session_state["meu_pedido_timestamp"] is not None:
                    st.success("🎉 O seu pedido anterior já foi interpretado ou retirado da fila!")
                    st.session_state["meu_pedido_timestamp"] = None
                    st.rerun()
                    
                total_fila_geral = len(pendentes_geral)
                st.info(f"ℹ️ Existem **{total_fila_geral} músicas** na fila de espera global.")
                
                st.markdown(html_rodape_fila, unsafe_allow_html=True)
                
                st.markdown('<div class="ff-action-box">', unsafe_allow_html=True)
                st.markdown("##### 🔍 PEDIR MÚSICA")
                with st.form("form_cliente", clear_on_submit=True):
                    musica_inicial = st.text_input("Nome da música ou artista:", placeholder="Ex: Bruno Mars, Matias Damásio...")
                    submitted_inicial = st.form_submit_button("Pedir Música")
                    
                    if submitted_inicial:
                        if musica_inicial.strip():
                            novo_ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            dados_novo_pedido = {
                                "cantor": cantor_atual,
                                "musica": musica_inicial.strip(),
                                "token_prestador": token_p,
                                "status": "pendente",
                                "timestamp": novo_ts
                            }
                            guardar_pedido_musica(dados_novo_pedido)
                            st.session_state["meu_pedido_timestamp"] = novo_ts
                            st.success("Pedido adicionado à fila com sucesso!")
                            st.rerun()
                        else:
                            st.error("Por favor, preencha o nome da música ou artista.")
                st.markdown('</div>', unsafe_allow_html=True)

        renderizar_painel_fila(cantor, token_prestador)
            
        st.markdown('<div class="ff-how-it-works-title">🎧 COMO FUNCIONA?</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="ff-steps-container">
                <div class="ff-step-card">
                    <div class="ff-step-number">1</div>
                    <h5>Escolha</h5>
                    <p>Digite o nome da música.</p>
                </div>
                <div class="ff-step-card">
                    <div class="ff-step-number">2</div>
                    <h5>Aguarde</h5>
                    <p>Acompanhe a sua posição.</p>
                </div>
                <div class="ff-step-card">
                    <div class="ff-step-number">3</div>
                    <h5>Cante</h5>
                    <p>Dê o seu show na hora!</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Alterar Nome / Sair"):
            st.session_state["cliente_nome"] = ""
            st.session_state["meu_pedido_timestamp"] = None
            st.rerun()

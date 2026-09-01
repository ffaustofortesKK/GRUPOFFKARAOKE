import streamlit as st
import time
from datetime import datetime
from db import guardar_prestador, obter_prestadores, obter_pedidos_musicas

def render():
    if "pedido_submetido" not in st.session_state:
        st.session_state.pedido_submetido = False
        st.session_state.token_prestador = None
        st.session_state.estado_pedido = "pendente"
    if "aprovado" not in st.session_state:
        st.session_state.aprovado = False

    prestador_atual = None
    if st.session_state.pedido_submetido and st.session_state.token_prestador:
        prestadores = obter_prestadores()
        prestador_atual = next((p for p in prestadores if p.get("token") == st.session_state.token_prestador), None)
        
        if prestador_atual:
            status_atual = prestador_atual.get("status_str", "pendente")
            st.session_state.estado_pedido = status_atual
            
            if status_atual == "aprovado":
                st.session_state.aprovado = True

    # 1. SE ESTIVER APROVADO: Painel Operacional
    if st.session_state.get("aprovado", False) or st.session_state.get("estado_pedido") == "aprovado":
        
        token_ativo = st.session_state.get("token_prestador", "")
        try:
            base_url = st.context.headers.get("Host", "")
            if base_url:
                protocol = "http" if "localhost" in base_url or "127.0.0.1" in base_url else "https"
                url_cliente = f"{protocol}://{base_url}/?page=cliente&token={token_ativo}"
                url_tela = f"{protocol}://{base_url}/?page=tela&token={token_ativo}"
            else:
                raise Exception()
        except Exception:
            url_cliente = f"https://grupoffkaraoke.streamlit.app/?page=cliente&token={token_ativo}"
            url_tela = f"https://grupoffkaraoke.streamlit.app/?page=tela&token={token_ativo}"

        st.markdown("""
            <style>
                .box-container {
                    background-color: #0c0c0e;
                    border: 2px solid #eab308;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 16px;
                    box-shadow: 0 0 10px rgba(234, 179, 8, 0.15);
                }
                .box-title {
                    color: #eab308;
                    font-weight: bold;
                    font-size: 15px;
                    margin-bottom: 10px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .box-content {
                    color: #d4d4d8;
                    font-size: 14px;
                }
                div[data-testid="column"] {
                    padding: 0px !important;
                }
                .stButton button {
                    min-height: 26px !important;
                    height: 28px !important;
                    padding: 0px 6px !important;
                    font-size: 12px !important;
                }
            </style>
        """, unsafe_allow_html=True)

        col_logo, col_top_info, col_top_btn = st.columns([1.2, 4.3, 1.2])
        with col_logo:
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 10px; margin-top: 5px;">
                    <span style="font-size: 32px;">⭐</span>
                    <div>
                        <span style="color: #eab308; font-weight: bold; font-size: 18px; display: block; line-height: 1;">FF KARAOKE</span>
                        <span style="color: #a1a1aa; font-size: 9px; letter-spacing: 0.5px;">FAZ A VOZ, FAZ A FESTA!</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_top_info:
            nome_prestador = prestador_atual.get('nome', '') if prestador_atual else ''
            st.markdown(f"<div style='text-align: center;'><span style='color: #eab308; font-size: 40px; font-weight: 900; letter-spacing: 2px;'>PRESTADOR: {nome_prestador.upper()}</span></div>", unsafe_allow_html=True)
            
        with col_top_btn:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("🚪 Sair / Terminar", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        col_esq, col_dir = st.columns([1.3, 1])

        with col_esq:
            @st.fragment(run_every=3)
            def renderizar_a_tocar():
                nonlocal prestador_atual
                if st.session_state.token_prestador:
                    prestadores = obter_prestadores()
                    prestador_atual = next((p for p in prestadores if p.get("token") == st.session_state.token_prestador), None)

                segundos_restantes = 7200  
                if prestador_atual:
                    segundos_contrato_inicial = prestador_atual.get("segundos_restantes", 7200)
                    data_pedido_str = prestador_atual.get("data_pedido", "")
                    
                    try:
                        dt_pedido = datetime.strptime(data_pedido_str, "%d/%m/%Y %H:%M")
                        decorrido = int((datetime.now() - dt_pedido).total_seconds())
                        segundos_restantes = max(0, segundos_contrato_inicial - decorrido)
                    except Exception:
                        segundos_restantes = segundos_contrato_inicial

                horas = segundos_restantes // 3600
                minutos = (segundos_restantes % 3600) // 60
                segundos = segundos_restantes % 60
                tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

                st.markdown(f"""
                    <div class="box-container">
                        <div class="box-title">
                            <span>▶ A TOCAR AGORA</span>
                            <span style="color: #eab308; font-family: monospace; font-size: 16px;">⏳ {tempo_formatado}</span>
                        </div>
                        <div class="box-content">
                            <p style="margin-bottom: 6px; font-weight: 500;">Nada em reprodução.</p>
                            <p style="color: #a1a1aa; font-size: 13px; margin-bottom: 15px;">A música é reproduzida apenas no ecrã de TV.</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            renderizar_a_tocar()
            
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("▶ Tocar primeiro da fila", use_container_width=True):
                    st.toast("A tocar o primeiro da fila...")
            with b2:
                if st.button("⏸ Parar", use_container_width=True):
                    st.toast("Reprodução parada.")
            with b3:
                if st.button("⏭ Próxima", use_container_width=True):
                    st.toast("A avançar para a próxima música...")

            st.markdown("<br>", unsafe_allow_html=True)

            # --- CAIXA 2: FILA DE PEDIDOS COM GESTÃO EM SESSÃO ---
            if "fila_local_cache" not in st.session_state:
                st.session_state.fila_local_cache = None

            @st.fragment(run_every=3)
            def renderizar_fila_pedidos():
                try:
                    todos_pedidos = obter_pedidos_musicas() or []
                except Exception:
                    todos_pedidos = []

                token_ativo = str(st.session_state.get("token_prestador", ""))
                
                lista_pedidos = []
                for p in todos_pedidos:
                    if p.get("status", "pendente") == "pendente":
                        p_token = str(p.get("token_prestador", ""))
                        if not p_token or p_token == "None" or p_token == token_ativo:
                            lista_pedidos.append(p)

                total_pedidos = len(lista_pedidos)
                
                st.markdown(f"""
                    <div class="box-container">
                        <div class="box-title">
                            <span>📄 FILA DE PEDIDOS ({total_pedidos})</span>
                        </div>
                        <div class="box-content">
                """, unsafe_allow_html=True)

                if total_pedidos > 0:
                    for idx, pedido in enumerate(lista_pedidos):
                        musica = pedido.get('musica', 'Música Desconhecida')
                        cantor = pedido.get('cantor', 'Convidado')

                        col_txt, col_botoes = st.columns([6, 2])
                        
                        with col_txt:
                            st.markdown(f"""
                                <div style="padding-top: 4px; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                    <b style="color: #eab308;">{idx+1}º</b> <b>{musica}</b> — <span style="color: #a1a1aa;">{cantor}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with col_botoes:
                            b_up, b_down, b_del = st.columns(3)
                            with b_up:
                                if idx > 0:
                                    if st.button("⬆️", key=f"up_{idx}", help="Subir"):
                                        lista_pedidos[idx], lista_pedidos[idx-1] = lista_pedidos[idx-1], lista_pedidos[idx]
                                        st.rerun()
                            with b_down:
                                if idx < total_pedidos - 1:
                                    if st.button("⬇️", key=f"down_{idx}", help="Descer"):
                                        lista_pedidos[idx], lista_pedidos[idx+1] = lista_pedidos[idx+1], lista_pedidos[idx]
                                        st.rerun()
                            with b_del:
                                if st.button("❌", key=f"del_{idx}", help="Remover"):
                                    lista_pedidos.pop(idx)
                                    st.toast(f"Removido com sucesso!")
                                    st.rerun()

                        if idx < total_pedidos - 1:
                            st.markdown("<hr style='margin: 4px 0px; border: none; border-top: 1px solid #27272a;'>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #a1a1aa; margin: 0;'>Sem pedidos em espera.</p>", unsafe_allow_html=True)

                st.markdown("""
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            renderizar_fila_pedidos()

        with col_dir:
            url_cliente = f"https://grupoffkaraoke.streamlit.app/?page=cliente&token={token_ativo}"
            url_tela = f"https://grupoffkaraoke.streamlit.app/?page=tela&token={token_ativo}"

            st.markdown(f"""
                <div class="box-container">
                    <div class="box-title">
                        <span>🔗 LINKS E QR CODE</span>
                    </div>
                    <div class="box-content" style="font-size: 11px; word-break: break-all; margin-bottom: 12px;">
                        <span style="color: #eab308; font-weight: bold;">Cliente:</span><br>{url_cliente}<br><br>
                        <span style="color: #3b82f6; font-weight: bold;">TV:</span><br>{url_tela}
                    </div>
                    <div style="text-align: center; background: #ffffff; padding: 10px; border-radius: 6px; margin-bottom: 12px;">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=170x170&data={url_cliente}" width="170" />
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_bt_tv, col_bt_cli = st.columns(2)
            with col_bt_tv: 
                st.markdown(f'<a href="{url_tela}" target="_blank"><button style="width: 100%; background-color: #18181b; color: #ffffff; border: 1px solid #eab308; padding: 8px; border-radius: 6px; cursor: pointer; font-size: 13px;">🖥️ Abrir TV</button></a>', unsafe_allow_html=True)
            with col_bt_cli:
                st.markdown(f'<a href="{url_cliente}" target="_blank"><button style="width: 100%; background-color: #18181b; color: #ffffff; border: 1px solid #eab308; padding: 8px; border-radius: 6px; cursor: pointer; font-size: 13px;">📱 Abrir cliente</button></a>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            videos_disponiveis = {
                "- Sem vídeo de fundo -": "",
                "Vídeo 1 (Oficial)": "https://youtu.be/cQ4MD7gOBmc?si=5wzaxysiHSEwn9QT",
                "Vídeo 2": "https://youtu.be/H_aniWehIYY?si=e9WzMGyFSy7PdrAj",
                "Vídeo 3": "https://youtu.be/sGGlQ9yJQNg?si=LVeN5zjZ153uksLW",
                "Vídeo 4": "https://youtu.be/sGGlQ9yJQNg?si=ZxjJ34_4Z13MUL-g",
                "Vídeo 5": "https://youtu.be/TmayKMV0bJY?si=Zb99BwXuFyDDJ-tN"
            }

            st.markdown("""
                <div class="box-container" style="margin-bottom: 10px;">
                    <div class="box-title" style="margin-bottom: 0;">
                        <span>🎬 VÍDEO DE FUNDO DA TV</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            video_escolhido = st.selectbox("Selecione o vídeo de fundo:", list(videos_disponiveis.keys()), label_visibility="collapsed")
            url_video_selecionado = videos_disponiveis[video_escolhido]

            if st.button("▶ Iniciar Vídeo Clipe Tela", use_container_width=True, type="primary"):
                if st.session_state.token_prestador:
                    prestadores = obter_prestadores()
                    for p in prestadores:
                        if p.get("token") == st.session_state.token_prestador:
                            p["video_fundo"] = url_video_selecionado
                            guardar_prestador(p)
                    st.success("Vídeo clipe de tela iniciado/guardado com sucesso!")
        return

    # 2. SE ESTIVER RECUSADO
    if st.session_state.pedido_submetido and st.session_state.estado_pedido == "recusado":
        st.markdown("""
            <div style="background-color: #0f0f11; border: 2px solid #ef4444; padding: 40px 20px; text-align: center; border-radius: 12px; margin-top: 20px;">
                <div style="font-size: 50px; margin-bottom: 15px;">❌</div>
                <h2 style="color: #ef4444; font-weight: bold; margin-bottom: 15px;">Pedido Recusado</h2>
                <p style="color: #d4d4d8; font-size: 16px; max-width: 500px; margin: 0 auto 20px auto;">
                    Infelizmente o seu pedido de acesso foi recusado pelo Administrador.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Tentar Novamente / Novo Registo", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()
        return

    # 3. SE ESTIVER PENDENTE
    if st.session_state.pedido_submetido:
        st.markdown("""
            <style>
                @keyframes girarHorario { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                @keyframes girarAntiHorario { 0% { transform: rotate(0deg); } 100% { transform: rotate(-360deg); } }
                .circulo-externo {
                    width: 140px; height: 140px; border-radius: 50%; border: 2px dashed #ef4444;
                    display: flex; justify-content: center; align-items: center; position: relative;
                    animation: girarHorario 10s linear infinite;
                }
                .circulo-interno {
                    width: 100px; height: 100px; border-radius: 50%; border: 2px dashed #eab308;
                    display: flex; justify-content: center; align-items: center;
                    animation: girarAntiHorario 8s linear infinite;
                }
            </style>
            
            <div style="background-color: #0f0f11; padding: 40px 20px; text-align: center; border-radius: 12px; margin-top: 20px;">
                <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 25px;">
                    <div class="circulo-externo">
                        <div class="circulo-interno">
                            <span style="font-size: 42px;">🎤</span>
                        </div>
                    </div>
                </div>
                <h2 style="color: #ffffff; font-weight: bold; margin-bottom: 15px;">Aguardando Aprovação</h2>
                <p style="color: #d4d4d8; font-size: 16px; max-width: 500px; margin: 0 auto 10px auto;">
                    O seu registo foi enviado com sucesso e está a aguardar a validação do Administrador.
                </p>
                <p style="color: #a1a1aa; font-size: 14px;">
                    Esta página abrirá o seu painel automaticamente assim que o Administrador aprovar.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(3)
        st.rerun()
        return

    # 4. TELA INICIAL: NOVO REGISTO OU LOGIN
    st.markdown("""
        <style>
            .prestador-wrapper {
                background: linear-gradient(180deg, rgba(15, 15, 20, 0.95) 0%, rgba(10, 10, 15, 0.98) 100%);
                border: 2px solid #8b5cf6;
                border-radius: 14px;
                padding: 30px;
                box-shadow: 0 0 25px rgba(139, 92, 246, 0.25);
                max-width: 850px;
                margin: 0 auto;
            }
            .prestador-header {
                text-align: center;
                margin-bottom: 25px;
            }
            .prestador-title {
                color: #eab308;
                font-size: 28px;
                font-weight: 800;
                letter-spacing: 1px;
                margin-top: 10px;
                margin-bottom: 5px;
            }
            .prestador-subtitle {
                color: #a1a1aa;
                font-size: 14px;
            }
            .top-icon-badge {
                width: 60px;
                height: 60px;
                border: 2px solid #eab308;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
                background: #18181b;
                box-shadow: 0 0 15px rgba(234, 179, 8, 0.3);
            }
            .opcao-box {
                background-color: #121217;
                border: 1px solid #3f3f46;
                border-radius: 8px;
                padding: 12px 18px;
                margin-bottom: 20px;
                color: #eab308;
                font-weight: 600;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .linha-dourada {
                width: 60px;
                height: 3px;
                background-color: #eab308;
                margin: 8px auto 20px auto;
                border-radius: 2px;
            }
            .footer-features {
                display: flex;
                justify-content: space-between;
                gap: 15px;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #27272a;
            }
            .feature-card {
                background: #121216;
                border: 1px solid #27272a;
                border-radius: 8px;
                padding: 15px;
                flex: 1;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            }
            .feature-icon {
                width: 38px;
                height: 38px;
                border-radius: 50%;
                border: 1px solid #8b5cf6;
                background: #181824;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }
        </style>

        <div class="prestador-wrapper">
            <div class="prestador-header">
                <div class="top-icon-badge">
                    <span style="font-size: 26px;">👤</span>
                </div>
                <div class="prestador-title">ÁREA DO PRESTADOR</div>
                <div class="linha-dourada"></div>
                <div class="prestador-subtitle">Faça o seu registo de acesso ou entre com os seus dados se já tiver uma sessão ativa.</div>
            </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="opcao-box">
            <span>👥</span> ESCOLHA A OPÇÃO:
        </div>
    """, unsafe_allow_html=True)

    modo_acesso = st.radio("Escolha a opção:", ["Novo Registo", "Já estou online / Entrar com Nome e Telefone"], horizontal=True, label_visibility="collapsed")

    if modo_acesso == "Novo Registo":
        with st.form("form_registo_prestador"):
            nome = st.text_input("Nome Completo", placeholder="Digite o seu nome completo")
            telefone = st.text_input("Telemóvel / Telefone", placeholder="Digite o seu número de telefone")
            estabelecimento = st.text_input("Estabelecimento", placeholder="Ex: Bar do Zé, Restaurante Bom Sabor, etc.")
            contrato = st.selectbox("Escolha o Contrato", [
                "1 Hora - 12.000,00 Kwanzaas", 
                "2 Horas - 17.000,00 Kwanzaas",
                "3 Horas - 20.000,00 Kwanzaas"
            ])
            
            submitted = st.form_submit_button("🚀 SUBMETER PEDIDO", use_container_width=True)
            
            if submitted:
                if nome.strip() and telefone.strip():
                    token_gerado = f"token_{int(time.time())}"
                    segundos_contrato = 3600 if "1 Hora" in contrato else (7200 if "2 Horas" in contrato else 10800)

                    novo_prestador = {
                        "nome": nome.strip(),
                        "telefone": telefone.strip(),
                        "estabelecimento": estabelecimento.strip(),
                        "plano": contrato,
                        "contrato": contrato,
                        "status_str": "pendente",
                        "approved": False,
                        "token": token_gerado,
                        "segundos_restantes": segundos_contrato,
                        "data_pedido": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "video_fundo": ""
                    }
                    
                    guardar_prestador(novo_prestador)
                    
                    st.session_state.pedido_submetido = True
                    st.session_state.token_prestador = token_gerado
                    st.session_state.estado_pedido = "pendente"
                    st.session_state.aprovado = False
                    st.rerun()
                else:
                    st.error("Por favor, preencha pelo menos o Nome Completo e o Telefone.")
    else:
        with st.form("form_login_prestador"):
            st.markdown("<h4 style='color: #eab308; margin-bottom: 15px;'>Entrar com Sessão Ativa</h4>", unsafe_allow_html=True)
            login_nome = st.text_input("Nome Registado", placeholder="Digite o seu nome registado")
            login_telefone = st.text_input("Telemóvel / Telefone Registado", placeholder="Digite o seu telefone")
            
            btn_entrar = st.form_submit_button("🔑 ACEDER AO PAINEL", use_container_width=True)
            
            if btn_entrar:
                if login_nome.strip() and login_telefone.strip():
                    prestadores = obter_prestadores()
                    prestador_encontrado = next(
                        (p for p in prestadores if p.get("nome", "").strip().lower() == login_nome.strip().lower() and p.get("telefone", "").strip() == login_telefone.strip()), 
                        None
                    )
                    
                    if prestador_encontrado:
                        st.session_state.pedido_submetido = True
                        st.session_state.token_prestador = prestador_encontrado.get("token")
                        status_db = prestador_encontrado.get("status_str", "pendente")
                        st.session_state.estado_pedido = status_db
                        if status_db == "aprovado":
                            st.session_state.aprovado = True
                        st.success("Sessão encontrada com sucesso! A entrar...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Não foi encontrado nenhum registo ativo com este Nome e Telemóvel.")
                else:
                    st.error("Por favor, insira o seu Nome e Telemóvel para entrar.")

    st.markdown("""
        <div class="footer-features">
            <div class="feature-card">
                <div class="feature-icon">🎧</div>
                <div>
                    <div style="color: #eab308; font-weight: bold; font-size: 13px; margin-bottom: 2px;">RÁPIDO E FÁCIL</div>
                    <div style="color: #a1a1aa; font-size: 11px; line-height: 1.3;">Registe-se em poucos passos e comece já.</div>
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <div>
                    <div style="color: #eab308; font-weight: bold; font-size: 13px; margin-bottom: 2px;">SEGURO</div>
                    <div style="color: #a1a1aa; font-size: 11px; line-height: 1.3;">Os seus dados estão protegidos com total segurança.</div>
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⭐</div>
                <div>
                    <div style="color: #eab308; font-weight: bold; font-size: 13px; margin-bottom: 2px;">FAZ A VOZ, FAZ A FESTA!</div>
                    <div style="color: #a1a1aa; font-size: 11px; line-height: 1.3;">Junte-se à comunidade do FF KARAOKE e brilhe!</div>
                </div>
            </div>
        </div>
        </div>
    """, unsafe_allow_html=True)

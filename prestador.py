from datetime import datetime
import time
import streamlit as st
from db import guardar_prestador, obter_pedidos_musicas, obter_prestadores, apagar_pedido_musica

LINK_LOGO = "https://cdn.phototourl.com/free/2026-07-03-793a0f18-6143-44c8-b56e-e44af828c30c.png"

def render():
    # 1. INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO
    if "pedido_submetido" not in st.session_state:
        st.session_state.pedido_submetido = False
    if "token_prestador" not in st.session_state:
        st.session_state.token_prestador = None
    if "estado_pedido" not in st.session_state:
        st.session_state.estado_pedido = "pendente"
    if "aprovado" not in st.session_state:
        st.session_state.aprovado = False

    # 2. SINCRONIZAÇÃO DE DADOS NA BASE DE DADOS
    prestador_atual = None
    if st.session_state.token_prestador:
        prestadores = obter_prestadores() or []
        prestador_atual = next(
            (p for p in prestadores if p.get("token") == st.session_state.token_prestador),
            None,
        )
        if prestador_atual:
            status_atual = prestador_atual.get("status_str", "pendente")
            st.session_state.estado_pedido = status_atual
            if status_atual == "aprovado":
                st.session_state.aprovado = True
                st.session_state.pedido_submetido = True
            elif status_atual == "pendente":
                st.session_state.pedido_submetido = True
        else:
            st.session_state.token_prestador = None
            st.session_state.pedido_submetido = False
            st.session_state.aprovado = False
            st.session_state.estado_pedido = "pendente"

    # =========================================================================
    # 3. SE ESTIVER PENDENTE: BLOQUEIO COM ATUALIZAÇÃO AUTOMÁTICA (POLLING)
    # =========================================================================
    if st.session_state.pedido_submetido and st.session_state.estado_pedido == "pendente":
        
        @st.fragment(run_every=3)
        def verificar_aprovacao_em_segundo_plano():
            if st.session_state.token_prestador:
                prestadores_db = obter_prestadores() or []
                p_atual = next((p for p in prestadores_db if p.get("token") == st.session_state.token_prestador), None)
                if p_atual and p_atual.get("status_str") == "aprovado":
                    st.session_state.aprovado = True
                    st.session_state.estado_pedido = "aprovado"
                    st.rerun()

        verificar_aprovacao_em_segundo_plano()

        st.markdown(
            """
            <style>
                .stApp {
                    background-color: #000000 !important;
                }
                header[data-testid="stHeader"] {
                    background-color: transparent !important;
                }
                .block-container {
                    max-width: 600px !important;
                    padding-top: 5rem !important;
                    background-color: #000000 !important;
                }
            </style>
            <div style="background-color: #050507; border: 1px solid #3b2c60; padding: 25px; text-align: center; border-radius: 8px; margin: auto;">
                <div style="font-size: 32px; margin-bottom: 10px;">⏳</div>
                <h3 style="color: #ffffff; font-size: 18px; margin-bottom: 8px;">Aguardando Aprovação</h3>
                <p style="color: #d4d4d8; font-size: 12px; margin-bottom: 15px;">O seu registo está a aguardar validação do Administrador. A tela abrirá automaticamente assim que for aprovado.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        if st.button("🚪 Terminar Sessão / Voltar", use_container_width=True):
            st.session_state.pedido_submetido = False
            st.session_state.token_prestador = None
            st.session_state.estado_pedido = "pendente"
            st.session_state.aprovado = False
            st.rerun()
            
        return

    # ==========================================
    # 4. SE ESTIVER APROVADO: Painel Operacional
    # ==========================================
    if st.session_state.aprovado or st.session_state.estado_pedido == "aprovado":
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

        st.markdown(
            """
            <style>
                .stApp {
                    background-color: #000000 !important;
                }
                header[data-testid="stHeader"] {
                    background-color: transparent !important;
                }
                .block-container {
                    max-width: 1400px !important;
                    min-height: 98vh !important;
                    padding-top: 0.1rem !important;
                    padding-bottom: 0.5rem !important;
                    padding-left: 0.6rem !important;
                    padding-right: 0.6rem !important;
                    background-color: #000000 !important;
                    border-radius: 6px;
                    border: 1px solid rgba(138, 43, 226, 0.25);
                    margin-top: 0rem;
                    margin-bottom: 0rem;
                }
                .box-container {
                    background-color: #050507;
                    border: 1px solid #27272a;
                    border-radius: 4px;
                    padding: 10px 12px;
                    margin-bottom: 8px;
                }
                .box-title {
                    color: #eab308;
                    font-weight: bold;
                    font-size: 11px;
                    margin-bottom: 4px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                div[data-testid="column"] {
                    padding: 0px !important;
                }
                .stButton button {
                    background-color: #0d0d10 !important;
                    color: #ffffff !important;
                    border: 1px solid #27272a !important;
                    border-radius: 3px !important;
                    min-height: 31px !important;
                    height: 33px !important;
                    font-size: 11px !important;
                    font-weight: 500;
                }
                .stButton button:hover {
                    border-color: #eab308 !important;
                    color: #eab308 !important;
                }
                div[data-testid="column"] button {
                    background-color: #ffffff !important;
                    color: #000000 !important;
                    border: 1px solid #d4d4d8 !important;
                    font-size: 10px !important;
                    font-weight: bold !important;
                    min-height: 28px !important;
                    height: 30px !important;
                }
                div[data-testid="column"] button:hover {
                    background-color: #f4f4f5 !important;
                    border-color: #eab308 !important;
                    color: #000000 !important;
                }
                @keyframes equalizer {
                    0% { height: 2px; }
                    50% { height: 16px; }
                    100% { height: 2px; }
                }
                .eq-bar {
                    background-color: #eab308;
                    width: 3px;
                    border-radius: 2px;
                    animation: equalizer 1.2s infinite ease-in-out;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        
        col_lateral, col_principal = st.columns([1, 2.9])

        with col_lateral:
            @st.fragment(run_every=3)
            def renderizar_relogio_topo():
                nonlocal prestador_atual
                if st.session_state.token_prestador:
                    prestadores = obter_prestadores() or []
                    prestador_atual = next(
                        (p for p in prestadores if p.get("token") == st.session_state.token_prestador),
                        None,
                    )

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

                st.markdown(
                    f"""
                    <div style="background-color: #0d0d10; border: 1px solid #eab308; padding: 6px 8px; border-radius: 4px; text-align: center; margin-bottom: 6px;">
                        <div style="color: #eab308; font-size: 9px; font-weight: bold;">⏳ TEMPO RESTANTE</div>
                        <div style="color: #ffffff; font-family: monospace; font-size: 17px; font-weight: 900;">{tempo_formatado}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            renderizar_relogio_topo()

            nome_prestador_txt = prestador_atual.get("nome", "Prestador") if prestador_atual else "Prestador"
            estabelecimento_txt = prestador_atual.get("estabelecimento", "") if prestador_atual else ""
            video_fundo_atual = prestador_atual.get("video_fundo", "") if prestador_atual else ""

            st.markdown(
                f"""
                <div style="background-color: #0d0d10; border: 1px solid #8b5cf6; padding: 10px 10px; border-radius: 4px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 24px;">🎙️</span>
                        <div>
                            <div style="color: #c084fc; font-size: 9px; font-weight: bold;">PRESTADOR</div>
                            <div style="color: #ffffff; font-size: 24px; font-weight: bold; line-height: 1.1;">{nome_prestador_txt}</div>
                            <div style="color: #a1a1aa; font-size: 10px;">{estabelecimento_txt}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # LOGOTIPO
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 5px; margin-bottom: 6px;">
                    <img src="{LINK_LOGO}" style="max-width: 100%; width: 140px; border-radius: 4px;" />
                </div>
                """,
                unsafe_allow_html=True,
            )

          # SECÇÃO DE CONFIGURAÇÃO DO VÍDEO CLIPE NO PAINEL LATERAL
            with st.container():
                st.markdown('<div style="color: #c084fc; font-size: 10px; font-weight: bold; margin-bottom: 3px;">🎬 VÍDEO CLIPE DE FUNDO (TV)</div>', unsafe_allow_html=True)
                novo_video_fundo = st.text_input("Vídeo Clipe de Fundo", value=video_fundo_atual, placeholder="Cole o link do vídeo...", label_visibility="collapsed", key="input_atualizar_video")
                if st.button("💾 Guardar Vídeo", use_container_width=True):
                    if prestador_atual:
                        prestador_atual["video_fundo"] = novo_video_fundo.strip()
                        guardar_prestador(prestador_atual)
                        st.success("Vídeo de fundo atualizado com sucesso!")
                        time.sleep(0.5)
                        st.rerun()

            # NOTA INFORMATIVA ATUALIZADA
            st.markdown(
                """
                <div style="background-color: #0d0d10; border: 1px solid #3b2c60; padding: 10px 10px; border-radius: 4px; margin-top: 6px; margin-bottom: 6px; font-size: 10px; color: #d4d4d8; line-height: 1.3;">
                    <div style="color: #c084fc; font-weight: bold; margin-bottom: 3px;">📌 NOTAS IMPORTANTES:</div>
                    <div>• <b>Código QR:</b> O cliente deve apontar a câmara do telemóvel para fazer o seu registo e pedido de música.</div>
                    <div style="margin-top: 4px;">• <b>Tela (TV):</b> Abra o link/botão "TV" num projetor ou ecrã secundário para exibir o vídeo e a playlist.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()

        with col_principal:
            col_esq, col_dir = st.columns([1.4, 1])

            with col_esq:
                @st.fragment(run_every=3)
                def renderizar_a_tocar():
                    bars_html = ""
                    delays = [0.0, 0.2, 0.4, 0.1, 0.5, 0.3, 0.6, 0.15, 0.35, 0.45]
                    for i, d in enumerate(delays):
                        bars_html += f'<div class="eq-bar" style="animation-delay: {d}s; height: {8 + (i % 4) * 2}px;"></div>'

                    st.markdown(
                        f"""
                            <div class="box-container">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 30px; height: 30px; border: 1px solid #eab308; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                        <span style="font-size: 14px; color: #eab308;">🎵</span>
                                    </div>
                                    <div>
                                        <div style="color: #eab308; font-weight: bold; font-size: 10px;">▶ A TOCAR AGORA</div>
                                        <div style="color: #ffffff; font-size: 13px; font-weight: bold;">Nada em reprodução</div>
                                    </div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: flex-end; height: 18px; padding: 0 2px; margin-top: 6px;">
                                    {bars_html}
                                </div>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )
                renderizar_a_tocar()

                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("▶ Tocar", use_container_width=True, key="btn_tocar"):
                        st.toast("A tocar o primeiro...")
                with b2:
                    if st.button("⏸ Parar", use_container_width=True, key="btn_parar"):
                        st.toast("Parado.")
                with b3:
                    if st.button("⏭ Próxima", use_container_width=True, key="btn_proxima"):
                        st.toast("Próxima.")

                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

                @st.fragment(run_every=3)
                def renderizar_fila_pedidos():
                    try:
                        todos_pedidos = obter_pedidos_musicas() or []
                    except Exception:
                        todos_pedidos = []

                    token_ativo = str(st.session_state.get("token_prestador", ""))
                    lista_pedidos = [p for p in todos_pedidos if p.get("status", "pendente") == "pendente" and (str(p.get("token_prestador", "")) in ["", "None", token_ativo])]
                    total_pedidos = len(lista_pedidos)

                    # INÍCIO DA CAIXA CONTIDA (COM SCROLL INTERNO PARA NÃO SAIR DO RETÂNGULO)
                    st.markdown(
                        f"""
                            <div class="box-container" style="max-height: 380px; min-height: 250px; overflow-y: auto;">
                                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid #27272a; padding-bottom: 4px;">
                                    <span style="color: #c084fc; font-weight: bold; font-size: 11px;">👥 FILA DE PEDIDOS ({total_pedidos})</span>
                                </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if total_pedidos > 0:
                        for idx, pedido in enumerate(lista_pedidos):
                            musica = pedido.get("musica", "Desconhecida")
                            cantor = pedido.get("cantor", "Convidado")
                            pedido_id = pedido.get("id") or pedido.get("timestamp") or idx

                            # CADA ITEM É RENDERIZADO DENTRO DA CAIXA DA FILA DE PEDIDOS
                            cols_item = st.columns([2.4, 0.7, 0.7, 0.7])
                            with cols_item[0]:
                                st.markdown(
                                    f"""
                                    <div style="background-color: #0d0d10; border: 1px solid #27272a; border-radius: 3px; padding: 4px 6px; display: flex; align-items: center; gap: 6px; height: 32px; margin-bottom: 4px;">
                                        <span style="color: #c084fc; font-weight: bold; font-size: 10px;">{idx+1}º</span>
                                        <span style="color: #ffffff; font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{musica} — <span style="color: #a1a1aa;">{cantor}</span></span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            with cols_item[1]:
                                if idx > 0:
                                    if st.button("⬆", key=f"up_{pedido_id}", use_container_width=True):
                                        # Lógica para subir na ordem (trocar timestamps ou prioridade)
                                        pass
                            with cols_item[2]:
                                if idx < total_pedidos - 1:
                                    if st.button("⬇", key=f"down_{pedido_id}", use_container_width=True):
                                        # Lógica para descer na ordem
                                        pass
                            with cols_item[3]:
                                if st.button("✕", key=f"del_{pedido_id}", use_container_width=True):
                                    apagar_pedido_musica(pedido_id)
                                    st.rerun()
                    else:
                        st.markdown("<p style='color: #a1a1aa; margin: 8px 0; font-size: 11px;'>Sem pedidos na fila.</p>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                renderizar_fila_pedidos()
        
            with col_dir:
                st.markdown(
                    f"""
                        <div class="box-container">
                            <div class="box-title">
                                <span>🔗 LINKS E QR CODE</span>
                            </div>
                            <div class="box-content" style="font-size: 10px; word-break: break-all; margin-bottom: 8px;">
                                <span style="color: #eab308;">Cli:</span> {url_cliente}<br>
                                <span style="color: #3b82f6;">TV:</span> {url_tela}
                            </div>
                            <div style="text-align: center; background: #ffffff; padding: 6px; border-radius: 3px;">
                                <img src="https://api.qrserver.com/v1/create-qr-code/?size=115x115&data={url_cliente}" width="115" />
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_bt_tv, col_bt_cli = st.columns(2)
                with col_bt_tv:
                    st.markdown(f'<a href="{url_tela}" target="_blank"><button style="width: 100%; background-color: #0d0d10; color: #ffffff; border: 1px solid #27272a; padding: 6px; border-radius: 3px; font-size: 11px;">🖥️ TV</button></a>', unsafe_allow_html=True)
                with col_bt_cli:
                    st.markdown(f'<a href="{url_cliente}" target="_blank"><button style="width: 100%; background-color: #0d0d10; color: #ffffff; border: 1px solid #27272a; padding: 6px; border-radius: 3px; font-size: 11px;">📱 Cliente</button></a>', unsafe_allow_html=True)

        return

    # ==========================================
    # 5. SE ESTIVER RECUSADO
    # ==========================================
    if st.session_state.pedido_submetido and st.session_state.estado_pedido == "recusado":
        st.markdown(
            """
                <div style="background-color: #050507; border: 1px solid #ef4444; padding: 12px; text-align: center; border-radius: 4px; max-width: 400px; margin: 15px auto;">
                    <div style="font-size: 24px; margin-bottom: 2px;">❌</div>
                    <h3 style="color: #ef4444; font-size: 15px; margin-bottom: 2px;">Pedido Recusado</h3>
                    <p style="color: #d4d4d8; font-size: 11px; margin-bottom: 6px;">O seu pedido foi recusado pelo Administrador.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Tentar Novamente", use_container_width=True):
            st.session_state.pedido_submetido = False
            st.session_state.token_prestador = None
            st.session_state.estado_pedido = "pendente"
            st.session_state.aprovado = False
            st.rerun()
        return

    # =========================================================================
    # 🎨 6. TELA DE REGISTO / LOGIN
    # =========================================================================
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: #000000 !important;
            }}
            header[data-testid="stHeader"] {{
                background-color: transparent !important;
            }}
            .block-container {{
                max-width: 720px !important;
                padding-top: 0.1rem !important;
                padding-bottom: 0.2rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                background-color: #000000 !important;
                border-radius: 6px;
                border: 1px solid rgba(138, 43, 226, 0.25);
                margin-top: 0rem;
                margin-bottom: 0rem;
            }}
            div[data-baseweb="input"] input {{
                min-height: 20px !important;
                height: 22px !important;
                padding-top: 2px !important;
                padding-bottom: 2px !important;
                font-size: 11px !important;
            }}
            div[data-baseweb="base-input"] {{
                min-height: 22px !important;
            }}
            div[data-baseweb="select"] div {{
                min-height: 22px !important;
                font-size: 11px !important;
            }}
            div.row-widget.stRadio div[role="radiogroup"] label p {{
                color: #ffffff !important;
                font-weight: bold !important;
                font-size: 11px !important;
            }}
        </style>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
            <img src="{LINK_LOGO}" style="width: 130px; border-radius: 4px; display: block;" />
            <div style="width: 26px; height: 26px; background: rgba(234, 179, 8, 0.1); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: #eab308; font-size: 11px;">👤</div>
        </div>

        <div style="text-align: center; margin-bottom: 3px;">
            <h1 style="color: #eab308; font-size: 17px; font-weight: 900; margin-bottom: 1px;">ÁREA DO PRESTADOR</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div style="color: #eab308; font-size: 17px; font-weight: 900; margin-bottom: 2px;">Escolha a opção:</div>', unsafe_allow_html=True)
    modo_acesso = st.radio(
        "Escolha a opção:",
        ["Novo Registo", "Já estou online / Entrar com Nome e Telefone"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if modo_acesso == "Novo Registo":
        with st.form("form_registo_prestador_idêntico"):
            st.markdown(
                """
                <div style="background-color: #050507; border: 1px solid #3b2c60; border-radius: 6px; padding: 4px 8px;">
                """,
                unsafe_allow_html=True,
            )

            c_emo1, c_inp1 = st.columns([0.08, 0.92])
            with c_emo1:
                st.markdown('<div style="font-size: 18px; text-align: center; line-height: 1.5;">👤</div>', unsafe_allow_html=True)
            with c_inp1:
                nome = st.text_input("Nome Completo", placeholder="Digite o seu nome completo", label_visibility="collapsed")

            c_emo2, c_inp2 = st.columns([0.08, 0.92])
            with c_emo2:
                st.markdown('<div style="font-size: 18px; text-align: center; line-height: 1.5;">📞</div>', unsafe_allow_html=True)
            with c_inp2:
                telefone = st.text_input("Telemóvel / Telefone", placeholder="Digite o seu número de telefone", label_visibility="collapsed")

            c_emo3, c_inp3 = st.columns([0.08, 0.92])
            with c_emo3:
                st.markdown('<div style="font-size: 18px; text-align: center; line-height: 1.5;">📍</div>', unsafe_allow_html=True)
            with c_inp3:
                estabelecimento = st.text_input("Estabelecimento", placeholder="Ex: Bar do Zé, Restaurante Bom Sabor...", label_visibility="collapsed")

            c_emo4, c_inp4 = st.columns([0.08, 0.92])
            with c_emo4:
                st.markdown('<div style="font-size: 18px; text-align: center; line-height: 1.5;">📄</div>', unsafe_allow_html=True)
            with c_inp4:
                contrato = st.selectbox(
                    "Contrato",
                    [
                        "1 Hora - 12.000,00 Kwanzaas",
                        "2 Horas - 17.000,00 Kwanzaas",
                        "3 Horas - 20.000,00 Kwanzaas",
                    ],
                    label_visibility="collapsed",
                )

            c_emo5, c_inp5 = st.columns([0.08, 0.92])
            with c_emo5:
                st.markdown('<div style="font-size: 18px; text-align: center; line-height: 1.5;">🎬</div>', unsafe_allow_html=True)
            with c_inp5:
                video_fundo = st.text_input("Link do Vídeo Clipe de Fundo (Opcional)", placeholder="Cole aqui o link do vídeo de fundo para a TV...", label_visibility="collapsed")

            st.markdown("<div style='height: 1px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 SUBMETER PEDIDO", use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

            if submitted:
                if nome.strip() and telefone.strip():
                    token_gerado = f"token_{int(time.time())}"
                    segundos_contrato = (
                        3600
                        if "1 Hora" in contrato
                        else (7200 if "2 Horas" in contrato else 10800)
                    )

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
                        "video_fundo": video_fundo.strip() if 'video_fundo' in locals() else "",
                    }

                    guardar_prestador(novo_prestador)

                    st.session_state.pedido_submetido = True
                    st.session_state.token_prestador = token_gerado
                    st.session_state.estado_pedido = "pendente"
                    st.session_state.aprovado = False
                    st.rerun()
                else:
                    st.error("Preencha pelo menos o Nome e o Telefone.")
    else:
        with st.form("form_login_prestador_idêntico"):
            st.markdown(
                """
                <div style="background-color: #050507; border: 1px solid #3b2c60; border-radius: 6px; padding: 5px 8px;">
                """,
                unsafe_allow_html=True,
            )

            c_emo_l1, c_inp_l1 = st.columns([0.08, 0.92])
            with c_emo_l1:
                st.markdown('<div style="font-size: 18px; text-align: center; line-height: 1.5;">👤</div>', unsafe_allow_html=True)
            with c_inp_l1:
                login_nome = st.text_input("Nome", placeholder="Digite o seu nome cadastrado", label_visibility="collapsed")

            c_emo_l2, c_inp_l2 = st.columns([0.08, 0.92])
            with c_emo_l2:
                st.markdown('<div style="font-size: 18px; text-align: center; line-height: 1.5;">📞</div>', unsafe_allow_html=True)
            with c_inp_l2:
                login_telefone = st.text_input("Telemóvel / Telefone", placeholder="Digite o seu número de telefone", label_visibility="collapsed")

            st.markdown("<div style='height: 1px;'></div>", unsafe_allow_html=True)
            login_submitted = st.form_submit_button("🔓 ENTRAR", use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if login_submitted:
                if login_nome.strip() and login_telefone.strip():
                    prestadores = obter_prestadores() or []
                    prestador_encontrado = next(
                        (
                            p for p in prestadores
                            if p.get("nome", "").strip().lower() == login_nome.strip().lower()
                            and p.get("telefone", "").strip() == login_telefone.strip()
                        ),
                        None
                    )

                    if prestador_encontrado:
                        st.session_state.pedido_submetido = True
                        st.session_state.token_prestador = prestador_encontrado.get("token")
                        st.session_state.estado_pedido = prestador_encontrado.get("status_str", "pendente")
                        st.session_state.aprovado = (prestador_encontrado.get("status_str") == "aprovado")
                        st.rerun()
                    else:
                        st.error("Prestador não encontrado com estes dados ou ainda não registado.")
                else:
                    st.error("Preencha o Nome e o Telefone para entrar.")

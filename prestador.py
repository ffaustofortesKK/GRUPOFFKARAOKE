from datetime import datetime
import time
import streamlit as st
from db import guardar_prestador, obter_pedidos_musicas, obter_prestadores, guardar_pedido_musica, apagar_pedido_musica

LINK_LOGO = "https://cdn.phototourl.com/free/2026-07-03-793a0f18-6143-44c8-b56e-e44af828c30c.png"

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
        prestador_atual = next(
            (
                p
                for p in prestadores
                if p.get("token") == st.session_state.token_prestador
            ),
            None,
        )

        if prestador_atual:
            status_atual = prestador_atual.get("status_str", "pendente")
            st.session_state.estado_pedido = status_atual

            if status_atual == "aprovado":
                st.session_state.aprovado = True

    # 1. SE ESTIVER APROVADO: Painel Operacional Compacto
    if (
        st.session_state.get("aprovado", False)
        or st.session_state.get("estado_pedido") == "aprovado"
    ):
        token_ativo = st.session_state.get("token_prestador", "")
        try:
            base_url = st.context.headers.get("Host", "")
            if base_url:
                protocol = (
                    "http"
                    if "localhost" in base_url or "127.0.0.1" in base_url
                    else "https"
                )
                url_cliente = f"{protocol}://{base_url}/?page=cliente&token={token_ativo}"
                url_tela = f"{protocol}://{base_url}/?page=tela&token={token_ativo}"
            else:
                raise Exception()
        except Exception:
            url_cliente = (
                f"https://grupoffkaraoke.streamlit.app/?page=cliente&token={token_ativo}"
            )
            url_tela = (
                f"https://grupoffkaraoke.streamlit.app/?page=tela&token={token_ativo}"
            )

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
                    max-width: 920px !important;
                    padding-top: 0.5rem !important;
                    padding-bottom: 0.8rem !important;
                    padding-left: 1.2rem !important;
                    padding-right: 1.2rem !important;
                    background-color: #000000 !important;
                    border-radius: 12px;
                    border: 1px solid rgba(138, 43, 226, 0.25);
                    margin-top: 0.2rem;
                    margin-bottom: 0.2rem;
                }
                .box-container {
                    background-color: #050507;
                    border: 1px solid #27272a;
                    border-radius: 6px;
                    padding: 8px 12px;
                    margin-bottom: 6px;
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
                    border-radius: 4px !important;
                    min-height: 28px !important;
                    height: 30px !important;
                    font-size: 11px !important;
                    font-weight: 500;
                }
                .stButton button:hover {
                    border-color: #eab308 !important;
                    color: #eab308 !important;
                }
                @keyframes equalizer {
                    0% { height: 3px; }
                    50% { height: 16px; }
                    100% { height: 3px; }
                }
                .eq-bar {
                    background-color: #eab308;
                    width: 4px;
                    border-radius: 2px;
                    animation: equalizer 1.2s infinite ease-in-out;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        
        col_lateral, col_principal = st.columns([1, 2.8])

        with col_lateral:
            @st.fragment(run_every=3)
            def renderizar_relogio_topo():
                nonlocal prestador_atual
                if st.session_state.token_prestador:
                    prestadores = obter_prestadores()
                    prestador_atual = next(
                        (
                            p
                            for p in prestadores
                            if p.get("token") == st.session_state.token_prestador
                        ),
                        None,
                    )

                segundos_restantes = 7200
                if prestador_atual:
                    segundos_contrato_inicial = prestador_atual.get(
                        "segundos_restantes", 7200
                    )
                    data_pedido_str = prestador_atual.get("data_pedido", "")

                    try:
                        dt_pedido = datetime.strptime(data_pedido_str, "%d/%m/%Y %H:%M")
                        decorrido = int((datetime.now() - dt_pedido).total_seconds())
                        segundos_restantes = max(
                            0, segundos_contrato_inicial - decorrido
                        )
                    except Exception:
                        segundos_restantes = segundos_contrato_inicial
                
                horas = segundos_restantes // 3600
                minutos = (segundos_restantes % 3600) // 60
                segundos = segundos_restantes % 60
                tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

                st.markdown(
                    f"""
                    <div style="background-color: #0d0d10; border: 1px solid #eab308; padding: 4px 8px; border-radius: 6px; text-align: center; margin-bottom: 6px;">
                        <div style="color: #eab308; font-size: 8px; font-weight: bold; letter-spacing: 0.5px;">⏳ TEMPO RESTANTE</div>
                        <div style="color: #ffffff; font-family: monospace; font-size: 16px; font-weight: 900;">{tempo_formatado}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            renderizar_relogio_topo()

            nome_prestador_txt = prestador_atual.get("nome", "Prestador") if prestador_atual else "Prestador"
            estabelecimento_txt = prestador_atual.get("estabelecimento", "") if prestador_atual else ""

            st.markdown(
                f"""
                <div style="background-color: #0d0d10; border: 1px solid #8b5cf6; padding: 8px 10px; border-radius: 6px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 18px;">🎙️</span>
                        <div>
                            <div style="color: #c084fc; font-size: 9px; font-weight: bold;">PRESTADOR</div>
                            <div style="color: #ffffff; font-size: 14px; font-weight: bold; line-height: 1.1;">{nome_prestador_txt}</div>
                            <div style="color: #a1a1aa; font-size: 10px;">{estabelecimento_txt}</div>
                        </div>
                    </div>
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

            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 6px;">
                    <img src="{LINK_LOGO}" style="max-width: 100%; width: 180px; border-radius: 6px;" />
                </div>
                """,
                unsafe_allow_html=True,
            )

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
                                    <div style="width: 32px; height: 32px; border: 1px solid #eab308; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                        <span style="font-size: 14px; color: #eab308;">🎵</span>
                                    </div>
                                    <div>
                                        <div style="color: #eab308; font-weight: bold; font-size: 10px;">▶ A TOCAR AGORA</div>
                                        <div style="color: #ffffff; font-size: 13px; font-weight: bold;">Nada em reprodução</div>
                                    </div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: flex-end; height: 20px; padding: 0 2px; margin-top: 4px;">
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

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

                @st.fragment(run_every=3)
                def renderizar_fila_pedidos():
                    try:
                        todos_pedidos = obter_pedidos_musicas() or []
                    except Exception:
                        todos_pedidos = []

                    token_ativo = str(st.session_state.get("token_prestador", ""))
                    lista_pedidos = [p for p in todos_pedidos if p.get("status", "pendente") == "pendente" and (str(p.get("token_prestador", "")) in ["", "None", token_ativo])]
                    total_pedidos = len(lista_pedidos)

                    st.markdown(
                        f"""
                            <div class="box-container" style="max-height: 180px; overflow-y: auto;">
                                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; border-bottom: 1px solid #27272a; padding-bottom: 4px;">
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

                            col_info, col_botoes = st.columns([3, 1.2])
                            with col_info:
                                st.markdown(
                                    f"""
                                    <div style="background-color: #0d0d10; border: 1px solid #27272a; border-radius: 4px; padding: 4px 8px; display: flex; align-items: center; gap: 6px; height: 28px; margin-bottom: 4px;">
                                        <span style="color: #c084fc; font-weight: bold; font-size: 10px;">{idx+1}º</span>
                                        <span style="color: #ffffff; font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{musica} — <span style="color: #a1a1aa;">{cantor}</span></span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            with col_botoes:
                                b_up, b_down, b_del = st.columns(3)
                                with b_up:
                                    if idx > 0 and st.button("⬆️", key=f"up_{pedido_id}", use_container_width=True):
                                        pass
                                with b_down:
                                    if idx < total_pedidos - 1 and st.button("⬇️", key=f"down_{pedido_id}", use_container_width=True):
                                        pass
                                with b_del:
                                    if st.button("❌", key=f"del_{pedido_id}", use_container_width=True):
                                        apagar_pedido_musica(pedido_id)
                                        st.rerun()
                    else:
                        st.markdown("<p style='color: #a1a1aa; margin: 0; font-size: 11px;'>Sem pedidos na fila.</p>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                renderizar_fila_pedidos()
            
            with col_dir:
                st.markdown(
                    f"""
                        <div class="box-container">
                            <div class="box-title">
                                <span>🔗 LINKS E QR CODE</span>
                            </div>
                            <div class="box-content" style="font-size: 10px; word-break: break-all; margin-bottom: 6px;">
                                <span style="color: #eab308;">Cli:</span> {url_cliente}<br>
                                <span style="color: #3b82f6;">TV:</span> {url_tela}
                            </div>
                            <div style="text-align: center; background: #ffffff; padding: 4px; border-radius: 4px;">
                                <img src="https://api.qrserver.com/v1/create-qr-code/?size=90x90&data={url_cliente}" width="90" />
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_bt_tv, col_bt_cli = st.columns(2)
                with col_bt_tv:
                    st.markdown(f'<a href="{url_tela}" target="_blank"><button style="width: 100%; background-color: #0d0d10; color: #ffffff; border: 1px solid #27272a; padding: 4px; border-radius: 4px; font-size: 11px;">🖥️ TV</button></a>', unsafe_allow_html=True)
                with col_bt_cli:
                    st.markdown(f'<a href="{url_cliente}" target="_blank"><button style="width: 100%; background-color: #0d0d10; color: #ffffff; border: 1px solid #27272a; padding: 4px; border-radius: 4px; font-size: 11px;">📱 Cliente</button></a>', unsafe_allow_html=True)

                videos_disponiveis = {
                    "- Sem vídeo -": "",
                    "Vídeo 1": "https://youtu.be/cQ4MD7gOBmc?si=5wzaxysiHSEwn9QT",
                    "Vídeo 2": "https://youtu.be/H_aniWehIYY?si=e9WzMGyFSy7PdrAj",
                    "Vídeo 3": "https://youtu.be/sGGlQ9yJQNg?si=LVeN5zjZ153uksLW",
                }

                st.markdown('<div class="box-container" style="margin-top: 6px;"><div class="box-title"><span>🎬 VÍDEO TV</span></div>', unsafe_allow_html=True)
                video_escolhido = st.selectbox("Vídeo de fundo:", list(videos_disponiveis.keys()), label_visibility="collapsed")
                if st.button("▶ Atualizar", use_container_width=True, type="primary"):
                    if st.session_state.token_prestador:
                        prestadores = obter_prestadores()
                        for p in prestadores:
                            if p.get("token") == st.session_state.token_prestador:
                                p["video_fundo"] = videos_disponiveis[video_escolhido]
                                guardar_prestador(p)
                        st.success("Guardado!")
                st.markdown("</div>", unsafe_allow_html=True)

        return

    # 2. SE ESTIVER RECUSADO
    if st.session_state.pedido_submetido and st.session_state.estado_pedido == "recusado":
        st.markdown(
            """
                <div style="background-color: #050507; border: 1px solid #ef4444; padding: 15px; text-align: center; border-radius: 6px; max-width: 450px; margin: 20px auto;">
                    <div style="font-size: 28px; margin-bottom: 4px;">❌</div>
                    <h3 style="color: #ef4444; font-size: 16px; margin-bottom: 4px;">Pedido Recusado</h3>
                    <p style="color: #d4d4d8; font-size: 12px; margin-bottom: 8px;">O seu pedido foi recusado pelo Administrador.</p>
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

    # 3. SE ESTIVER PENDENTE
    if st.session_state.pedido_submetido:
        st.markdown(
            """
                <div style="background-color: #050507; padding: 20px; text-align: center; border-radius: 6px; max-width: 450px; margin: 20px auto;">
                    <h3 style="color: #ffffff; font-size: 16px; margin-bottom: 4px;">Aguardando Aprovação</h3>
                    <p style="color: #d4d4d8; font-size: 12px; margin-bottom: 4px;">O seu registo está a aguardar validação do Administrador.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(3)
        st.rerun()
        return

    # ==========================================
    # 🎨 4. TELA INICIAL: REGISTO / LOGIN COMPACTO
    # ==========================================
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
                max-width: 780px !important;
                padding-top: 0.4rem !important;
                padding-bottom: 0.6rem !important;
                padding-left: 1.5rem !important;
                padding-right: 1.5rem !important;
                background-color: #000000 !important;
                border-radius: 12px;
                border: 1px solid rgba(138, 43, 226, 0.25);
                margin-top: 0.2rem;
                margin-bottom: 0.2rem;
            }}
            .input-label-custom {{
                color: #e2e8f0;
                font-size: 11px;
                font-weight: 600;
                margin-bottom: 2px;
            }}
        </style>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <img src="{LINK_LOGO}" style="width: 110px; border-radius: 4px; display: block;" />
            <div style="width: 32px; height: 32px; background: rgba(234, 179, 8, 0.1); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: #eab308; font-size: 14px;">👤</div>
        </div>

        <div style="text-align: center; margin-bottom: 10px;">
            <h1 style="color: #eab308; font-size: 20px; font-weight: 900; margin-bottom: 2px;">ÁREA DO PRESTADOR</h1>
            <p style="color: #a1a1aa; font-size: 11px; margin: 0;">Faça o seu registo de acesso ou entre com os seus dados se já tiver uma sessão ativa.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    modo_acesso = st.radio(
        "Escolha a opção:",
        ["Novo Registo", "Já estou online / Entrar com Nome e Telefone"],
        horizontal=True,
    )

    if modo_acesso == "Novo Registo":
        with st.form("form_registo_prestador_idêntico"):
            st.markdown(
                """
                <div style="background-color: #050507; border: 1px solid #3b2c60; border-radius: 8px; padding: 10px 14px;">
                """,
                unsafe_allow_html=True,
            )

            st.markdown('<div class="input-label-custom">👤 Nome Completo</div>', unsafe_allow_html=True)
            nome = st.text_input("Nome Completo", placeholder="Digite o seu nome completo", label_visibility="collapsed")

            st.markdown('<div class="input-label-custom">📞 Telemóvel / Telefone</div>', unsafe_allow_html=True)
            telefone = st.text_input("Telemóvel / Telefone", placeholder="Digite o seu número de telefone", label_visibility="collapsed")

            st.markdown('<div class="input-label-custom">📍 Estabelecimento</div>', unsafe_allow_html=True)
            estabelecimento = st.text_input("Estabelecimento", placeholder="Ex: Bar do Zé, Restaurante Bom Sabor...", label_visibility="collapsed")

            st.markdown('<div class="input-label-custom">📄 Escolha o Contrato</div>', unsafe_allow_html=True)
            contrato = st.selectbox(
                "Contrato",
                [
                    "1 Hora - 12.000,00 Kwanzaas",
                    "2 Horas - 17.000,00 Kwanzaas",
                    "3 Horas - 20.000,00 Kwanzaas",
                ],
                label_visibility="collapsed",
            )

            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
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
                        "video_fundo": "",
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
                <div style="background-color: #050507; border: 1px solid #3b2c60; border-radius: 8px; padding: 12px 14px;">
                """,
                unsafe_allow_html=True,
            )

            st.markdown('<div class="input-label-custom">👤 Nome Registado</div>', unsafe_allow_html=True)
            login_nome = st.text_input("Nome", placeholder="Digite o nome com que se registou", label_visibility="collapsed")

            st.markdown('<div class="input-label-custom">📞 Telemóvel / Telefone</div>', unsafe_allow_html=True)
            login_telefone = st.text_input("Telefone", placeholder="Digite o número de telefone registado", label_visibility="collapsed")

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            btn_entrar = st.form_submit_button("🔑 ACEDER AO PAINEL", use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if btn_entrar:
                if login_nome.strip() and login_telefone.strip():
                    prestadores = obter_prestadores()
                    prestador_encontrado = next(
                        (
                            p
                            for p in prestadores
                            if p.get("nome", "").strip().lower()
                            == login_nome.strip().lower()
                            and p.get("telefone", "").strip() == login_telefone.strip()
                        ),
                        None,
                    )

                    if prestador_encontrado:
                        st.session_state.pedido_submetido = True
                        st.session_state.token_prestador = prestador_encontrado.get("token")
                        status_db = prestador_encontrado.get("status_str", "pendente")
                        st.session_state.estado_pedido = status_db
                        if status_db == "aprovado":
                            st.session_state.aprovado = True
                        st.rerun()
                    else:
                        st.error("Registo não encontrado com estes dados.")
                else:
                    st.error("Preencha o Nome e o Telefone.")

    # 3 BLOCOS INFORMATIVOS NO RODAPÉ COMPACTOS
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        st.markdown(
            """
            <div style="background-color: #050507; border: 1px solid #27203d; padding: 6px; border-radius: 6px; display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 14px;">🎧</span>
                <div>
                    <div style="color: #eab308; font-size: 9px; font-weight: bold;">RÁPIDO</div>
                    <div style="color: #a1a1aa; font-size: 9px;">Registe-se em passos simples.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_f2:
        st.markdown(
            """
            <div style="background-color: #050507; border: 1px solid #27203d; padding: 6px; border-radius: 6px; display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 14px;">🛡️</span>
                <div>
                    <div style="color: #eab308; font-size: 9px; font-weight: bold;">SEGURO</div>
                    <div style="color: #a1a1aa; font-size: 9px;">Dados protegidos com segurança.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_f3:
        st.markdown(
            """
            <div style="background-color: #050507; border: 1px solid #27203d; padding: 6px; border-radius: 6px; display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 14px;">⭐</span>
                <div>
                    <div style="color: #eab308; font-size: 9px; font-weight: bold;">FASTA!</div>
                    <div style="color: #a1a1aa; font-size: 9px;">Junte-se ao FF KARAOKE.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

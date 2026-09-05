from datetime import datetime
import time
import streamlit as st
from db import guardar_prestador, obter_pedidos_musicas, obter_prestadores, guardar_pedido_musica, apagar_pedido_musica

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

        # ==========================================
        # 🎨 ESTILO COM LARGURA AUMENTADA (1613px)
        # ==========================================
        st.markdown(
            """
            <style>
                /* Fundo preto geral da página */
                .stApp {
                    background-color: #08080a !important;
                }
                
                /* Moldura centralizada (Largura máxima ampliada para 1613px) */
                .block-container {
                    max-width: 1613px !important;
                    padding-top: 1.8rem !important;
                    padding-bottom: 2.2rem !important;
                    padding-left: 2rem !important;
                    padding-right: 2rem !important;
                    background-color: #0b0714 !important;
                    border-radius: 20px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
                    border: 1px solid rgba(138, 43, 226, 0.25);
                    margin-top: 1.5rem;
                    margin-bottom: 1.5rem;
                }

                .box-container {
                    background-color: #0c0c0e;
                    border: 1px solid #27272a;
                    border-radius: 8px;
                    padding: 12px 16px;
                    margin-bottom: 10px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
                }
                .box-title {
                    color: #eab308;
                    font-weight: bold;
                    font-size: 13px;
                    margin-bottom: 8px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    letter-spacing: 0.5px;
                }
                .box-content {
                    color: #d4d4d8;
                    font-size: 13px;
                }
                div[data-testid="column"] {
                    padding: 0px !important;
                }
                .stButton button {
                    background-color: #121215 !important;
                    color: #ffffff !important;
                    border: 1px solid #27272a !important;
                    border-radius: 6px !important;
                    min-height: 32px !important;
                    height: 36px !important;
                    font-weight: 500;
                }
                .stButton button:hover {
                    border-color: #eab308 !important;
                    color: #eab308 !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Cabeçalho reorganizado em 3 colunas: [Logotipo / Identidade], [Relógio], [Botão Sair]
        col_logo_info, col_relogio, col_top_btn = st.columns([2, 1, 0.8])

        with col_logo_info:
            nome_prestador = prestador_atual.get("nome", "Prestador") if prestador_atual else "Prestador"
            estabelecimento_prestador = prestador_atual.get("estabelecimento", "") if prestador_atual else ""
            sub_texto = f"📍 {estabelecimento_prestador}" if estabelecimento_prestador else "Painel de Controlo"

            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 12px; background-color: #121215; border: 1px solid #27272a; padding: 6px 12px; border-radius: 8px; height: 50px;">
                    <div style="width: 36px; height: 36px; border: 2px solid #eab308; border-radius: 50%; display: flex; align-items: center; justify-content: center; background-color: rgba(234, 179, 8, 0.1); flex-shrink: 0;">
                        <span style="color: #eab308; font-size: 16px;">⭐</span>
                    </div>
                    <div style="overflow: hidden;">
                        <div style="color: #eab308; font-weight: 800; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{nome_prestador}</div>
                        <div style="color: #a1a1aa; font-size: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{sub_texto}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_relogio:
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
                    <div style="background-color: #121215; border: 1px solid #eab308; padding: 4px 8px; border-radius: 8px; text-align: center; height: 50px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 0 10px rgba(234, 179, 8, 0.2);">
                        <div style="color: #eab308; font-size: 8px; font-weight: bold; letter-spacing: 1px;">⏳ TEMPO RESTANTE</div>
                        <div style="color: #ffffff; font-family: monospace; font-size: 16px; font-weight: 900; letter-spacing: 1px;">{tempo_formatado}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            renderizar_relogio_topo()

        with col_top_btn:
            st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()

        st.markdown(
            """
            <div style="margin: 8px 0px 14px 0px; text-align: center;">
                <hr style="border: none; border-top: 1px solid #eab308; opacity: 0.6; margin: 0;">
                <span style="position: relative; top: -10px; background-color: #08080a; padding: 0 10px; color: #eab308; font-size: 14px;">⭐</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_esq, col_dir = st.columns([1.35, 1])

        with col_esq:

            @st.fragment(run_every=3)
            def renderizar_a_tocar():
                st.markdown(
                    """
                        <div class="box-container" style="border: 1px solid #27272a;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <div style="width: 48px; height: 48px; border: 2px solid #eab308; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(234, 179, 8, 0.2);">
                                        <span style="font-size: 20px; color: #eab308;">🎵</span>
                                    </div>
                                    <div>
                                        <div style="color: #eab308; font-weight: bold; font-size: 12px; letter-spacing: 0.5px;">▶ A TOCAR AGORA</div>
                                        <div style="color: #ffffff; font-size: 18px; font-weight: bold;">Nada em reprodução</div>
                                        <div style="color: #a1a1aa; font-size: 11px;">(Apenas no ecrã de TV).</div>
                                    </div>
                                </div>
                            </div>
                            <div style="text-align: right; opacity: 0.7; margin-top: 4px;">
                                <span style="font-size: 11px; color: #eab308; letter-spacing: 2px;">▂▃▄▅▆▇█▇▆▅▄▃▂ ▂▃▄▅▆▇█</span>
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
            renderizar_a_tocar()

            st.markdown('<div class="btn-acao">', unsafe_allow_html=True)
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
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

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

                st.markdown(
                    f"""
                        <div class="box-container" style="max-height: 400px; overflow-y: auto;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; border-bottom: 1px solid #27272a; padding-bottom: 8px;">
                                <div style="width: 32px; height: 32px; border: 1px solid #c084fc; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                    <span style="color: #c084fc; font-size: 14px;">👥</span>
                                </div>
                                <span style="color: #c084fc; font-weight: bold; font-size: 13px; letter-spacing: 0.5px;">FILA DE PEDIDOS ({total_pedidos})</span>
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
                                <div style="background-color: #121215; border: 1px solid #27272a; border-radius: 6px; padding: 8px 12px; display: flex; align-items: center; gap: 10px; height: 40px; margin-bottom: 6px;">
                                    <span style="background-color: #27272a; color: #c084fc; font-weight: bold; font-size: 12px; padding: 2px 6px; border-radius: 4px;">{idx+1}º</span>
                                    <span style="color: #ffffff; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{musica} — <span style="color: #a1a1aa;">{cantor}</span></span>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        with col_botoes:
                            b_up, b_down, b_del = st.columns(3)
                            with b_up:
                                if idx > 0:
                                    if st.button("⬆️", key=f"up_{pedido_id}", use_container_width=True):
                                        global_idx_atual = next((i for i, item in enumerate(todos_pedidos) if (item.get("id") or item.get("timestamp") or i) == pedido_id), None)
                                        if global_idx_atual is not None and global_idx_atual > 0:
                                            todos_pedidos[global_idx_atual], todos_pedidos[global_idx_atual - 1] = todos_pedidos[global_idx_atual - 1], todos_pedidos[global_idx_atual]
                                            for item in todos_pedidos:
                                                guardar_pedido_musica(item)
                                        st.rerun()
                            with b_down:
                                if idx < total_pedidos - 1:
                                    if st.button("⬇️", key=f"down_{pedido_id}", use_container_width=True):
                                        global_idx_atual = next((i for i, item in enumerate(todos_pedidos) if (item.get("id") or item.get("timestamp") or i) == pedido_id), None)
                                        if global_idx_atual is not None and global_idx_atual < len(todos_pedidos) - 1:
                                            todos_pedidos[global_idx_atual], todos_pedidos[global_idx_atual + 1] = todos_pedidos[global_idx_atual + 1], todos_pedidos[global_idx_atual]
                                            for item in todos_pedidos:
                                                guardar_pedido_musica(item)
                                        st.rerun()
                            with b_del:
                                if st.button("❌", key=f"del_{pedido_id}", use_container_width=True):
                                    apagar_pedido_musica(pedido_id)
                                    st.rerun()
                else:
                    st.markdown(
                        "<p style='color: #a1a1aa; margin: 0; font-size: 12px;'>Sem pedidos na fila.</p>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    """
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

            renderizar_fila_pedidos()

        with col_dir:
            st.markdown(
                f"""
                    <div class="box-container">
                        <div class="box-title">
                            <span>🔗 LINKS E QR CODE</span>
                        </div>
                        <div class="box-content" style="font-size: 11px; word-break: break-all; margin-bottom: 8px;">
                            <span style="color: #eab308;">Cliente:</span> {url_cliente}<br>
                            <span style="color: #3b82f6;">TV:</span> {url_tela}
                        </div>
                        <div style="text-align: center; background: #ffffff; padding: 6px; border-radius: 6px;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={url_cliente}" width="120" />
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            col_bt_tv, col_bt_cli = st.columns(2)
            with col_bt_tv:
                st.markdown(
                    f'<a href="{url_tela}" target="_blank"><button style="width: 100%; background-color: #121215; color: #ffffff; border: 1px solid #27272a; padding: 6px; border-radius: 6px; font-size: 12px; font-weight: 500;">🖥️ TV</button></a>',
                    unsafe_allow_html=True,
                )
            with col_bt_cli:
                st.markdown(
                    f'<a href="{url_cliente}" target="_blank"><button style="width: 100%; background-color: #121215; color: #ffffff; border: 1px solid #27272a; padding: 6px; border-radius: 6px; font-size: 12px; font-weight: 500;">📱 Cliente</button></a>',
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

            videos_disponiveis = {
                "- Sem vídeo -": "",
                "Vídeo 1 (Oficial)": "https://youtu.be/cQ4MD7gOBmc?si=5wzaxysiHSEwn9QT",
                "Vídeo 2": "https://youtu.be/H_aniWehIYY?si=e9WzMGyFSy7PdrAj",
                "Vídeo 3": "https://youtu.be/sGGlQ9yJQNg?si=LVeN5zjZ153uksLW",
                "Vídeo 4": "https://youtu.be/sGGlQ9yJQNg?si=ZxjJ34_4Z13MUL-g",
                "Vídeo 5": "https://youtu.be/TmayKMV0bJY?si=Zb99BwXuFyDDJ-tN",
            }

            st.markdown(
                """
                <div class="box-container">
                    <div class="box-title">
                        <span>🎬 VÍDEO DE FUNDO DA TV</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            video_escolhido = st.selectbox(
                "Vídeo de fundo:",
                list(videos_disponiveis.keys()),
                label_visibility="collapsed",
            )
            url_video_selecionado = videos_disponiveis[video_escolhido]

            if st.button(
                "▶ Atualizar Vídeo",
                use_container_width=True,
                type="primary",
                key="btn_atualizar_video",
            ):
                if st.session_state.token_prestador:
                    prestadores = obter_prestadores()
                    for p in prestadores:
                        if p.get("token") == st.session_state.token_prestador:
                            p["video_fundo"] = url_video_selecionado
                            guardar_prestador(p)
                    st.success("Guardado!")

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Rodapé estruturado
        st.markdown(
            """
            <style>
                .footer-box {
                    background-color: #0c0c0e;
                    border: 1px solid #27272a;
                    border-radius: 8px;
                    padding: 14px 16px;
                    margin-top: 10px;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown(
                '<div class="footer-box">', unsafe_allow_html=True
            )
            f1, f2, f3, f4 = st.columns(4)

            with f1:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 38px; height: 38px; border: 1px solid #c084fc; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <span style="color: #c084fc; font-size: 16px;">🚀</span>
                        </div>
                        <div>
                            <div style="color: #c084fc; font-weight: bold; font-size: 10px; letter-spacing: 0.5px;">RÁPIDO E PRÁTICO</div>
                            <div style="color: #a1a1aa; font-size: 10px; line-height: 1.2;">Controle a reprodução fácil.</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with f2:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 38px; height: 38px; border: 1px solid #eab308; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 6px rgba(234, 179, 8, 0.2);">
                            <span style="color: #eab308; font-size: 16px;">🛡️</span>
                        </div>
                        <div>
                            <div style="color: #eab308; font-weight: bold; font-size: 10px; letter-spacing: 0.5px;">CONTROLE TOTAL</div>
                            <div style="color: #a1a1aa; font-size: 10px; line-height: 1.2;">Gerencie a fila e a TV.</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with f3:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 38px; height: 38px; border: 1px solid #c084fc; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <span style="color: #c084fc; font-size: 16px;">👥</span>
                        </div>
                        <div>
                            <div style="color: #c084fc; font-weight: bold; font-size: 10px; letter-spacing: 0.5px;">CONECTADO</div>
                            <div style="color: #a1a1aa; font-size: 10px; line-height: 1.2;">Links e QR Code ativos.</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with f4:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 38px; height: 38px; border: 1px solid #eab308; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 6px rgba(234, 179, 8, 0.2);">
                            <span style="color: #eab308; font-size: 16px;">⭐</span>
                        </div>
                        <div>
                            <div style="color: #eab308; font-weight: bold; font-size: 10px; letter-spacing: 0.5px;">FAZ A VOZ!</div>
                            <div style="color: #a1a1aa; font-size: 10px; line-height: 1.2;">Obrigado por fazer parte!</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        return

    # 2. SE ESTIVER RECUSADO
    if (
        st.session_state.pedido_submetido
        and st.session_state.estado_pedido == "recusado"
    ):
        st.markdown(
            """
                <div style="background-color: #0f0f11; border: 1px solid #ef4444; padding: 20px; text-align: center; border-radius: 8px; max-width: 500px; margin: 30px auto;">
                    <div style="font-size: 35px; margin-bottom: 8px;">❌</div>
                    <h3 style="color: #ef4444; font-size: 18px; margin-bottom: 8px;">Pedido Recusado</h3>
                    <p style="color: #d4d4d8; font-size: 14px; margin-bottom: 12px;">O seu pedido foi recusado pelo Administrador.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
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
                <div style="background-color: #0f0f11; padding: 25px; text-align: center; border-radius: 8px; max-width: 500px; margin: 30px auto;">
                    <h3 style="color: #ffffff; font-size: 18px; margin-bottom: 8px;">Aguardando Aprovação</h3>
                    <p style="color: #d4d4d8; font-size: 14px; margin-bottom: 6px;">O seu registo está a aguardar validação do Administrador.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(3)
        st.rerun()
        return

    # 4. TELA INICIAL: REGISTO OU LOGIN
    st.markdown(
        """
            <style>
                .prestador-wrapper {
                    background: #0f0f13;
                    border: 1px solid #8b5cf6;
                    border-radius: 10px;
                    padding: 16px 20px;
                    max-width: 700px;
                    margin: 0 auto;
                }
                .prestador-title {
                    color: #eab308;
                    font-size: 20px;
                    font-weight: 800;
                    margin-top: 4px;
                    margin-bottom: 2px;
                    text-align: center;
                }
                .prestador-subtitle {
                    color: #a1a1aa;
                    font-size: 13px;
                    text-align: center;
                    margin-bottom: 10px;
                }
            </style>
            <div class="prestador-wrapper">
                <div style="text-align: center;">
                    <span style="font-size: 28px;">👤</span>
                    <div class="prestador-title">ÁREA DO PRESTADOR</div>
                    <div class="prestador-subtitle">Registe-se ou entre com a sua sessão ativa.</div>
                </div>
        """,
        unsafe_allow_html=True,
    )

    modo_acesso = st.radio(
        "Modo:",
        ["Novo Registo", "Entrar com Sessão Ativa"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if modo_acesso == "Novo Registo":
        with st.form("form_registo_prestador_compacto"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input(
                    "Nome", placeholder="Nome Completo", label_visibility="collapsed"
                )
                estabelecimento = st.text_input(
                    "Local",
                    placeholder="Nome do Estabelecimento",
                    label_visibility="collapsed",
                )
            with c2:
                telefone = st.text_input(
                    "Telefone",
                    placeholder="Telemóvel / Telefone",
                    label_visibility="collapsed",
                )
                contrato = st.selectbox(
                    "Plano",
                    [
                        "1 Hora - 12.000,00 Kz",
                        "2 Horas - 17.000,00 Kz",
                        "3 Horas - 20.000,00 Kz",
                    ],
                    label_visibility="collapsed",
                )

            submitted = st.form_submit_button(
                "🚀 SUBMETER PEDIDO", use_container_width=True
            )

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
        with st.form("form_login_prestador_compacto"):
            c1, c2 = st.columns(2)
            with c1:
                login_nome = st.text_input(
                    "Nome",
                    placeholder="Nome registado",
                    label_visibility="collapsed",
                )
            with c2:
                login_telefone = st.text_input(
                    "Telefone",
                    placeholder="Telefone registado",
                    label_visibility="collapsed",
                )

            btn_entrar = st.form_submit_button(
                "🔑 ACEDER AO PAINEL", use_container_width=True
            )
            
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
                        st.session_state.token_prestador = prestador_encontrado.get(
                            "token"
                        )
                        status_db = prestador_encontrado.get("status_str", "pendente")
                        st.session_state.estado_pedido = status_db
                        if status_db == "aprovado":
                            st.session_state.aprovado = True
                        st.rerun()
                    else:
                        st.error("Registo não encontrado.")
                else:
                    st.error("Preencha os campos de Nome e Telefone.")

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

    # 1. SE ESTIVER APROVADO: Painel Operacional
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

        # Estilos globais seguros
        st.markdown(
            """
            <style>
                .stApp {
                    background-color: #08080a !important;
                }
                .block-container {
                    max-width: 1344px !important;
                    padding-top: 1.5rem !important;
                    padding-bottom: 2rem !important;
                    padding-left: 1.8rem !important;
                    padding-right: 1.8rem !important;
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
                    letter-spacing: 0.5px;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        col_lateral, col_principal = st.columns([0.8, 2.8])

        # COLUNA LATERAL USANDO COMPONENTES NATIVOS (Zero risco de tela branca)
        with col_lateral:
            @st.fragment(run_every=3)
            def renderizar_relogio_topo():
                prestadores_local = obter_prestadores()
                p_atual = next(
                    (
                        p
                        for p in prestadores_local
                        if p.get("token") == st.session_state.token_prestador
                    ),
                    None,
                )

                segundos_restantes = 7200
                if p_atual:
                    segundos_contrato_inicial = p_atual.get("segundos_restantes", 7200)
                    data_pedido_str = p_atual.get("data_pedido", "")

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
                    <div style="background-color: #121215; border: 2px solid #eab308; padding: 6px; border-radius: 8px; text-align: center; margin-bottom: 8px;">
                        <span style="color: #eab308; font-size: 9px; font-weight: bold;">⏳ TEMPO RESTANTE</span><br>
                        <span style="color: #ffffff; font-family: monospace; font-size: 18px; font-weight: bold;">{tempo_formatado}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            renderizar_relogio_topo()

            nome_prestador_txt = prestador_atual.get("nome", "Prestador") if prestador_atual else "Prestador"
            estabelecimento_txt = prestador_atual.get("estabelecimento", "") if prestador_atual else ""
            sub_info = f" — {estabelecimento_txt}" if estabelecimento_txt else ""

            st.markdown(
                f"""
                <div style="background-color: #121215; border: 1px solid #8b5cf6; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                    <span style="color: #c084fc; font-size: 9px; font-weight: bold;">🎙️ PRESTADOR EM SESSÃO</span><br>
                    <span style="color: #ffffff; font-size: 12px; font-weight: bold;">{nome_prestador_txt}{sub_info}</span><br>
                    <div style="margin-top: 6px; display: flex; justify-content: space-between; font-size: 10px;">
                        <span style="color: #a1a1aa;">Estado:</span>
                        <span style="color: #eab308; font-weight: bold;">🟢 Ativo</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("🚪 Sair da Sessão", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()

            st.markdown("---")
            st.caption("🚀 **Rápido e Prático**\nControle a reprodução fácil.")
            st.caption("🛡️ **Controle Total**\nGerencie a fila e a TV.")
            st.caption("👥 **Conectado**\nLinks e QR Code ativos.")

        # COLUNA PRINCIPAL
        with col_principal:
            col_esq, col_dir = st.columns([1.35, 1])

            with col_esq:
                @st.fragment(run_every=3)
                def renderizar_a_tocar():
                    st.markdown(
                        """
                            <div class="box-container">
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <div style="width: 44px; height: 44px; border: 2px solid #eab308; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                        <span style="font-size: 18px; color: #eab308;">🎵</span>
                                    </div>
                                    <div>
                                        <div style="color: #eab308; font-weight: bold; font-size: 11px;">▶ A TOCAR AGORA</div>
                                        <div style="color: #ffffff; font-size: 16px; font-weight: bold;">Nada em reprodução</div>
                                        <div style="color: #a1a1aa; font-size: 10px;">(Apenas no ecrã de TV).</div>
                                    </div>
                                </div>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )
                renderizar_a_tocar()

                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("▶ Tocar", use_container_width=True):
                        st.toast("A tocar o primeiro...")
                with b2:
                    if st.button("⏸ Parar", use_container_width=True):
                        st.toast("Parado.")
                with b3:
                    if st.button("⏭ Próxima", use_container_width=True):
                        st.toast("Próxima.")

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

                @st.fragment(run_every=3)
                def renderizar_fila_pedidos():
                    try:
                        todos_pedidos = obter_pedidos_musicas() or []
                    except Exception:
                        todos_pedidos = []

                    token_ativo_local = str(st.session_state.get("token_prestador", ""))

                    lista_pedidos = []
                    for p in todos_pedidos:
                        if p.get("status", "pendente") == "pendente":
                            p_token = str(p.get("token_prestador", ""))
                            if not p_token or p_token == "None" or p_token == token_ativo_local:
                                lista_pedidos.append(p)

                    total_pedidos = len(lista_pedidos)

                    st.markdown(
                        f"""
                            <div class="box-container" style="max-height: 380px; overflow-y: auto;">
                                <div style="color: #c084fc; font-weight: bold; font-size: 12px; margin-bottom: 10px; border-bottom: 1px solid #27272a; padding-bottom: 6px;">
                                    👥 FILA DE PEDIDOS ({total_pedidos})
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
                                    <div style="background-color: #121215; border: 1px solid #27272a; border-radius: 6px; padding: 6px 10px; font-size: 12px; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                        <b>{idx+1}º</b> {musica} — <span style="color: #a1a1aa;">{cantor}</span>
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
                            "<p style='color: #a1a1aa; margin: 0; font-size: 11px;'>Sem pedidos na fila.</p>",
                            unsafe_allow_html=True,
                        )

                    st.markdown("</div>", unsafe_allow_html=True)

                renderizar_fila_pedidos()

            with col_dir:
                st.markdown(
                    f"""
                        <div class="box-container">
                            <div class="box-title">🔗 LINKS E QR CODE</div>
                            <div style="font-size: 11px; color: #d4d4d8; word-break: break-all; margin-bottom: 6px;">
                                <b style="color: #eab308;">Cliente:</b> {url_cliente}<br>
                                <b style="color: #3b82f6;">TV:</b> {url_tela}
                            </div>
                            <div style="text-align: center; background: #ffffff; padding: 4px; border-radius: 6px;">
                                <img src="https://api.qrserver.com/v1/create-qr-code/?size=110x110&data={url_cliente}" width="110" />
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_bt_tv, col_bt_cli = st.columns(2)
                with col_bt_tv:
                    st.markdown(
                        f'<a href="{url_tela}" target="_blank"><button style="width: 100%; background-color: #121215; color: #ffffff; border: 1px solid #27272a; padding: 4px; border-radius: 6px; font-size: 11px;">🖥️ TV</button></a>',
                        unsafe_allow_html=True,
                    )
                with col_bt_cli:
                    st.markdown(
                        f'<a href="{url_cliente}" target="_blank"><button style="width: 100%; background-color: #121215; color: #ffffff; border: 1px solid #27272a; padding: 4px; border-radius: 6px; font-size: 11px;">📱 Cliente</button></a>',
                        unsafe_allow_html=True,
                    )

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

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
                        <div class="box-title">🎬 VÍDEO DE FUNDO DA TV</div>
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
                ):
                    if st.session_state.token_prestador:
                        prestadores = obter_prestadores()
                        for p in prestadores:
                            if p.get("token") == st.session_state.token_prestador:
                                p["video_fundo"] = url_video_selecionado
                                guardar_prestador(p)
                        st.success("Guardado!")

                st.markdown("</div>", unsafe_allow_html=True)

        return

    # 2. SE ESTIVER RECUSADO
    if (
        st.session_state.pedido_submetido
        and st.session_state.estado_pedido == "recusado"
    ):
        st.error("O seu pedido foi recusado pelo Administrador.")
        if st.button("Tentar Novamente"):
            st.session_state.pedido_submetido = False
            st.session_state.token_prestador = None
            st.session_state.estado_pedido = "pendente"
            st.session_state.aprovado = False
            st.rerun()
        return

    # 3. SE ESTIVER PENDENTE
    if st.session_state.pedido_submetido:
        st.warning("O seu registo está a aguardar validação do Administrador. A atualizar...")
        time.sleep(3)
        st.rerun()
        return

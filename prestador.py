from datetime import datetime
import time
import streamlit as st
from db import guardar_prestador, obter_pedidos_musicas, obter_prestadores

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
                .block-container {
                    padding-top: 1.8rem !important;
                    padding-bottom: 0.5rem !important;
                    padding-left: 1rem !important;
                    padding-right: 1rem !important;
                    max-width: 100% !important;
                }
                .box-container {
                    background-color: #0c0c0e;
                    border: 1px solid #eab308;
                    border-radius: 6px;
                    padding: 10px 14px;
                    margin-bottom: 8px;
                    box-shadow: 0 0 6px rgba(234, 179, 8, 0.1);
                }
                .box-title {
                    color: #eab308;
                    font-weight: bold;
                    font-size: 14px;
                    margin-bottom: 6px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .box-content {
                    color: #d4d4d8;
                    font-size: 13px;
                }
                div[data-testid="column"] {
                    padding: 0px !important;
                }
                /* Estilo geral de botões padrão */
                .stButton button {
                    min-height: 28px !important;
                    height: 30px !important;
                    padding: 0px 6px !important;
                    font-size: 13px !important;
                }
                /* Classe específica para reduzir os botões Tocar, Parar, Próxima */
                .btn-acao button {
                    min-height: 22px !important;
                    height: 24px !important;
                    font-size: 11px !important;
                    padding: 0px 4px !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        col_logo, col_top_info, col_top_btn = st.columns([1.2, 4.3, 1.2])
        with col_logo:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                    <span style="font-size: 26px;">⭐</span>
                    <div>
                        <span style="color: #eab308; font-weight: bold; font-size: 15px; display: block; line-height: 1;">FF KARAOKE</span>
                        <span style="color: #a1a1aa; font-size: 8px; letter-spacing: 0.5px;">FAZ A VOZ, FAZ A FESTA!</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_top_info:
            nome_prestador = (
                prestador_atual.get("nome", "") if prestador_atual else ""
            )
            st.markdown(
                f"<div style='text-align: center; padding-top: 4px;'><span"
                f" style='color: #eab308; font-size: 19px; font-weight: 800;"
                f" letter-spacing: 1px;'>PRESTADOR:"
                f" {nome_prestador.upper()}</span></div>",
                unsafe_allow_html=True,
            )

        with col_top_btn:
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        col_esq, col_dir = st.columns([1.3, 1])

        with col_esq:

            @st.fragment(run_every=3)
            def renderizar_a_tocar():
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
                        <div class="box-container">
                            <div class="box-title">
                                <span>▶ A TOCAR AGORA</span>
                                <span style="color: #eab308; font-family: monospace; font-size: 14px;">⏳ {tempo_formatado}</span>
                            </div>
                            <div class="box-content">
                                <p style="margin: 0 0 2px 0; font-weight: 500; font-size: 13px;">Nada em reprodução (Apenas no ecrã de TV).</p>
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

            renderizar_a_tocar()

            # Botões de ação reduzidos com classe customizada
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
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

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
                        <div class="box-container" style="max-height: 200px; overflow-y: auto;">
                            <div class="box-title" style="margin-bottom: 4px;">
                                <span>📄 FILA DE PEDIDOS ({total_pedidos})</span>
                            </div>
                            <div class="box-content">
                    """,
                    unsafe_allow_html=True,
                )

                if total_pedidos > 0:
                    for idx, pedido in enumerate(lista_pedidos):
                        musica = pedido.get("musica", "Desconhecida")
                        cantor = pedido.get("cantor", "Convidado")

                        col_txt, col_botoes = st.columns([5, 3])

                        with col_txt:
                            st.markdown(
                                f"""
                                        <div style="font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.3;">
                                            <b style="color: #eab308;">{idx+1}º</b> {musica} — <span style="color: #a1a1aa;">{cantor}</span>
                                        </div>
                                    """,
                                unsafe_allow_html=True,
                            )

                        with col_botoes:
                            b_up, b_down, b_del = st.columns(3)
                            with b_up:
                                if idx > 0:
                                    if st.button("⬆️", key=f"up_{idx}"):
                                        lista_pedidos[idx], lista_pedidos[idx - 1] = (
                                            lista_pedidos[idx - 1],
                                            lista_pedidos[idx],
                                        )
                                        st.rerun()
                            with b_down:
                                if idx < total_pedidos - 1:
                                    if st.button("⬇️", key=f"down_{idx}"):
                                        lista_pedidos[idx], lista_pedidos[idx + 1] = (
                                            lista_pedidos[idx + 1],
                                            lista_pedidos[idx],
                                        )
                                        st.rerun()
                            with b_del:
                                if st.button("❌", key=f"del_{idx}"):
                                    lista_pedidos.pop(idx)
                                    st.rerun()

                        if idx < total_pedidos - 1:
                            st.markdown(
                                "<hr style='margin: 3px 0px; border: none; border-top: 1px solid #27272a;'>",
                                unsafe_allow_html=True,
                            )
                else:
                    st.markdown(
                        "<p style='color: #a1a1aa; margin: 0; font-size: 12px;'>Sem pedidos.</p>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    """
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            renderizar_fila_pedidos()

        with col_dir:
            st.markdown(
                f"""
                    <div class="box-container">
                        <div class="box-title" style="margin-bottom: 4px;">
                            <span>🔗 LINKS E QR CODE</span>
                        </div>
                        <div class="box-content" style="font-size: 11px; word-break: break-all; margin-bottom: 6px;">
                            <span style="color: #eab308;">Cli:</span> {url_cliente}<br>
                            <span style="color: #3b82f6;">TV:</span> {url_tela}
                        </div>
                        <div style="text-align: center; background: #ffffff; padding: 4px; border-radius: 4px;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=105x105&data={url_cliente}" width="105" />
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            col_bt_tv, col_bt_cli = st.columns(2)
            with col_bt_tv:
                st.markdown(
                    f'<a href="{url_tela}" target="_blank"><button style="width: 100%;'
                    " background-color: #18181b; color: #ffffff; border: 1px solid"
                    " #eab308; padding: 4px; border-radius: 4px; font-size:"
                    ' 12px;">🖥️ TV</button></a>',
                    unsafe_allow_html=True,
                )
            with col_bt_cli:
                st.markdown(
                    f'<a href="{url_cliente}" target="_blank"><button style="width:'
                    " 100%; background-color: #18181b; color: #ffffff; border: 1px solid"
                    " #eab308; padding: 4px; border-radius: 4px; font-size:"
                    ' 12px;">📱 Cliente</button></a>',
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

            video_escolhido = st.selectbox(
                "Vídeo de fundo:",
                list(videos_disponiveis.keys()),
                label_visibility="collapsed",
            )
            url_video_selecionado = videos_disponiveis[video_escolhido]

            if st.button("▶ Atualizar Vídeo", use_container_width=True, type="primary", key="btn_atualizar_video"):
                if st.session_state.token_prestador:
                    prestadores = obter_prestadores()
                    for p in prestadores:
                        if p.get("token") == st.session_state.token_prestador:
                            p["video_fundo"] = url_video_selecionado
                            guardar_prestador(p)
                    st.success("Guardado!")
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
                    st.error("Preencha os campos.")

    st.markdown("</div>", unsafe_allow_html=True)

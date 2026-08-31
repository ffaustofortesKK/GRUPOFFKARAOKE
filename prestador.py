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

    # Verificação periódica do estado do prestador se houver token ativo
    prestador_atual = None
    if st.session_state.pedido_submetido and st.session_state.token_prestador:
        prestadores = obter_prestadores()
        prestador_atual = next((p for p in prestadores if p.get("token") == st.session_state.token_prestador), None)
        
        if prestador_atual:
            status_atual = prestador_atual.get("status_str", "pendente")
            st.session_state.estado_pedido = status_atual
            
            if status_atual == "aprovado":
                st.session_state.aprovado = True

    # 1. SE ESTIVER APROVADO: Mostra o painel operacional completo
    if st.session_state.get("aprovado", False) or st.session_state.get("estado_pedido") == "aprovado":
        
        # --- GERAR URLS BASE ROBUSTAS (Apontando corretamente para as páginas do app) ---
        try:
            base_url = st.context.headers.get("Host", "")
            if base_url:
                protocol = "http" if "localhost" in base_url or "127.0.0.1" in base_url else "https"
                url_cliente = f"{protocol}://{base_url}/?page=cliente"
                url_tela = f"{protocol}://{base_url}/?page=tela"
            else:
                raise Exception()
        except Exception:
            url_cliente = "https://grupoffkaraoke.streamlit.app/?page=cliente"
            url_tela = "https://grupoffkaraoke.streamlit.app/?page=tela"

        # CSS personalizado para o estilo escuro com bordas douradas
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
            </style>
        """, unsafe_allow_html=True)

        # Botão discreto para terminar sessão no topo (com o texto aumentado 100%)
        col_top_info, col_top_btn = st.columns([4, 1])
        with col_top_info:
            st.markdown(f"<span style='color: #eab308; font-size: 26px; font-weight: bold;'>Sessão Ativa | Prestador: {prestador_atual.get('nome', '') if prestador_atual else ''}</span>", unsafe_allow_html=True)
        with col_top_btn:
            if st.button("Sair / Terminar", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Layout de 2 colunas principais
        col_esq, col_dir = st.columns([1.3, 1])

        with col_esq:
            # --- CAIXA 1: A TOCAR AGORA (Com atualização em tempo real do temporizador) ---
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
            
            # Botões de ação
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

            # --- CAIXA 2: FILA DE PEDIDOS (Com numeração sequencial exata e títulos a preto) ---
            @st.fragment(run_every=3)
            def renderizar_fila_pedidos():
                try:
                    todos_pedidos = obter_pedidos_musicas()
                except Exception:
                    todos_pedidos = []

                # Filtra estritamente apenas os pedidos pendentes associados ao token do prestador atual
                token_ativo = st.session_state.get("token_prestador")
                lista_pedidos = [
                    p for p in todos_pedidos 
                    if p.get("status", "pendente") == "pendente" 
                    and str(p.get("token_prestador", "")) == str(token_ativo)
                ]

                total_pedidos = len(lista_pedidos)

                st.markdown(f"""
                    <div class="box-container">
                        <div class="box-title">
                            <span>📄 FILA DE PEDIDOS ({total_pedidos})</span>
                        </div>
                        <div class="box-content">
                """, unsafe_allow_html=True)

                if total_pedidos > 0:
                    for idx, pedido in enumerate(lista_pedidos, start=1):
                        musica = pedido.get('musica', 'Música Desconhecida')
                        cantor = pedido.get('cantor', 'Convidado')
                        # Texto com cor preta (#000000) e fundo destacado para leitura perfeita
                        st.markdown(f"<p style='margin: 6px 0; padding: 4px 8px; background-color: #e4e4e7; border-radius: 4px; color: #000000;'><b>{idx}ª Posição.</b> <b>{musica}</b> — <span>{cantor}</span></p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #a1a1aa; margin: 0;'>Sem pedidos em espera.</p>", unsafe_allow_html=True)

                st.markdown("""
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            renderizar_fila_pedidos()

        with col_dir:
            # --- CAIXA 3: LINKS E QR CODE ---
            st.markdown(f"""
                <div class="box-container">
                    <div class="box-title">
                        <span>🔗 LINKS E QR CODE</span>
                    </div>
                    <div class="box-content" style="font-size: 12px; word-break: break-all; margin-bottom: 12px;">
                        <span style="color: #eab308; font-weight: bold;">Cliente:</span> {url_cliente}<br><br>
                        <span style="color: #3b82f6; font-weight: bold;">TV:</span> {url_tela}
                    </div>
                    <div style="text-align: center; background: #ffffff; padding: 10px; border-radius: 6px; margin-bottom: 12px;">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=170x170&data={url_cliente}" width="170" />
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_bt_tv, col_bt_cli = st.columns(2)
            with col_bt_tv: st.markdown(f'<a href="{url_tela}" target="_blank"><button style="width: 100%; background-color: #18181b; color: #ffffff; border: 1px solid #eab308; padding: 8px; border-radius: 6px; cursor: pointer; font-size: 13px;">🖥️ Abrir TV</button></a>', unsafe_allow_html=True)
            with col_bt_cli:
                st.markdown(f'<a href="{url_cliente}" target="_blank"><button style="width: 100%; background-color: #18181b; color: #ffffff; border: 1px solid #eab308; padding: 8px; border-radius: 6px; cursor: pointer; font-size: 13px;">📱 Abrir cliente</button></a>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # --- CAIXA 4: VÍDEO DE FUNDO DA TV ---
            videos_disponiveis = {
                "- Sem vídeo de fundo -": "",
                "Vídeo 1 (Oficial)": "https://youtu.be/cQ4MD7gOBmc?si=5wzaxysiHSEwn9QT",
                "Vídeo 2": "https://youtu.be/H_aniWehIYY?si=e9WzMGyFSy7PdrAj",
                "Vídeo 3": "https://youtu.be/sGGlQ9yJQNg?si=LVeN5zjZ153uksLW",
                "Vídeo 4": "https://youtu.be/sGGlQ9yJQNg?si=ZxjJ34_4Z13MUL-g",
                "Vídeo 5": "https://youtu.be/TmayKMV0bJY?si=Zb99BwXuFyDDJ-tN"
            }

            st.markdown("""
                <div class="box-container" style="margin-bottom: 0;">
                    <div class="box-title">
                        <span>🎬 VÍDEO DE FUNDO DA TV</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            video_escolhido = st.selectbox("Selecione o vídeo de fundo:", list(videos_disponiveis.keys()), label_visibility="collapsed")
            url_video_selecionado = videos_disponiveis[video_escolhido]

            if st.button("Iniciar Vídeo Clipe Tela", use_container_width=True, type="primary"):
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

    # 3. SE ESTIVER PENDENTE / À ESPERA DE APROVAÇÃO
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

    # 4. TELA INICIAL: NOVO REGISTO OU ENTRAR COM SESSÃO ATIVA
    st.markdown("<h2 style='text-align: center; color: #eab308;'>Área do Prestador</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a1a1aa; margin-bottom: 25px;'>Faça o seu registo de acesso ou entre com os seus dados se já tiver uma sessão ativa.</p>", unsafe_allow_html=True)

    modo_acesso = st.radio("Escolha a opção:", ["Novo Registo", "Já estou online / Entrar com Nome e Telefone"], horizontal=True)

    if modo_acesso == "Novo Registo":
        with st.form("form_registo_prestador"):
            nome = st.text_input("Nome Completo")
            telefone = st.text_input("Telemóvel / Telefone")
            estabelecimento = st.text_input("Estabelecimento (Local onde vai prestar o serviço)")
            
            contrato = st.selectbox("Escolha o Contrato", [
                "1 Hora - 12.000,00 Kwanzaas", 
                "2 Horas - 17.000,00 Kwanzaas",
                "3 Horas - 20.000,00 Kwanzaas"
            ])
            
            submitted = st.form_submit_button("Submeter Pedido", use_container_width=True)
            
            if submitted:
                if nome.strip() and telefone.strip():
                    token_gerado = f"token_{int(time.time())}"
                    
                    if "1 Hora" in contrato:
                        segundos_contrato = 3600
                    elif "2 Horas" in contrato:
                        segundos_contrato = 7200
                    else:
                        segundos_contrato = 10800

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
            st.markdown("#### Entrar com Sessão Ativa")
            login_nome = st.text_input("Nome Registado")
            login_telefone = st.text_input("Telemóvel / Telefone Registado")
            
            btn_entrar = st.form_submit_button("Aceder ao Painel", use_container_width=True)
            
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
                        st.error("Não foi encontrado nenhum registo ativo com este Nome e Telemóvel. Verifique os dados ou faça um novo registo.")
                else:
                    st.error("Por favor, insira o seu Nome e Telemóvel para entrar.")

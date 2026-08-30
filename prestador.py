import streamlit as st
import time
from datetime import datetime
from db import guardar_prestador, obter_prestadores

def render():
    if "pedido_submetido" not in st.session_state:
        st.session_state.pedido_submetido = False
        st.session_state.token_prestador = None
        st.session_state.estado_pedido = "pendente"
    if "aprovado" not in st.session_state:
        st.session_state.aprovado = False

    if st.session_state.pedido_submetido and st.session_state.token_prestador:
        prestadores = obter_prestadores()
        prestador_atual = next((p for p in prestadores if p.get("token") == st.session_state.token_prestador), None)
        
        if prestador_atual:
            status_atual = prestador_atual.get("status_str", "pendente")
            st.session_state.estado_pedido = status_atual
            
            if status_atual == "aprovado":
                st.session_state.aprovado = True

    # 1. SE ESTIVER APROVADO: Mostra o painel operacional e interrompe o fluxo com return
    if st.session_state.get("aprovado", False) or st.session_state.get("estado_pedido") == "aprovado":
        st.markdown("""
            <div style="border: 2px solid #eab308; background-color: #0f0f11; padding: 25px; border-radius: 12px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="color: #eab308; margin: 0;">Painel Operacional — FF Karaoke</h2>
                        <p style="color: #a1a1aa; margin: 5px 0 0 0;">Gestão de sala, fila de reprodução e links dedicados em tempo real.</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        tab_fila, tab_definicoes = st.tabs(["🎵 Fila de Reprodução & Links", "⚙️ Definições / Vídeo de Fundo"])
        
        with tab_fila:
            st.info("O seu sistema está ativo e a escutar novos pedidos de música dos clientes.")
            
            # --- GERAR URLS BASE ROBUSTAS ---
            try:
                host = st.context.headers.get("Host", "")
                if host:
                    protocol = "http" if "localhost" in host or "127.0.0.1" in host else "https"
                    url_cliente = f"{protocol}://{host}/?view=client_register"
                    url_tela = f"{protocol}://{host}/?view=client_screen"
                else:
                    raise ValueError("Host vazio")
            except Exception:
                # Fallback padrão caso o contexto de headers falhe
                url_cliente = "http://localhost:8501/?view=client_register"
                url_tela = "http://localhost:8501/?view=client_screen"

            col_links, col_qr = st.columns([2, 1])
            with col_links:
                st.markdown("##### 🔗 Links Dedicados de Acesso")
                st.text_input("1. LINK DO CLIENTE (Registo e Pedido de Música)", value=url_cliente, disabled=True)
                st.text_input("2. LINK DA TELA DE TV / REPRODUÇÃO (Fundo e Videoclipes)", value=url_tela, disabled=True)
            with col_qr:
                st.markdown("##### 📱 QR Code Clientes")
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=140x140&data={url_cliente}", width=140)

            st.markdown("---")
            st.markdown("#### 📋 Estado da Fila e Controlo de Reprodução")
            
            st.markdown("""
                <div style="background-color: #18181b; border: 1px solid #eab308; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 20px;">
                    <p style="color: #d4d4d8; font-weight: bold; margin: 0;">NENHUM PEDIDO NA LISTA NESTE MOMENTO.<br>À ESPERA DE NOVOS PEDIDOS...</p>
                </div>
            """, unsafe_allow_html=True)

            col_ctrl1, col_ctrl2 = st.columns(2)
            with col_ctrl1:
                if st.button("▶ Play", use_container_width=True):
                    st.toast("A reproduzir...")
            with col_ctrl2:
                if st.button("⏹ Stop", use_container_width=True):
                    st.toast("Reprodução parada.")

        with tab_definicoes:
            st.markdown("#### 🎬 Configuração de Vídeo Clipe de Fundo para a Tela")
            st.write("Selecione o vídeo que ficará a passar no fundo da tela de projeção do seu karaoke:")

            videos_disponiveis = {
                "Vídeo 1 (Oficial)": "https://youtu.be/cQ4MD7gOBmc?si=5wzaxysiHSEwn9QT",
                "Vídeo 2": "https://youtu.be/H_aniWehIYY?si=e9WzMGyFSy7PdrAj",
                "Vídeo 3": "https://youtu.be/sGGlQ9yJQNg?si=LVeN5zjZ153uksLW",
                "Vídeo 4": "https://youtu.be/sGGlQ9yJQNg?si=ZxjJ34_4Z13MUL-g",
                "Vídeo 5": "https://youtu.be/TmayKMV0bJY?si=Zb99BwXuFyDDJ-tN"
            }

            video_escolhido = st.selectbox("Escolha o Vídeo Clipe de Fundo:", list(videos_disponiveis.keys()))
            url_video_selecionado = videos_disponiveis[video_escolhido]

            if st.button("Guardar Vídeo de Fundo", type="primary"):
                if st.session_state.token_prestador:
                    prestadores = obter_prestadores()
                    for p in prestadores:
                        if p.get("token") == st.session_state.token_prestador:
                            p["video_fundo"] = url_video_selecionado
                            guardar_prestador(p)
                    st.success("Vídeo de fundo atualizado com sucesso para a sua tela!")

            st.divider()
            st.markdown("#### Gestão de Sessão")
            st.write("Pode encerrar a sua sessão de atendimento a qualquer momento.")
            
            if st.button("Terminar Sessão / Sair do Painel", use_container_width=True):
                st.session_state.pedido_submetido = False
                st.session_state.token_prestador = None
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()
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

    # 3. SE ESTIVER PENDENTE / À ESPERA
    if st.session_state.pedido_submetido:
        st.markdown("""
            <style>
                @keyframes girarHorario {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                @keyframes girarAntiHorario {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(-360deg); }
                }
                .circulo-externo {
                    width: 140px;
                    height: 140px;
                    border-radius: 50%;
                    border: 2px dashed #ef4444;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    position: relative;
                    animation: girarHorario 10s linear infinite;
                }
                .circulo-interno {
                    width: 100px;
                    height: 100px;
                    border-radius: 50%;
                    border: 2px dashed #eab308;
                    display: flex;
                    justify-content: center;
                    align-items: center;
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

    # 4. CASO CONTRÁRIO (Formulário de Registo)
    st.markdown("<h2 style='text-align: center; color: #eab308;'>Cadastramento</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a1a1aa; margin-bottom: 30px;'>Preencha os dados abaixo para submeter o seu pedido de acesso ao sistema.</p>", unsafe_allow_html=True)

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
                    "video_fundo": "https://youtu.be/cQ4MD7gOBmc?si=5wzaxysiHSEwn9QT"
                }
                
                guardar_prestador(novo_prestador)
                
                st.session_state.pedido_submetido = True
                st.session_state.token_prestador = token_gerado
                st.session_state.estado_pedido = "pendente"
                st.session_state.aprovado = False
                st.rerun()
            else:
                st.error("Por favor, preencha pelo menos o Nome Completo e o Telefone.")

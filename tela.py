import streamlit as st
import streamlit.components.v1 as components
from db import obter_prestadores, obter_pedidos_musicas

def render():
    st.markdown("""
        <style>
            .stApp {
                background-color: #0c0c0e;
                color: #ffffff;
            }
            header[data-testid="stHeader"] {
                background-color: transparent !important;
            }
            .block-container {
                max-width: 100% !important;
                padding: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Recuperar token da URL
    query_params = st.query_params
    token = query_params.get("token", None)
    token_str = str(token) if token else ""

    # Fragmento unificado de alta responsividade (atualiza a cada 2 segundos)
   @st.fragment(run_every=2)
    def renderizar_tela_unificada():
        try:
            prestadores = obter_prestadores() or []
        except Exception:
            prestadores = []

        prestador_ativo = None
        if token_str and token_str != "None":
            prestador_ativo = next((p for p in prestadores if str(p.get("token")) == token_str), None)
        
        if not prestador_ativo and prestadores:
            # Fallback: se não houver token na URL, pega o primeiro que tenha vídeo ou o primeiro aprovado
            prestador_ativo = next((p for p in prestadores if p.get("video_fundo")), prestadores[0])

        token_prestador_ativo = str(prestador_ativo.get("token", "")) if prestador_ativo else ""
        
        # 1. TENTA LER PRIMEIRO DA SESSÃO GLOBAL (caso estejam na mesma sessão ou partilhadas)
        video_fundo = ""
        if token_prestador_ativo and st.session_state.get(f"video_global_{token_prestador_ativo}"):
            video_fundo = st.session_state.get(f"video_global_{token_prestador_ativo}")
        elif st.session_state.get("video_global_atual"):
            video_fundo = st.session_state.get("video_global_atual")
        
        # 2. SE NÃO ESTIVER NA SESSÃO, LÊ DIRETAMENTE DA BASE DE DADOS DO PRESTADOR ATIVO
        if not video_fundo and prestador_ativo:
            video_fundo = prestador_ativo.get("video_fundo", "")

        nome_prestador = prestador_ativo.get("nome", "Desconhecido") if prestador_ativo else "Nenhum"

        # Extração limpa do ID do YouTube (suporta links normais e youtu.be)
        embed_url = ""
        if video_fundo:
            cleaned_url = video_fundo.strip()
            if "youtu.be/" in cleaned_url:
                try:
                    video_id = cleaned_url.split("youtu.be/")[1].split("?")[0].split("&")[0]
                    embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&controls=0&loop=1&playlist={video_id}"
                except:
                    pass
            elif "watch?v=" in cleaned_url:
                try:
                    video_id = cleaned_url.split("watch?v=")[1].split("&")[0]
                    embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&controls=0&loop=1&playlist={video_id}"
                except:
                    pass

        try:
            todos_pedidos = obter_pedidos_musicas() or []
        except Exception:
            todos_pedidos = []

        token_prestador_ativo = str(prestador_ativo.get("token", "")) if prestador_ativo else ""

        lista_pedidos = [
            p for p in todos_pedidos 
            if p.get("status", "pendente") == "pendente" 
            and (str(p.get("token_prestador", "")) in ["", "None", token_prestador_ativo])
        ]

        itens_html = ""
        if lista_pedidos:
            for idx, pedido in enumerate(lista_pedidos):
                musica = pedido.get("musica", "Desconhecida")
                cantor = pedido.get("cantor", "Convidado")
                itens_html += f"""
                <div style="background-color: rgba(28, 28, 36, 0.92); border: 1px solid #3f3f46; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; text-align: left;">
                    <div style="color: #eab308; font-size: 11px; font-weight: bold;">#{idx+1} na Fila</div>
                    <div style="color: #ffffff; font-size: 14px; font-weight: bold; margin-top: 2px;">🎵 {musica}</div>
                    <div style="color: #c084fc; font-size: 12px; margin-top: 2px;">🎤 Cantor: <b>{cantor}</b></div>
                </div>
                """
        else:
            itens_html = """
            <div style="text-align: center; color: #a1a1aa; padding: 20px;">
                <div style="font-size: 28px; margin-bottom: 5px;">🎤</div>
                <div style="font-size: 14px;">Sem músicas na fila.</div>
                <div style="font-size: 11px; margin-top: 3px;">Faça o seu pedido pelo QR Code!</div>
            </div>
            """

        if embed_url:
            conteudo_fundo = f"""
            <iframe class="video-fundo" src="{embed_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
            """
        else:
            conteudo_fundo = f"""
            <div class="sem-video">
                <div>📺 Aguardando vídeo do prestador...</div>
                <div style="font-size: 12px; color: #71717a; margin-top: 10px;">Link atual guardado: {video_fundo if video_fundo else 'Nenhum'}</div>
            </div>
            """

        html_completo = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{
                background-color: #0c0c0e;
                margin: 0;
                padding: 0;
                font-family: sans-serif;
                overflow: hidden;
                width: 100vw;
                height: 100vh;
            }}
            .video-fundo {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: 1;
                border: none;
                pointer-events: auto;
            }}
            .sem-video {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: #eab308;
                font-size: 26px;
                font-weight: bold;
                text-align: center;
                background: #0c0c0e;
                padding: 20px;
            }}
            .playlist-overlay {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 440px;
                max-height: 70vh;
                background: rgba(18, 18, 22, 0.94);
                border: 2px solid #eab308;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 0 50px rgba(0,0,0,0.95);
                backdrop-filter: blur(12px);
                display: flex;
                flex-direction: column;
                box-sizing: border-box;
                z-index: 99999;
                pointer-events: auto;
            }}
            .playlist-scroll {{
                overflow-y: auto;
                max-height: 52vh;
                padding-right: 4px;
            }}
            .playlist-scroll::-webkit-scrollbar {{
                width: 6px;
            }}
            .playlist-scroll::-webkit-scrollbar-thumb {{
                background: #3f3f46;
                border-radius: 4px;
            }}
        </style>
        </head>
        <body>
            {conteudo_fundo}

            <div class="playlist-overlay">
                <div style="color: #eab308; font-weight: bold; font-size: 16px; margin-bottom: 12px; border-bottom: 2px solid #3f3f46; padding-bottom: 8px; text-align: center; text-transform: uppercase;">
                    🎶 Playlist · Fila ({len(lista_pedidos)})
                </div>
                <div class="playlist-scroll">
                    {itens_html}
                </div>
            </div>
        </body>
        </html>
        """
        components.html(html_completo, height=850, scrolling=False)

    renderizar_tela_unificada()

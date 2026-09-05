import streamlit as st
import streamlit.components.v1 as components
import time
from db import obter_prestadores, obter_pedidos_musicas

def render():
    # Configuração da página para ocupar o espaço máximo e remover margens excessivas
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
                padding: 0.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Recuperar token da URL se houver
    query_params = st.query_params
    token = query_params.get("token", None)

    # Procurar prestador ativo
    prestadores = obter_prestadores() or []
    prestador_ativo = None
    if token:
        prestador_ativo = next((p for p in prestadores if p.get("token") == token), None)
    if not prestador_ativo:
        prestador_ativo = next((p for p in prestadores if p.get("status_str") == "aprovado"), None)

    video_fundo = prestador_ativo.get("video_fundo", "") if prestador_ativo else ""
    token_str = str(token or (prestador_ativo.get("token") if prestador_ativo else ""))

    # Converte link do YouTube para formato incorporado com SOM ATIVO (mute=0)
    embed_url = ""
    if video_fundo:
        if "youtu.be/" in video_fundo:
            video_id = video_fundo.split("youtu.be/")[1].split("?")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&loop=1&playlist={video_id}&controls=0"
        elif "watch?v=" in video_fundo:
            video_id = video_fundo.split("watch?v=")[1].split("&")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&loop=1&playlist={video_id}&controls=0"

    @st.fragment(run_every=3)
    def renderizar_tela_completa():
        try:
            todos_pedidos = obter_pedidos_musicas() or []
        except Exception:
            todos_pedidos = []

        # Filtrar pedidos pendentes
        lista_pedidos = [
            p for p in todos_pedidos 
            if p.get("status", "pendente") == "pendente" 
            and (str(p.get("token_prestador", "")) in ["", "None", token_str])
        ]

        itens_html = ""
        if lista_pedidos:
            for idx, pedido in enumerate(lista_pedidos):
                musica = pedido.get("musica", "Desconhecida")
                cantor = pedido.get("cantor", "Convidado")
                itens_html += f"""
                <div style="background-color: rgba(28, 28, 36, 0.85); border: 1px solid #3f3f46; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; text-align: left; backdrop-filter: blur(4px);">
                    <div style="color: #eab308; font-size: 11px; font-weight: bold;">#{idx+1} na Fila</div>
                    <div style="color: #ffffff; font-size: 14px; font-weight: bold; margin-top: 2px;">🎵 {musica}</div>
                    <div style="color: #c084fc; font-size: 12px; margin-top: 2px;">🎤 Cantor: <b>{cantor}</b></div>
                </div>
                """
        else:
            itens_html = """
            <div style="text-align: center; color: #a1a1aa; margin-top: 30px;">
                <div style="font-size: 28px; margin-bottom: 5px;">🎤</div>
                <div style="font-size: 14px;">Sem músicas na fila.</div>
                <div style="font-size: 11px; margin-top: 3px;">Faça o seu pedido pelo QR Code!</div>
            </div>
            """

        html_conteudo = f"""
        <html>
        <head>
        <style>
            body {{
                background-color: #000000;
                color: #ffffff;
                font-family: sans-serif;
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
            .video-background {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: 1;
                border: none;
            }}
            .playlist-overlay {{
                position: absolute;
                top: 20px;
                right: 20px;
                width: 340px;
                height: calc(100vh - 40px);
                background: rgba(18, 18, 22, 0.80);
                border: 2px solid #eab308;
                border-radius: 12px;
                padding: 15px;
                z-index: 10;
                box-shadow: 0 0 25px rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(8px);
                display: flex;
                flex-direction: column;
                box-sizing: border-box;
            }}
            .playlist-scroll {{
                overflow-y: auto;
                flex-grow: 1;
                padding-right: 4px;
            }}
            /* Estilo da barra de rolagem */
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
            <!-- Vídeo de Fundo a ocupar o ecrã inteiro -->
            <iframe class="video-background" src="{embed_url}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

            <!-- Playlist Flutuante por cima do vídeo no canto direito -->
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
        components.html(html_conteudo, height=820, scrolling=False)

    renderizar_tela_completa()

    # Atualização automática da página a cada 3 segundos
    time.sleep(3)
    st.rerun()

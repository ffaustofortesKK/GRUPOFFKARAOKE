import streamlit as st
import streamlit.components.v1 as components
import time
from db import obter_prestadores, obter_pedidos_musicas

def render():
    st.markdown("""
        <style>
            .stApp {
                background-color: #000000;
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
    
    query_params = st.query_params
    token = query_params.get("token", None)

    prestadores = obter_prestadores() or []
    prestador_ativo = None
    if token:
        prestador_ativo = next((p for p in prestadores if p.get("token") == token), None)
    if not prestador_ativo:
        prestador_ativo = next((p for p in prestadores if p.get("status_str") == "aprovado"), None)

    video_fundo = prestador_ativo.get("video_fundo", "") if prestador_ativo else ""
    token_str = str(token or (prestador_ativo.get("token") if prestador_ativo else ""))

    embed_url = ""
    if video_fundo:
        if "youtu.be/" in video_fundo:
            video_id = video_fundo.split("youtu.be/")[1].split("?")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&loop=1&playlist={video_id}&controls=0"
        elif "watch?v=" in video_fundo:
            video_id = video_fundo.split("watch?v=")[1].split("&")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&loop=1&playlist={video_id}&controls=0"

    # 1. Renderiza o vídeo de fundo fixo UMA ÚNICA VEZ (para nunca reiniciar quando a playlist atualizar)
    if embed_url:
        st.markdown(f"""
            <iframe style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1; border: none;" 
                    src="{embed_url}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
            </iframe>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #000000; z-index: 1; display: flex; justify-content: center; align-items: center; color: #eab308; font-size: 24px; font-family: sans-serif;">
                A aguardar que o prestador inicie o vídeo clipe...
            </div>
        """, unsafe_allow_html=True)

    # 2. Fragmento isolado que atualiza apenas a playlist a cada 3 segundos SEM mexer no vídeo de fundo
    @st.fragment(run_every=3)
    def renderizar_playlist_central():
        try:
            todos_pedidos = obter_pedidos_musicas() or []
        except Exception:
            todos_pedidos = []

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
                <div style="background-color: rgba(20, 20, 25, 0.55); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; text-align: left; backdrop-filter: blur(2px);">
                    <div style="color: #eab308; font-size: 11px; font-weight: bold;">#{idx+1} na Fila</div>
                    <div style="color: #ffffff; font-size: 14px; font-weight: bold; margin-top: 2px;">🎵 {musica}</div>
                    <div style="color: #d8b4fe; font-size: 12px; margin-top: 2px;">🎤 Cantor: <b>{cantor}</b></div>
                </div>
                """
        else:
            itens_html = """
            <div style="text-align: center; color: #d4d4d8; padding: 20px;">
                <div style="font-size: 24px; margin-bottom: 5px;">🎤</div>
                <div style="font-size: 13px;">Sem músicas na fila de momento.</div>
            </div>
            """

        html_playlist = f"""
        <html>
        <head>
        <style>
            body {{
                background-color: transparent;
                color: #ffffff;
                font-family: sans-serif;
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
            .playlist-center {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 450px;
                max-height: 75vh;
                background: rgba(12, 12, 16, 0.35); /* Fundo bem menos fuso / translúcido */
                border: 2px solid rgba(234, 179, 8, 0.8);
                border-radius: 14px;
                padding: 20px;
                box-shadow: 0 0 30px rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(6px); /* Efeito vidro subtil */
                display: flex;
                flex-direction: column;
                box-sizing: border-box;
                z-index: 999;
            }}
            .playlist-scroll {{
                overflow-y: auto;
                max-height: 60vh;
                padding-right: 4px;
            }}
            .playlist-scroll::-webkit-scrollbar {{
                width: 5px;
            }}
            .playlist-scroll::-webkit-scrollbar-thumb {{
                background: rgba(234, 179, 8, 0.5);
                border-radius: 4px;
            }}
        </style>
        </head>
        <body>
            <div class="playlist-center">
                <div style="color: #eab308; font-weight: bold; font-size: 16px; margin-bottom: 12px; border-bottom: 1px solid rgba(234, 179, 8, 0.4); padding-bottom: 8px; text-align: center; text-transform: uppercase; letter-spacing: 1px;">
                    🎶 Fila de Pedidos ({len(lista_pedidos)})
                </div>
                <div class="playlist-scroll">
                    {itens_html}
                </div>
            </div>
        </body>
        </html>
        """
        components.html(html_playlist, height=850, scrolling=False)

    renderizar_playlist_central()

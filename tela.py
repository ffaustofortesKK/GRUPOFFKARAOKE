import streamlit as st
import streamlit.components.v1 as components
import time
from db import obter_prestadores, obter_pedidos_musicas

def render():
    # Configuração da página para ocupar o espaço máximo de exibição na TV
    st.markdown("""
        <style>
            .stApp {
                background-color: #0c0c0e;
                color: #ffffff;
            }
            .block-container {
                max-width: 100% !important;
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
                padding-left: 1.5rem !important;
                padding-right: 1.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: #eab308; margin-bottom: 10px;'>📺 FFKaraoke · Tela de Exibição (TV)</h1>", unsafe_allow_html=True)
    
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

    # Layout Principal: Esquerda (Vídeo Clipe), Direita (Playlist / Fila de Pedidos)
    col_video, col_playlist = st.columns([1.8, 1])

    with col_video:
        if video_fundo:
            embed_url = video_fundo
            # Converte link do YouTube para formato incorporado com SOM ATIVO (mute=0)
            if "youtu.be/" in video_fundo:
                video_id = video_fundo.split("youtu.be/")[1].split("?")[0]
                embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&loop=1&playlist={video_id}"
            elif "watch?v=" in video_fundo:
                video_id = video_fundo.split("watch?v=")[1].split("&")[0]
                embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0&loop=1&playlist={video_id}"

            st.markdown(f"""
                <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; border-radius: 12px; border: 2px solid #eab308; box-shadow: 0 0 20px rgba(234, 179, 8, 0.2);">
                    <iframe src="{embed_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="position: relative; width: 100%; min-height: 56.25vh; display: flex; flex-direction: column; justify-content: center; align-items: center; border: 2px solid #eab308; border-radius: 12px; padding: 30px; background: #121216; box-shadow: 0 0 20px rgba(234, 179, 8, 0.2); text-align: center;">
                    <div style="color: #eab308; font-size: 36px; font-weight: bold; margin-bottom: 20px;">🎵 A Tocar Agora</div>
                    <div style="color: #d4d4d8; font-size: 22px; margin-bottom: 10px;">Nenhum vídeo de fundo configurado.</div>
                </div>
            """, unsafe_allow_html=True)

    with col_playlist:
        @st.fragment(run_every=3)
        def renderizar_playlist_lateral():
            try:
                todos_pedidos = obter_pedidos_musicas() or []
            except Exception:
                todos_pedidos = []

            # Filtrar pedidos pendentes do prestador correspondente
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
                    <div style="background-color: #1c1c24; border: 1px solid #3f3f46; border-radius: 8px; padding: 12px 15px; margin-bottom: 10px; text-align: left;">
                        <div style="color: #eab308; font-size: 12px; font-weight: bold;">#{idx+1} na Fila</div>
                        <div style="color: #ffffff; font-size: 15px; font-weight: bold; margin-top: 2px;">🎵 {musica}</div>
                        <div style="color: #c084fc; font-size: 13px; margin-top: 2px;">🎤 Cantor: <b>{cantor}</b></div>
                    </div>
                    """
            else:
                itens_html = """
                <div style="text-align: center; color: #71717a; margin-top: 50px;">
                    <div style="font-size: 32px; margin-bottom: 10px;">🎤</div>
                    <div style="font-size: 16px;">Sem músicas na fila de momento.</div>
                    <div style="font-size: 13px; margin-top: 5px;">Faça o seu pedido através do QR Code!</div>
                </div>
                """

            html_conteudo = f"""
            <html>
            <head>
            <style>
                body {{
                    background-color: #121216;
                    color: #ffffff;
                    font-family: sans-serif;
                    margin: 0;
                    padding: 0;
                }}
                .playlist-container {{
                    border: 2px solid #eab308;
                    border-radius: 12px;
                    padding: 15px;
                    height: 72vh;
                    overflow-y: auto;
                    box-shadow: 0 0 20px rgba(234, 179, 8, 0.2);
                    background-color: #121216;
                    box-sizing: border-box;
                }}
            </style>
            </head>
            <body>
                <div class="playlist-container">
                    <div style="color: #eab308; font-weight: bold; font-size: 18px; margin-bottom: 15px; border-bottom: 2px solid #3f3f46; padding-bottom: 8px; text-align: center;">
                        🎶 PLAYLIST · FILA ({len(lista_pedidos)})
                    </div>
                    {itens_html}
                </div>
            </body>
            </html>
            """
            components.html(html_conteudo, height=540, scrolling=False)

        renderizar_playlist_lateral()

    # Atualização automática da página a cada 3 segundos
    time.sleep(3)
    st.rerun()

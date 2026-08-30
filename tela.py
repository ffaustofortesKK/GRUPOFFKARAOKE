import streamlit as st
import time
from db import obter_prestadores

def render():
    # Configuração da página para ocupar o espaço máximo de exibição na TV
    st.markdown("""
        <style>
            .stApp {
                background-color: #0c0c0e;
                color: #ffffff;
            }
            .tv-container {
                position: relative;
                width: 100%;
                min-height: 80vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                border: 2px solid #eab308;
                border-radius: 12px;
                padding: 30px;
                background: #121216;
                box-shadow: 0 0 20px rgba(234, 179, 8, 0.2);
                text-align: center;
            }
            .tv-title {
                color: #eab308;
                font-size: 36px;
                font-weight: bold;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            .tv-status {
                color: #d4d4d8;
                font-size: 22px;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: #eab308;'>📺 FFKaraoke · Tela de Exibição (TV)</h1>", unsafe_allow_html=True)
    st.write("Esta tela exibe as músicas a cantar em direto para o público e o vídeo de fundo selecionado pelo prestador.")
    st.divider()

    # Procurar se existe algum prestador aprovado para carregar o vídeo de fundo
    prestadores = obter_prestadores()
    prestador_ativo = next((p for p in prestadores if p.get("status_str") == "aprovado"), None)

    video_fundo = ""
    if prestador_ativo:
        video_fundo = prestador_ativo.get("video_fundo", "")

    # Layout de exibição da TV
    if video_fundo:
        st.markdown(f"""
            <div style="margin-bottom: 20px; border: 1px solid #3f3f46; border-radius: 8px; overflow: hidden;">
                <p style="background: #18181b; color: #eab308; padding: 10px; margin: 0; font-weight: bold;">🎬 Vídeo de Fundo Ativo</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Converte link do YouTube para formato incorporado caso necessário
        embed_url = video_fundo
        if "youtu.be/" in video_fundo:
            video_id = video_fundo.split("youtu.be/")[1].split("?")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}"
        elif "watch?v=" in video_fundo:
            video_id = video_fundo.split("watch?v=")[1].split("&")[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}"

        st.markdown(f"""
            <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; border-radius: 8px; margin-bottom: 20px;">
                <iframe src="{embed_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="tv-container">
                <div class="tv-title">🎵 A Tocar Agora</div>
                <div class="tv-status">Nada em reprodução no momento.</div>
                <p style="color: #71717a; font-size: 16px; margin-top: 15px;">A aguardar seleções e pedidos do público...</p>
            </div>
        """, unsafe_allow_html=True)

    # Atualiza automaticamente a tela a cada 3 segundos para refletir mudanças do prestador
    time.sleep(3)
    st.rerun()

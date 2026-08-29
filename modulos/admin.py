import streamlit as st
import urllib.parse
import time
from modulos.db import obter_prestadores, guardar_prestador

def formatarTempo(segundos: int) -> str:
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    secs = segundos % 60
    if horas > 0:
        return f"{horas}h {minutos}m"
    return f"{minutos}m {secs}s"

def render():
    st.title("Painel de Administração — FF Karaoke")
    st.caption("Gestão de acessos e controlos do programa FFK")
    st.divider()

    if not st.session_state.get("logged", False):
        st.subheader("🔒 Área restrita")
        with st.form("login_form"):
            password_input = st.text_input("Palavra-passe de administrador", type="password")
            submit_login = st.form_submit_button("Entrar")
            
            if submit_login:
                if password_input == "admin":
                    st.session_state.logged = True
                    st.rerun()
                else:
                    st.error("Palavra-passe incorreta.")
    else:
        col_l1, col_l2 = st.columns([8, 2])
        with col_l2:
            if st.button("Terminar sessão"):
                st.session_state.logged = False
                st.rerun()

        prestadores_atuais = obter_prestadores()

        aba1, aba2, aba3, aba4 = st.tabs([
            "🔗 Link e QR Registo", 
            "⏳ Pedidos e Aprovação", 
            "📊 Gestão Total", 
            "📈 Relatórios e Estatísticas"
        ])

        with aba1:
            st.subheader("Portal do Prestadores")
            st.write("Partilhe este link ou o QR Code com os prestadores para que possam submeter os seus dados.")
            
            try:
                base_url = st.context.headers.get("Host", "")
                if base_url:
                    if "localhost" in base_url or "127.0.0.1" in base_url:
                        base_url = f"http://{base_url}/?view=prestador"
                    else:
                        base_url = f"https://{base_url}/?view=prestador"
                else:
                    raise Exception()
            except Exception:
                base_url = "https://grupoffkaraoke.streamlit.app/?view=prestador"
            
            st.markdown(f"""
                <div style="border: 2px solid #eab308; border-radius: 8px; padding: 15px; background-color: #18181b; margin-bottom: 20px;">
                    <p style="color: #eab308; font-weight: bold; margin-bottom: 5px;">Link Direto de Registo:</p>
                    <a href="{base_url}" target="_blank" style="color: #facc15; font-size: 16px; word-break: break-all;">{base_url}</a>
                </div>
            """, unsafe_allow_html=True)

            col_q1, col_q2 = st.columns([2, 5])
            with col_q1:
                url_encoded = urllib.parse.quote(base_url)
                qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={url_encoded}"
                st.image(qr_api_url, width=180, caption="QR Code de Registo")
                
            with col_q2:
                st.markdown("""
                    <div style="padding-top: 20px;">
                        <p style="color: #d4d4d8; font-size: 15px;">
                            Os prestadores que acederem a este link ou lerem o QR Code poderão preencher o nome, contacto, estabelecimento e tempo pretendido para a prestação do serviço de karaoke.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

        with aba2:
            pendentes = [p for p in prestadores_atuais if p.get("status_str", "pendente") == "pendente"]
            st.subheader(f"⏳ Registos pendentes ({len(pendentes)})")
            
            if not pendentes:
                st.info("Nenhum registo à espera de aprovação. O painel verifica novos pedidos automaticamente...")
                # Faz uma verificação automática suave a cada 5 segundos se não houver pendentes
                time.sleep(5)
                st.rerun()
            else:
                for p in pendentes:
                    with st.container(border=True):
                        st.markdown(f"**{p['nome']}**")
                        st.caption(f"Telefone: {p['telefone']} · Estabelecimento: {p.get('estabelecimento', 'N/A')} · Plano: {p['plano']} · Token: {p['token']}")
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button("✅ Aprovar", key=f"aprov_{p['token']}"):
                                p["approved"] = True
                                p["status_str"] = "aprovado"
                                guardar_prestador(p)
                                if "historico" not in st.session_state:
                                    st.session_state.historico = []
                                st.session_state.historico.append({"acao": "Aprovação", "detalhe": f"Prestador {p['nome']} aprovado.", "data": "Hoje"})
                                st.rerun()
                                
                        with col_b:
                            if st.button("❌ Recusar", key=f"rec_{p['token']}"):
                                p["approved"] = False
                                p["status_str"] = "recusado"
                                guardar_prestador(p)
                                if "historico" not in st.session_state:
                                    st.session_state.historico = []
                                st.session_state.historico.append({"acao": "Recusa", "detalhe": f"Prestador {p['nome']} foi recusado.", "data": "Hoje"})
                                st.rerun()

        with aba3:
            ativos = [p for p in prestadores_atuais if p.get("status_str") == "aprovado"]
            st.subheader(f"🟢 Prestadores Ativos / Online ({len(ativos)})")
            if not ativos:
                st.info("Nenhum prestador ativo no momento.")
            else:
                for p in ativos:
                    with st.container(border=True):
                        tempo_str = formatarTempo(p.get("segundos_restantes", 0))
                        st.markdown(f"**{p['nome']}** — Estabelecimento: {p.get('estabelecimento', 'N/A')} — Plano: {p['plano']}")
                        st.write(f"Tempo restante: **{tempo_str}** | Token: `{p['token']}`")
                        if st.button("Suspender Acesso", key=f"susp_{p['token']}"):
                            p["approved"] = False
                            p["status_str"] = "suspenso"
                            guardar_prestador(p)
                            st.rerun()

        with aba4:
            st.subheader("📊 Relatórios e Estatísticas Gerais")
            if "historico" in st.session_state and st.session_state.historico:
                for h in st.session_state.historico:
                    st.markdown(f"- **[{h['data']}] {h['acao']}**: {h['detalhe']}")
            else:
                st.info("Nenhum registo estatístico recente.")

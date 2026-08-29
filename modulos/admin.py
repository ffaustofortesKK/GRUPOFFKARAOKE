import streamlit as st
import urllib.parse
import time
from datetime import datetime
from modulos.db import obter_prestadores, guardar_prestador

def formatarTempoDecrescente(segundos: int) -> str:
    if segundos <= 0:
        return "00m 00s"
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    secs = segundos % 60
    if horas > 0:
        return f"{horas:02d}h {minutos:02d}m {secs:02d}s"
    return f"{minutos:02d}m {secs:02d}s"

def render():
    st.title("Painel de Administração — FF Karaoke")
    st.caption("Gestão de acessos e controlos do programa FFK")

    if not st.session_state.get("logged", False):
        st.divider()
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
        prestadores_atuais = obter_prestadores()
        
        # Filtros estritos para garantir separação correta
        ativos = [p for p in prestadores_atuais if p.get("status_str") == "aprovado"]
        qtd_ativos = len(ativos)
        
        pendentes_lista = [p for p in prestadores_atuais if p.get("status_str") == "pendente"]
        qtd_pendentes = len(pendentes_lista)

        # Indicador de Activos com o tamanho duplicado
        col_topo_esq, col_topo_dir = st.columns([8, 3])
        with col_topo_dir:
            st.markdown(f"""
                <div style="text-align: right; padding-bottom: 5px;">
                    <span style="color: #eab308; font-weight: bold; font-size: 30px;">Activos:</span> 
                    <span style="color: #22c55e; font-weight: bold; font-size: 52px;">{qtd_ativos}</span>
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Linha do botão Terminar sessão por baixo da linha divisoria
        col_l1, col_l2 = st.columns([9, 2])
        with col_l2:
            if st.button("Terminar sessão", use_container_width=True):
                st.session_state.logged = False
                st.rerun()

        # Alerta numérico por cima do título da Aba Pedidos e Aprovação
        if qtd_pendentes > 0:
            titulo_aba_pendentes = f"⏳ Pedidos ({qtd_pendentes})"
        else:
            titulo_aba_pendentes = "⏳ Pedidos e Aprovação"

        aba1, aba2, aba3, aba4 = st.tabs([
            "🔗 Link e QR Registo", 
            titulo_aba_pendentes, 
            "🟢 Prestadores Activos", 
            "📈 Relatórios e Estatísticas"
        ])

        with aba1:
            st.subheader("Portal dos Prestadores")
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
                            Os prestadores que acederem a este link ou lerem o QR Code poderão preencher o nome, contacto, estabelecimento e o contrato pretendido para a prestação do serviço de karaoke.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

        with aba2:
            if qtd_pendentes > 0:
                st.markdown(f"""
                    <div style="background-color: #fef08a; color: #713f12; padding: 8px 15px; border-radius: 6px; font-weight: bold; margin-bottom: 15px; display: inline-block;">
                        ⚠️ Atenção: Existem {qtd_pendentes} pedido(s) pendente(s) a aguardar aprovação!
                    </div>
                """, unsafe_allow_html=True)
            
            st.subheader(f"⏳ Registos pendentes ({qtd_pendentes})")
            
            if not pendentes_lista:
                st.info("Nenhum pedido pendente de momento.")
            else:
                for p in pendentes_lista:
                    with st.container(border=True):
                        st.markdown(f"**{p['nome']}**")
                        st.caption(f"Telefone: {p['telefone']} · Estabelecimento: {p.get('estabelecimento', 'N/A')} · Contrato: {p.get('plano', p.get('contrato', 'N/A'))} · Token: {p['token']}")
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button("✅ Aprovar", key=f"aprov_{p['token']}"):
                                p["approved"] = True
                                p["status_str"] = "aprovado"
                                p["data_pedido"] = p.get("data_pedido", datetime.now().strftime("%d/%m/%Y %H:%M"))
                                guardar_prestador(p)
                                st.rerun()
                                
                        with col_b:
                            if st.button("❌ Recusar", key=f"rec_{p['token']}"):
                                p["approved"] = False
                                p["status_str"] = "recusado"
                                p["data_pedido"] = p.get("data_pedido", datetime.now().strftime("%d/%m/%Y %H:%M"))
                                guardar_prestador(p)
                                st.rerun()

        with aba3:
            st.subheader(f"🟢 Prestadores Activos / Online ({qtd_ativos})")
            
            if not ativos:
                st.info("Nenhum prestador ativo no momento.")
            else:
                dados_tabela = []
                for p in ativos:
                    segundos_restantes = p.get("segundos_restantes", 3600)
                    tempo_formatado = formatarTempoDecrescente(segundos_restantes)
                    
                    dados_tabela.append({
                        "Nome": p['nome'],
                        "Estabelecimento": p.get('estabelecimento', 'N/A'),
                        "Contrato": p.get('plano', p.get('contrato', 'N/A')),
                        "Reforço": p.get('reforco', 'N/A'),
                        "Tempo restante": tempo_formatado
                    })
                
                st.dataframe(dados_tabela, use_container_width=True)
                
                # Relógio a decrementar segundos em tempo real
                time.sleep(1)
                for p in ativos:
                    if p.get("segundos_restantes", 3600) > 0:
                        p["segundos_restantes"] = p.get("segundos_restantes", 3600) - 1
                        guardar_prestador(p)
                st.rerun()

        with aba4:
            st.subheader("📈 Relatórios e Estatísticas Gerais")
            st.write("Registo completo de todas as solicitações e submissões de prestadores:")
            
            dados_historico_tabela = []
            for p in prestadores_atuais:
                status_atual = p.get("status_str", "pendente")
                if status_atual == "aprovado":
                    estado_formatado = "Aprovado"
                elif status_atual == "recusado":
                    estado_formatado = "Recusado"
                elif status_atual == "suspenso":
                    estado_formatado = "Suspenso"
                else:
                    estado_formatado = "Pendente"
                
                dados_historico_tabela.append({
                    "Nome": p.get('nome', 'N/A'),
                    "Contrato": p.get('plano', p.get('contrato', 'N/A')),
                    "Estado": estado_formatado,
                    "Reforço": p.get('reforco', 'N/A'),
                    "Data do contrato": p.get('data_pedido', datetime.now().strftime("%d/%m/%Y %H:%M"))
                })
            
            if dados_historico_tabela:
                st.dataframe(dados_historico_tabela, use_container_width=True)
            else:
                st.info("Nenhum registo estatístico disponível.")

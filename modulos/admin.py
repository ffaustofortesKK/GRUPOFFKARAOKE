import streamlit as st
import urllib.parse
from datetime import datetime
from collections import defaultdict
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
        try:
            prestadores_atuais = obter_prestadores()
            if not isinstance(prestadores_atuais, list):
                prestadores_atuais = []
        except Exception:
            prestadores_atuais = []
        
        # Processa a expiração automática de tempo antes de filtrar
        for p in prestadores_atuais:
            if not isinstance(p, dict):
                continue
            status_str = p.get("status_str", "pendente")
            if status_str == "aprovado":
                segundos = p.get("segundos_restantes", 0)
                if segundos > 0:
                    segundos -= 1
                    p["segundos_restantes"] = segundos
                    if segundos <= 0:
                        p["status_str"] = "expirado"
                        p["approved"] = False
                    guardar_prestador(p)

        ativos = [p for p in prestadores_atuais if isinstance(p, dict) and (p.get("status_str") == "aprovado" or p.get("approved") is True) and p.get("segundos_restantes", 0) > 0]
        qtd_ativos = len(ativos)
        
        # Filtro corrigido e mais abrangente para apanhar todos os pendentes reais
        pendentes_lista = []
        for p in prestadores_atuais:
            if not isinstance(p, dict):
                continue
            status_str = str(p.get("status_str", "")).lower()
            approved_val = p.get("approved")
            
            # É considerado pendente se não estiver explicitamente aprovado, recusado, expirado ou suspenso
            if status_str in ["pendente", ""] and approved_val is not True:
                pendentes_lista.append(p)
            elif approved_val is False and status_str not in ["recusado", "expirado", "suspenso"]:
                pendentes_lista.append(p)
                
        qtd_pendentes = len(pendentes_lista)

        col_topo_esq, col_topo_dir = st.columns([8, 3])
        with col_topo_dir:
            st.markdown(f"""
                <div style="text-align: right; padding-bottom: 5px;">
                    <span style="color: #eab308; font-weight: bold; font-size: 30px;">Activos:</span> 
                    <span style="color: #22c55e; font-weight: bold; font-size: 52px;">{qtd_ativos}</span>
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        col_l1, col_l2 = st.columns([9, 2])
        with col_l2:
            if st.button("Terminar sessão", use_container_width=True):
                st.session_state.logged = False
                st.rerun()

        titulo_aba_pendentes = f"⏳ Pedidos ({qtd_pendentes})" if qtd_pendentes > 0 else "⏳ Pedidos e Aprovação"

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
                        st.markdown(f"**{p.get('nome', 'Sem Nome')}**")
                        st.caption(f"Telefone: {p.get('telefone', 'N/A')} · Estabelecimento: {p.get('estabelecimento', 'N/A')} · Contrato: {p.get('plano', p.get('contrato', 'N/A'))} · Token: {p.get('token', 'N/A')}")
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button("✅ Aprovar", key=f"aprov_{p.get('token', 't')}"):
                                p["approved"] = True
                                p["status_str"] = "aprovado"
                                p["data_pedido"] = p.get("data_pedido", datetime.now().strftime("%d/%m/%Y %H:%M"))
                                guardar_prestador(p)
                                st.rerun()
                                
                        with col_b:
                            if st.button("❌ Recusar", key=f"rec_{p.get('token', 't')}"):
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
                    segundos_restantes = p.get("segundos_restantes", 0)
                    tempo_formatado = formatarTempoDecrescente(segundos_restantes)
                    
                    dados_tabela.append({
                        "Nome": p.get('nome', 'N/A'),
                        "Estabelecimento": p.get('estabelecimento', 'N/A'),
                        "Contrato": p.get('plano', p.get('contrato', 'N/A')),
                        "Reforço": p.get('reforco', 'N/A'),
                        "Tempo restante": tempo_formatado
                    })
                
                st.dataframe(dados_tabela, use_container_width=True)

        with aba4:
            st.subheader("📈 Relatórios e Estatísticas Gerais")
            
            todos_registos = obter_prestadores()
            if not isinstance(todos_registos, list):
                todos_registos = []
            
            # --- SECÇÃO 1: RESUMO DIÁRIO (TOTAL DE CLIENTES E VALOR POR DIA) ---
            st.markdown("### 📅 Resumo Agregado por Dia")
            st.write("Estatísticas consolidadas de prestadores e valores cobrados por dia:")
            
            resumo_diario_dict = defaultdict(lambda: {"total_clientes": 0, "valor_total": 0})
            
            for p in todos_registos:
                if not isinstance(p, dict):
                    continue
                data_completa = p.get('data_pedido', datetime.now().strftime("%d/%m/%Y %H:%M"))
                data_dia = data_completa.split(" ")[0] if " " in data_completa else data_completa
                
                contrato_str = p.get('plano', p.get('contrato', 'N/A'))
                
                valor_numerico = 0
                if "1 Hora" in contrato_str or "12" in contrato_str:
                    valor_numerico = 12000
                elif "2 Horas" in contrato_str or "17" in contrato_str:
                    valor_numerico = 17000
                elif "3 Horas" in contrato_str or "20" in contrato_str:
                    valor_numerico = 20000
                
                resumo_diario_dict[data_dia]["total_clientes"] += 1
                resumo_diario_dict[data_dia]["valor_total"] += valor_numerico
            
            tabela_resumo_dados = []
            for dia, valores in sorted(resumo_diario_dict.items(), reverse=True):
                tabela_resumo_dados.append({
                    "Dia": dia,
                    "Total de Clientes": valores["total_clientes"],
                    "Valor Total": f"{valores['valor_total']:,.2f} Kwanzaas".replace(",", "X").replace(".", ",").replace("X", ".")
                })
            
            if tabela_resumo_dados:
                st.dataframe(tabela_resumo_dados, use_container_width=True)
            else:
                st.info("Nenhum resumo diário disponível.")

            st.divider()

            # --- SECÇÃO 2: HISTÓRICO DETALHADO COMPLETO ---
            st.markdown("### 📋 Registo Detalhado de Solicitações")
            st.write("Lista individual de todas as submissões e contratos:")
            
            dados_historico_tabela = []
            for p in todos_registos:
                if not isinstance(p, dict):
                    continue
                status_atual = p.get("status_str", "pendente")
                
                if status_atual == "aprovado" or p.get("approved") is True:
                    if p.get("segundos_restantes", 0) <= 0:
                        estado_formatado = "Concluído / Expirado"
                    else:
                        estado_formatado = "Ativo / Em curso"
                elif status_atual == "expirado":
                    estado_formatado = "Concluído / Expirado"
                elif status_atual == "recusado":
                    estado_formatado = "Recusado"
                elif status_atual == "suspenso":
                    estado_formatado = "Suspenso"
                else:
                    estado_formatado = "Pendente"
                
                contrato_str = p.get('plano', p.get('contrato', 'N/A'))
                
                if "1 Hora" in contrato_str or "12" in contrato_str:
                    valor_str = "12.000,00 Kwanzaas"
                elif "2 Horas" in contrato_str or "17" in contrato_str:
                    valor_str = "17.000,00 Kwanzaas"
                elif "3 Horas" in contrato_str or "20" in contrato_str:
                    valor_str = "20.000,00 Kwanzaas"
                else:
                    valor_str = "N/A"
                
                dados_historico_tabela.append({
                    "Nome": p.get('nome', 'N/A'),
                    "Estabelecimento": p.get('estabelecimento', 'N/A'),
                    "Contrato": contrato_str,
                    "Valor": valor_str,
                    "Estado": estado_formatado,
                    "Reforço": p.get('reforco', 'N/A'),
                    "Data do contrato": p.get('data_pedido', datetime.now().strftime("%d/%m/%Y %H:%M"))
                })
            
            if dados_historico_tabela:
                st.dataframe(dados_historico_tabela, use_container_width=True)
            else:
                st.info("Nenhum registo estatístico disponível.")

import streamlit as st
import urllib.parse
from datetime import datetime, timedelta, date
from collections import defaultdict
from db import obter_prestadores, guardar_prestador

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
    # --- CSS CUSTOMIZADO PARA ABAS E CABEÇALHOS DE TABELAS AMARELOS COM TEXTO PRETO ---
    st.markdown("""
        <style>
        /* Estilização e compactação das abas de navegação */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #000000 !important;
            color: #ffffff !important;
            border-radius: 6px 6px 0px 0px;
            padding: 6px 12px;
            font-weight: bold;
            font-size: 13px;
            border: 1px solid #3f3f46;
        }
        .stTabs [aria-selected="true"] {
            background-color: #18181b !important;
            color: #eab308 !important;
            border-color: #eab308 !important;
        }

        /* Estilização dos cabeçalhos das tabelas (fundo amarelo e texto preto) */
        div[data-testid="stDataFrame"] th, 
        div[data-testid="stTable"] th,
        thead tr th {
            background-color: #eab308 !important;
            color: #000000 !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Painel de Administração — FF Karaoke")
    st.caption("Gestão de acessos e controlos do programa FFK (Baseado em Tempo Real)")

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
        # --- BLOCO NATIVO DE ATUALIZAÇÃO AUTOMÁTICA GLOBAL (A CADA 5 SEGUNDOS) ---
        @st.fragment(run_every=5)
        def painel_admin_automatico():
            agora_ts = datetime.now().timestamp()
            
            try:
                prestadores_atuais = obter_prestadores()
                if not isinstance(prestadores_atuais, list):
                    prestadores_atuais = []
            except Exception:
                prestadores_atuais = []
            
            # Processa a expiração automática baseada no relógio real (Timestamp)
            houve_alteracao = False
            for p in prestadores_atuais:
                if not isinstance(p, dict):
                    continue
                status_str = p.get("status_str", "pendente")
                
                if status_str == "aprovado":
                    expira_ts = p.get("expira_timestamp", 0)
                    
                    if expira_ts > 0 and agora_ts >= expira_ts:
                        p["status_str"] = "expirado"
                        p["approved"] = False
                        p["segundos_restantes"] = 0
                        guardar_prestador(p)
                        houve_alteracao = True
                    elif expira_ts > 0:
                        p["segundos_restantes"] = int(expira_ts - agora_ts)

            ativos = [
                p for p in prestadores_atuais 
                if isinstance(p, dict) 
                and (p.get("status_str") == "aprovado" or p.get("approved") is True) 
                and p.get("expira_timestamp", 0) > agora_ts
            ]
            qtd_ativos = len(ativos)
            
            pendentes_lista = []
            for p in prestadores_atuais:
                if not isinstance(p, dict):
                    continue
                status_str = str(p.get("status_str", "")).lower()
                approved_val = p.get("approved")
                
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
                "🔗 Link e QR", 
                titulo_aba_pendentes, 
                "🟢 Activos", 
                "📈 Relatórios"
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
                st.subheader(f"⏳ Registos pendentes ({qtd_pendentes})")

                if qtd_pendentes > 0:
                    st.markdown(f"""
                        <div style="background-color: #fef08a; color: #713f12; padding: 8px 15px; border-radius: 6px; font-weight: bold; margin-bottom: 15px; display: inline-block;">
                            ⚠️ Atenção: Existem {qtd_pendentes} pedido(s) pendente(s) a aguardar aprovação!
                        </div>
                    """, unsafe_allow_html=True)
                
                if not pendentes_lista:
                    st.info("Nenhum pedido pendente de momento. Os novos pedidos aparecerão aqui automaticamente.")
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
                                    p["data_pedido"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                                    
                                    contrato_str = str(p.get('plano', p.get('contrato', ''))).lower()
                                    
                                    if "3 hora" in contrato_str or "20.000" in contrato_str:
                                        segundos_contrato = 10800  # 3 Horas
                                    elif "2 hora" in contrato_str or "17.000" in contrato_str:
                                        segundos_contrato = 7200   # 2 Horas
                                    else:
                                        segundos_contrato = 3600   # 1 Hora / Padrão
                                    
                                    p["expira_timestamp"] = datetime.now().timestamp() + segundos_contrato
                                    p["segundos_restantes"] = segundos_contrato
                                    
                                    guardar_prestador(p)
                                    st.rerun()
                                    
                            with col_b:
                                if st.button("❌ Recusar", key=f"rec_{p.get('token', 't')}"):
                                    p["approved"] = False
                                    p["status_str"] = "recusado"
                                    p["data_pedido"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                                    guardar_prestador(p)
                                    st.rerun()

            with aba3:
                st.subheader(f"🟢 Prestadores Activos / Online ({qtd_ativos})")
                
                if not ativos:
                    st.info("Nenhum prestador ativo no momento.")
                else:
                    dados_tabela = []
                    for p in ativos:
                        expira_ts = p.get("expira_timestamp", 0)
                        segundos_restantes = max(0, int(expira_ts - agora_ts))
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
                
                # --- CALENDÁRIO NO TOPO DA ABA RELATÓRIOS PARA CONTROLAR OS TOTAIS SUPERIORES ---
                st.markdown("### 📅 Filtro por Data para os Indicadores")
                
                data_calendario = st.date_input(
                    "📅 Selecione a Data do Contrato para ver os clientes e atualizar os totais:",
                    value=date.today(),
                    format="DD/MM/YYYY",
                    key="calendario_detalhado"
                )
                
                data_selecionada_str = data_calendario.strftime("%d/%m/%Y")
                
                dados_filtrados = []
                total_aprovados_filtro = 0
                total_recusados_filtro = 0
                valor_total_filtro = 0
                
                for p in prestadores_atuais:
                    if not isinstance(p, dict):
                        continue
                    
                    data_completa = p.get('data_pedido', datetime.now().strftime("%d/%m/%Y %H:%M"))
                    data_dia = data_completa.split(" ")[0] if " " in data_completa else data_completa
                    
                    if data_dia == data_selecionada_str:
                        status_atual = p.get("status_str", "pendente")
                        expira_ts = p.get("expira_timestamp", 0)
                        
                        if status_atual == "aprovado" or p.get("approved") is True:
                            if expira_ts > 0 and agora_ts >= expira_ts:
                                estado_formatado = "Concluído / Expirado"
                            else:
                                estado_formatado = "Ativo / Em curso"
                            total_aprovados_filtro += 1
                        elif status_atual == "expirado":
                            estado_formatado = "Concluído / Expirado"
                            total_aprovados_filtro += 1
                        elif status_atual == "recusado":
                            estado_formatado = "Recusado"
                            total_recusados_filtro += 1
                        elif status_atual == "suspenso":
                            estado_formatado = "Suspenso"
                        else:
                            estado_formatado = "Pendente"
                        
                        contrato_str = p.get('plano', p.get('contrato', 'N/A'))
                        
                        valor_numerico = 0
                        if "1 Hora" in contrato_str or "12" in contrato_str:
                            valor_str = "12.000,00 Kwanzaas"
                            valor_numerico = 12000
                        elif "2 Horas" in contrato_str or "17" in contrato_str:
                            valor_str = "17.000,00 Kwanzaas"
                            valor_numerico = 17000
                        elif "3 Horas" in contrato_str or "20" in contrato_str:
                            valor_str = "20.000,00 Kwanzaas"
                            valor_numerico = 20000
                        else:
                            valor_str = "N/A"
                        
                        valor_total_filtro += valor_numerico
                        
                        dados_filtrados.append({
                            "Nome": p.get('nome', 'N/A'),
                            "Estabelecimento": p.get('estabelecimento', 'N/A'),
                            "Contrato": contrato_str,
                            "Valor": valor_str,
                            "Estado": estado_formatado,
                            "Reforço": p.get('reforco', 'N/A'),
                            "Data do contrato": data_completa
                        })
                
                # --- BOTÃO DE OCULTAR / MOSTRAR SALDO ---
                col_btn_ocultar, col_vazio = st.columns([2, 8])
                with col_btn_ocultar:
                    ocultar_saldo = st.toggle("🔒 Ocultar Saldo / Valores", value=False, key="toggle_ocultar_saldo")

                st.divider()
                
                # --- CARTÕES DE TOTAIS SUPERIORES (REFLETEM O DIA SELECIONADO NO CALENDÁRIO) ---
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                with col_m1:
                    st.metric("Total de Prestadores", len(dados_filtrados))
                with col_m2:
                    if ocultar_saldo:
                        valor_total_fmt = "******** Kwanzaas"
                    else:
                        valor_total_fmt = f"{valor_total_filtro:,.2f} Kwanzaas".replace(",", "X").replace(".", ",").replace("X", ".")
                    st.metric("Total em Kwanzas", valor_total_fmt)
                with col_m3:
                    st.metric("Total Aprovados", total_aprovados_filtro)
                with col_m4:
                    st.metric("Total Recusados", total_recusados_filtro)

                st.divider()

                st.markdown("### 📅 Resumo Agregado por Dia")
                resumo_diario_dict = defaultdict(lambda: {"total_clientes": 0, "valor_total": 0, "aprovados": 0, "recusados": 0})
                
                for p in prestadores_atuais:
                    if not isinstance(p, dict):
                        continue
                    data_completa = p.get('data_pedido', datetime.now().strftime("%d/%m/%Y %H:%M"))
                    data_dia = data_completa.split(" ")[0] if " " in data_completa else data_completa
                    
                    status_atual = str(p.get('status_str', '')).lower()
                    approved_val = p.get('approved')
                    
                    is_aprovado = (status_atual == "aprovado" or approved_val is True or status_atual == "expirado")
                    is_recusado = (status_atual == "recusado")
                    
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
                    
                    if is_aprovado:
                        resumo_diario_dict[data_dia]["aprovados"] += 1
                    elif is_recusado:
                        resumo_diario_dict[data_dia]["recusados"] += 1
                
                tabela_resumo_dados = []
                for dia, valores in sorted(resumo_diario_dict.items(), reverse=True):
                    if ocultar_saldo:
                        val_fmt = "******** Kwanzaas"
                    else:
                        val_fmt = f"{valores['valor_total']:,.2f} Kwanzaas".replace(",", "X").replace(".", ",").replace("X", ".")
                        
                    tabela_resumo_dados.append({
                        "Dia": dia,
                        "Total de Clientes": valores["total_clientes"],
                        "Aprovados": valores["aprovados"],
                        "Recusados": valores["recusados"],
                        "Valor Total": val_fmt
                    })
                
                if tabela_resumo_dados:
                    st.dataframe(tabela_resumo_dados, use_container_width=True)
                else:
                    st.info("Nenhum resumo diário disponível.")

                st.divider()

                # --- SEÇÃO DE REGISTO DETALHADO DE SOLICITAÇÕES ---
                st.markdown("### 📋 Registo Detalhado de Solicitações")
                
                st.markdown(f"<p style='color: #a1a1aa;'>A exibir os registos para a data: <b>{data_selecionada_str}</b></p>", unsafe_allow_html=True)
                
                if dados_filtrados:
                    # Aplica ocultação de saldo na tabela de detalhe se o botão estiver ativo
                    dados_tabela_exibicao = []
                    for item in dados_filtrados:
                        item_copy = item.copy()
                        if ocultar_saldo:
                            item_copy["Valor"] = "********"
                        dados_tabela_exibicao.append(item_copy)
                        
                    st.dataframe(dados_tabela_exibicao, use_container_width=True)
                else:
                    st.info(f"Nenhum registo encontrado para a data {data_selecionada_str}.")

        painel_admin_automatico()

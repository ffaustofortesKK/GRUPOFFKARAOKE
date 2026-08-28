# Dentro do ficheiro modulos/admin.py, na Aba 1:
with aba1:
    pendentes = [p for p in st.session_state.prestadores if not p["approved"]]
    st.subheader(f"⏳ Registos pendentes ({len(pendentes)})")
    if not pendentes:
        st.info("Nenhum registo à espera de aprovação.")
    else:
        for p in pendentes:
            with st.container(border=True):
                st.markdown(f"**{p['nome']}**")
                st.caption(f"Telefone: {p['telefone']} · Estabelecimento: {p.get('estabelecimento', 'N/A')} · Plano: {p['plano']} · Token: {p['token']}")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Aprovar", key=f"aprov_{p['token']}"):
                        p["approved"] = True
                        st.session_state.historico.append({"acao": "Aprovação", "detalhe": f"Prestador {p['nome']} aprovado.", "data": "Hoje"})
                        st.rerun()
                with col_b:
                    if st.button("❌ Recusar", key=f"rec_{p['token']}"):
                        # Remove o prestador
                        st.session_state.prestadores = [x for x in st.session_state.prestadores if x["token"] != p["token"]]
                        st.session_state.historico.append({"acao": "Recusa", "detalhe": f"Prestador {p['nome']} foi recusado.", "data": "Hoje"})
                        st.rerun()

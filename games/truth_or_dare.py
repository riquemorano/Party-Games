import streamlit as st
import pandas as pd
import random
import os

def render_truth_or_dare():
    st.header("🎲 Verdade ou Desafio")

    # --- Inicialização do Estado ---
    if "td_game" not in st.session_state:
        st.session_state.td_game = {
            "jogadores": [],
            "resultado_dado": "", # 'VERDADE' ou 'DESAFIO'
            "pergunta_de": "",
            "pergunta_para": "",
            "sugestao_atual": ""
        }

    # --- BOTÃO PRINCIPAL (O DADO) ---
    st.write("### ⚡ Sorteio Rápido")
    if st.button("🔥 VERDADE OU DESAFIO?", use_container_width=True):
        st.session_state.td_game["resultado_dado"] = random.choice(["VERDADE", "DESAFIO"])
        
        # Se houver jogadores, sorteia quem faz para quem
        if len(st.session_state.td_game["jogadores"]) >= 2:
            dupla = random.sample(st.session_state.td_game["jogadores"], 2)
            st.session_state.td_game["pergunta_de"] = dupla[0]
            st.session_state.td_game["pergunta_para"] = dupla[1]
        
        # Limpa sugestão anterior para focar no novo sorteio
        st.session_state.td_game["sugestao_atual"] = ""

    # --- EXIBIÇÃO DO RESULTADO DO "DADO" ---
    if st.session_state.td_game["resultado_dado"]:
        res = st.session_state.td_game["resultado_dado"]
        cor = "#28a745" if res == "VERDADE" else "#dc3545"
        
        st.markdown(f"""
            <div style="text-align: center; padding: 30px; border-radius: 15px; border: 5px solid {cor}; background-color: rgba(0,0,0,0.2);">
                <h1 style="color: {cor}; font-size: 3rem; margin: 0;">{res}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Exibe quem pergunta para quem (SÓ SE TIVER JOGADORES)
        if st.session_state.td_game["pergunta_de"]:
            st.info(f"🎤 **{st.session_state.td_game['pergunta_de']}** pergunta para **{st.session_state.td_game['pergunta_para']}**")

    st.divider()

    # --- OPÇÕES ADICIONAIS ---
    col1, col2 = st.columns(2)
    
    with col1:
        # Sugestão baseada no que caiu no dado
        if st.session_state.td_game["resultado_dado"]:
            if st.button(f"✨ Sugestão de {st.session_state.td_game['resultado_dado'].capitalize()}", use_container_width=True):
                caminho = os.path.join("data", "sugestoesTruthOrDare.csv")
                try:
                    df = pd.read_csv(caminho, header=None, names=["texto", "tipo"])
                    # Filtra o CSV para pegar apenas o tipo que caiu no dado
                    tipo_atual = st.session_state.td_game["resultado_dado"].strip().upper()
                    df_filtrado = df[df['tipo'].str.strip().str.upper() == tipo_atual]
                    
                    if not df_filtrado.empty:
                        st.session_state.td_game["sugestao_atual"] = df_filtrado.sample(n=1).iloc[0]["texto"]
                    else:
                        st.warning(f"Sem sugestões de {tipo_atual} no arquivo.")
                except:
                    st.error("Erro ao ler o CSV de sugestões.")

    with col2:
        with st.popover("👥 Nomes (Opcional)", use_container_width=True):
            nomes_input = st.text_area("Nomes (um por linha):")
            if st.button("Salvar Lista"):
                st.session_state.td_game["jogadores"] = [n.strip() for n in nomes_input.split('\n') if n.strip()]
                st.rerun()

    # --- EXIBIÇÃO DA SUGESTÃO ---
    if st.session_state.td_game["sugestao_atual"]:
        st.chat_message("assistant").write(st.session_state.td_game["sugestao_atual"])
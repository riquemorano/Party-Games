import streamlit as st
import pandas as pd
import random
import os
import time

def tocar_som_fim():
    # Som de alarme via URL pública
    audio_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    html_string = f"""
        <audio autoplay>
          <source src="{audio_url}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(html_string, height=0)

def render_password_game():
    st.header("🤫 Megasenha - Lista Completa")

    # --- Inicialização do Estado ---
    if "pw_game" not in st.session_state:
        st.session_state.pw_game = {
            "iniciado": False,
            "palavras": [],
            "tempo_total": 0,
            "jogo_finalizado": False
        }

    # --- Configuração Inicial ---
    if not st.session_state.pw_game["iniciado"]:
        st.subheader("Configurações da Rodada")
        qtd_palavras = st.number_input("Quantidade de Palavras", 3, 15, 5)
        tempo_segundos = st.slider("Tempo Total (segundos)", 30, 180, 60)

        if st.button("Gerar Lista e Iniciar", use_container_width=True):
            caminho = os.path.join("data", "palavrasPassword.csv")
            try:
                df = pd.read_csv(caminho, header=None)
                lista_total = df.values.flatten().tolist()
                lista_total = [p for p in lista_total if str(p).lower() != "nan" and str(p).strip() != ""]
                
                selecionadas = random.sample(lista_total, min(qtd_palavras, len(lista_total)))
                
                st.session_state.pw_game.update({
                    "iniciado": True,
                    "palavras": selecionadas,
                    "tempo_total": tempo_segundos,
                    "jogo_finalizado": False
                })
                st.rerun()
            except Exception as e:
                st.error("Erro ao carregar 'password.csv'. Verifique a pasta 'data'.")

    # --- Tela de Jogo Ativo ---
    elif not st.session_state.pw_game["jogo_finalizado"]:
        palavras = st.session_state.pw_game["palavras"]
        tempo_limite = st.session_state.pw_game["tempo_total"]

        # 1. Cronômetro Visual
        col_t1, col_t2 = st.columns([1, 3])
        placeholder_tempo = col_t1.empty()
        progresso = col_t2.progress(1.0)

        # 2. Exibição das Palavras em "Cards"
        st.write("### 📝 Suas Palavras:")
        cols = st.columns(1) # Uma palavra por linha para facilitar a leitura no celular
        for i, p in enumerate(palavras):
            st.markdown(f"""
                <div style="background-color: #262730; padding: 10px; border-radius: 10px; border-left: 5px solid #FF4B4B; margin-bottom: 5px;">
                    <h3 style="margin: 0; color: white;">{i+1}. {p.upper()}</h3>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        
        # Botão para encerrar antes do tempo
        if st.button("Finalizar Rodada (Concluí todas!)", use_container_width=True):
            st.session_state.pw_game["jogo_finalizado"] = True
            st.rerun()

        # 3. Lógica do Timer (Loop de atualização)
        for t in range(tempo_limite, -1, -1):
            placeholder_tempo.metric("Tempo", f"{t}s")
            progresso.progress(t / tempo_limite)
            
            if t == 0:
                tocar_som_fim()
                st.session_state.pw_game["jogo_finalizado"] = True
                st.rerun()
            
            time.sleep(1)

    # --- Fim de Jogo ---
    else:
        st.success("🏁 Fim do Tempo!")
        st.write("Confira com o grupo quantas palavras foram adivinhadas.")
        
        if st.button("Nova Partida", use_container_width=True):
            st.session_state.pw_game = {
                "iniciado": False,
                "palavras": [],
                "tempo_total": 0,
                "jogo_finalizado": False
            }
            st.rerun()
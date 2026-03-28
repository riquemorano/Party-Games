import streamlit as st
import pandas as pd
import random
import os


def render_spy_game():
    st.header("🕵️ Who is the Spy?")

    if "spy_game" not in st.session_state:
        st.session_state.spy_game = {
            "iniciado": False,
            "palavras": [],
            "atual": 0,
            "revelado": False,
        }

    if not st.session_state.spy_game["iniciado"]:
        n = st.number_input("Jogadores", 3, 20, 4)
        diff = st.selectbox("Dificuldade", ["Normal", "Hard"])
        if st.button("Sortear Papéis"):
            caminho_spy = os.path.join("data", "palavrasSpy.csv")
            if os.path.exists(caminho_spy):
                df = pd.read_csv(caminho_spy)
                par = random.choice(df.values.tolist())
                p1, p2 = random.sample(list(par), 2)
                espiao = random.randint(0, n - 1)

                lista = [
                    (
                        "⚠️ TEMA LIVRE"
                        if i == espiao and diff == "Hard"
                        else (p2 if i == espiao else p1)
                    )
                    for i in range(n)
                ]
                st.session_state.spy_game.update(
                    {"iniciado": True, "palavras": lista, "atual": 0, "revelado": False}
                )
                st.rerun()
            else:
                st.error("Arquivo 'palavrasSpy.csv' não encontrado na pasta 'data'.")
    else:
        atual = st.session_state.spy_game["atual"]
        if atual < len(st.session_state.spy_game["palavras"]):
            st.subheader(f"Jogador {atual + 1}")
            if not st.session_state.spy_game["revelado"]:
                if st.button(f"Ver Minha Palavra", key=f"spy_btn_{atual}"):
                    st.session_state.spy_game["revelado"] = True
                    st.rerun()
            else:
                st.success(
                    f"Sua palavra: **{st.session_state.spy_game['palavras'][atual]}**"
                )
                if st.button("OK, Próximo!", key=f"spy_next_{atual}"):
                    st.session_state.spy_game["atual"] += 1
                    st.session_state.spy_game["revelado"] = False
                    st.rerun()
        else:
            st.success("Todos já viram! Comecem a rodada.")
            if st.button("Novo Jogo"):
                st.session_state.spy_game = {
                    "iniciado": False,
                    "palavras": [],
                    "atual": 0,
                    "revelado": False,
                }
                st.rerun()

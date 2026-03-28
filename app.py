import streamlit as st
import pandas as pd
import random
import os

import streamlit as st
from games.spy import render_spy_game
from games.mafia import render_mafia_game
from games.stop import render_stop_game
from games.mime import render_mime_game
from games.truth_or_dare import render_truth_or_dare
from games.password_game import render_password_game
from games.post_it import render_post_it_game

# Configuração da Página
st.set_page_config(page_title="Game Night Hub", page_icon="🎮", layout="centered")


# --- Funções Auxiliares ---
def carregar_palavra_aleatoria(nome_arquivo):
    caminho = os.path.join("data", nome_arquivo)
    try:
        # Usando header=None se seus CSVs não tiverem cabeçalho, ou ajuste conforme necessário
        df = pd.read_csv(caminho)
        lista = df.values.flatten().tolist()
        return random.choice(
            [x for x in lista if str(x).lower() != "nan" and str(x).strip() != ""]
        )
    except Exception as e:
        st.error(
            f"Erro ao ler {nome_arquivo}. Verifique se o arquivo está na pasta 'data'."
        )
        return "Erro"


# --- Interface Lateral ---
st.sidebar.title("🎮 Menu de Jogos")
jogo_selecionado = st.sidebar.selectbox(
    "Escolha o que jogar:",
    [
        "Who is the Spy?",
        "Máfia (Cidade Dorme)",
        "Stop!",
        "Verdade ou Desafio",
        "Megasenha (Password)",
        "Post-it na Testa",
    ],
)

# Limpar estados de outros jogos ao trocar no menu
if "ultimo_jogo" not in st.session_state:
    st.session_state.ultimo_jogo = jogo_selecionado
if st.session_state.ultimo_jogo != jogo_selecionado:
    for key in [
        "spy_game",
        "mafia_game",
        "stop_game",
        "truth_dare_game",
        "password_game",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.ultimo_jogo = jogo_selecionado

# --- WHO IS THE SPY? ---
if jogo_selecionado == "Who is the Spy?":
    render_spy_game()

# --- MÁFIA (CIDADE DORME) ---
elif jogo_selecionado == "Máfia (Cidade Dorme)":
    render_mafia_game()

# --- MÍMICA ---
elif jogo_selecionado == "Mímica":
    render

# --- DRAW & GUESS ---
elif jogo_selecionado == "Draw & Guess":
    render_draw_guess_game()

# --- POST-IT NA TESTA ---
elif jogo_selecionado == "Post-it na Testa":
    render_post_it_game(carregar_palavra_aleatoria("palavrasPostIt.csv"))
# --- 6. STOP! ---
elif jogo_selecionado == "Stop!":
    render_stop_game(carregar_palavra_aleatoria("temasStop.csv"))

elif jogo_selecionado == "Verdade ou Desafio":
    render_truth_or_dare()

elif jogo_selecionado == "Megasenha (Password)":
    render_password_game()
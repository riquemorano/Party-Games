import streamlit as st
import pandas as pd
import random
import os

def render_stop_game(palavra_aleatoria):
    st.header("🛑 Stop / Adedonha")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sortear Letra"):
            st.session_state.letra = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if "letra" in st.session_state:
            st.markdown(f"## Letra: `{st.session_state.letra}`")
    with col2:
        if st.button("Sortear Tema"):
            st.session_state.tema_stop = palavra_aleatoria
        if "tema_stop" in st.session_state:
            st.markdown(f"## Tema: `{st.session_state.tema_stop}`")

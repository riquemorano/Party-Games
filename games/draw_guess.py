import streamlit as st
import pandas as pd
import random
import os


def render_draw_guess_game():

    st.header("🎨 Draw & Guess")
    if st.button("O que devo desenhar?"):
        palavra = carregar_palavra_aleatoria("palavrasDraw.csv")
        st.markdown(
            f"<h1 style='text-align: center; color: #FF4B4B;'>{palavra}</h1>",
            unsafe_allow_html=True,
        )

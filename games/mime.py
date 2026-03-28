import streamlit as st
import pandas as pd
import random
import os


def render_mime_game():
    
    st.header("🎭 Mímica")
    if st.button("Sortear nova Mímica"):
        palavra = carregar_palavra_aleatoria("palavrasMimica.csv")
        st.markdown(
            f"<h1 style='text-align: center;'>{palavra}</h1>", unsafe_allow_html=True
        )

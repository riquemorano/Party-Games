import streamlit as st
import time

def render_post_it_game(palavra_aleatoria):
    st.header("🏷️ Post-it na Testa")
    st.write("Clique no botão e vire a tela para sua testa rapidamente!")

    # Inicializa o estado para controlar a exibição
    if "postit_revelado" not in st.session_state:
        st.session_state.postit_revelado = False
        st.session_state.palavra_atual = ""

    # Botão principal
    if st.button("🚀 Sortear e Preparar (3s)", use_container_width=True):
        st.session_state.postit_revelado = False
        
        # Mecanismo de Delay com Contador Visual
        placeholder = st.empty()
        for i in range(3, 0, -1):
            placeholder.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>Vire a tela em {i}...</h1>", unsafe_allow_html=True)
            time.sleep(1)
        
        placeholder.empty()
        
        # Sorteia a palavra usando a função auxiliar que você já tem
        st.session_state.palavra_atual = palavra_aleatoria
        st.session_state.postit_revelado = True
        st.rerun()

    # Exibição da Palavra
    if st.session_state.postit_revelado:
        st.markdown(
            f"""
            <div style='
                border: 5px dashed yellow; 
                padding: 40px; 
                background-color: #ffffcc; 
                color: black; 
                text-align: center;
                border-radius: 15px;
                box-shadow: 10px 10px 5px rgba(0,0,0,0.2);
            '>
                <h1 style='font-size: 4rem; margin: 0;'>{st.session_state.palavra_atual}</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        if st.button("Limpar Tela / Próximo"):
            st.session_state.postit_revelado = False
            st.rerun()
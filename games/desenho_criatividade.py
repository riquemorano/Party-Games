import streamlit as st
import random
import os

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def carregar_palavras_desenho():
    """Tenta carregar palavras do CSV do repositório, com fallback para frases divertidas."""
    caminho_csv = os.path.join("data", "palavrasDraw.csv")
    if os.path.exists(caminho_csv):
        try:
            import pandas as pd
            df = pd.read_csv(caminho_csv)
            return df.iloc[:, 0].dropna().astype(str).tolist()
        except Exception as e:
            st.warning(f"Erro ao ler CSV: {e}")
            
    # Fallback / Lista de situações inusitadas
    return [
        "Um dinossauro andando de skate", "Um alienígena comendo pizza",
        "Pinguim no deserto", "Cachorro vestido de super-herói",
        "Uma árvore de hambúrguer", "Gato tocando piano",
        "Um vampiro na praia", "Astronauta pescando",
        "Monalisa tirando selfie", "Sapo voando de balão"
    ]

TABULEIRO_CONCEPT = {
    "Pessoas / Seres": ["👨 Pessoa", "👩 Mulher", "👶 Bebê", "👴 Idoso", "👽 Alien", "👻 Fantasma", "🤖 Robô", "🐕 Animal"],
    "Natureza / Elementos": ["🌳 Planta", "💧 Água", "🔥 Fogo", "💨 Ar", "🌍 Terra", "☀️ Sol", "🌙 Lua", "⚡ Eletricidade"],
    "Objetos / Ferramentas": ["⚙️ Engrenagem", "🚗 Veículo", "🏠 Casa", "📱 Tecnologia", "⚔️ Arma", "👕 Roupa", "💰 Dinheiro", "💊 Remédio"],
    "Ações / Conceitos": ["❤️ Amor", "☠️ Morte", "⌚ Tempo", "⚖️ Justiça", "🎵 Música", "🎨 Arte", "🗣️ Fala", "👁️ Visão"],
    "Cores / Formas": ["🔴 Vermelho", "🔵 Azul", "🟡 Amarelo", "🟩 Quadrado", "🔺 Triângulo", "⚪ Círculo", "⬛ Preto", "⬜ Branco"]
}

def inicializar_estado():
    if 'jogo_desenho_ativo' not in st.session_state:
        st.session_state.jogo_desenho_ativo = None
    if 'banco_desenho' not in st.session_state:
        st.session_state.banco_desenho = carregar_palavras_desenho()
        
    if "dg_palavra" not in st.session_state:
        st.session_state.dg_palavra = None

def iniciar_gartic():
    st.session_state.gartic_fase = 1
    st.session_state.gartic_historico = []
    st.session_state.gartic_frase_inicial = random.choice(st.session_state.banco_desenho)
    st.session_state.jogo_desenho_ativo = "gartic"

def iniciar_concept():
    st.session_state.concept_palavra = random.choice(st.session_state.banco_desenho)
    st.session_state.concept_marcadores = []
    st.session_state.jogo_desenho_ativo = "concept"

def app():
    inicializar_estado()
    
    st.header("🎨 Desenho e Criatividade")
    st.markdown("Mostre sua capacidade de se expressar (com ou sem talento para arte)!")

    # Menu Principal com 3 colunas
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✏️ Gartic (Telefone Sem Fio)", use_container_width=True):
            iniciar_gartic()
    with col2:
        if st.button("💡 Concept", use_container_width=True):
            iniciar_concept()
    with col3:
        if st.button("🖌️ Draw & Guess", use_container_width=True):
            st.session_state.jogo_desenho_ativo = "draw_guess"

    st.divider()

    # --- LÓGICA: GARTIC PHONE ---
    if st.session_state.jogo_desenho_ativo == "gartic":
        st.subheader("✏️ Telefone Sem Fio Desenhado")
        st.info("💡 **Como jogar:** Usem papéis e canetas reais. Este app vai coordenar as rodadas!")

        fase = st.session_state.gartic_fase
        if fase == 1:
            st.write("### Jogador 1: Sua vez!")
            st.write("Leia a frase abaixo, **desenhe-a no papel** e passe o papel (sem mostrar a frase) para o próximo.")
            st.error(f"**Frase inicial:** {st.session_state.gartic_frase_inicial}")
            
            if st.button("Passei o desenho! Avançar"):
                st.session_state.gartic_historico.append(st.session_state.gartic_frase_inicial)
                st.session_state.gartic_fase = 2
                st.rerun()
                
        elif fase % 2 == 0:
            st.write(f"### Jogador {fase}: O que é isso?")
            st.write("Olhe o desenho recebido, escreva seu palpite abaixo e **esconda o desenho original**.")
            palpite = st.text_input("O que foi desenhado?")
            if st.button("Confirmar Palpite"):
                if palpite:
                    st.session_state.gartic_historico.append(palpite)
                    st.session_state.gartic_fase += 1
                    st.rerun()
                else:
                    st.warning("Escreva um palpite antes de continuar!")
                    
        elif fase > 0:
            st.write(f"### Jogador {fase}: Hora de desenhar!")
            ultimo_palpite = st.session_state.gartic_historico[-1]
            st.write("Leia a frase abaixo, **desenhe no papel** e passe apenas o seu desenho para o próximo.")
            st.error(f"**Desenhe isto:** {ultimo_palpite}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Avançar para próximo jogador"):
                    st.session_state.gartic_fase += 1
                    st.rerun()
            with col_b:
                if st.button("🏁 Finalizar Jogo", type="primary"):
                    st.session_state.gartic_fase = -1
                    st.rerun()

        if fase == -1:
            st.success("🎉 Jogo Finalizado! Veja a evolução:")
            for i, texto in enumerate(st.session_state.gartic_historico):
                if i == 0:
                    st.write(f"**Original:** {texto}")
                elif i % 2 != 0:
                    st.write(f"👉 **Palpite:** {texto}")
                else:
                    st.write(f"✏️ *(Novo Desenho)*")
            if st.button("Jogar Novamente"):
                iniciar_gartic()
                st.rerun()

    # --- LÓGICA: CONCEPT ---
    elif st.session_state.jogo_desenho_ativo == "concept":
        st.subheader("💡 Concept")
        
        with st.expander("👀 Revelar Palavra (Apenas quem vai dar as dicas)", expanded=False):
            st.markdown(f"### A Palavra Secreta é: **{st.session_state.concept_palavra}**")
            st.write("Selecione os ícones abaixo para formar o conceito dessa palavra.")
            if st.button("Pular Palavra"):
                iniciar_concept()
                st.rerun()

        st.write("---")
        st.write("### 🧩 Ícones Selecionados (Dicas)")
        if st.session_state.concept_marcadores:
            dicas_html = " ".join([f"<span style='font-size: 24px; background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 5px; display: inline-block;'>{icone}</span>" for icone in st.session_state.concept_marcadores])
            st.markdown(dicas_html, unsafe_allow_html=True)
            if st.button("Limpar Ícones"):
                st.session_state.concept_marcadores = []
                st.rerun()
        else:
            st.info("Nenhum ícone selecionado ainda. Clique nos ícones abaixo!")

        st.write("---")
        st.write("### 🎛️ Tabuleiro de Conceitos")
        for categoria, icones in TABULEIRO_CONCEPT.items():
            st.markdown(f"**{categoria}**")
            cols = st.columns(len(icones))
            for i, icone in enumerate(icones):
                with cols[i]:
                    if st.button(icone.split()[0], key=f"btn_{icone}", help=icone):
                        st.session_state.concept_marcadores.append(icone)
                        st.rerun()

    # --- LÓGICA: DRAW & GUESS ---
    elif st.session_state.jogo_desenho_ativo == "draw_guess":
        st.subheader("🖌️ Draw & Guess")
        st.write("Sorteie uma palavra, pegue o papel (ou quadro) e desenhe para o grupo adivinhar!")
        
        if st.button("O que devo desenhar?", use_container_width=True, type="primary"):
            st.session_state.dg_palavra = random.choice(st.session_state.banco_desenho)
            
        if st.session_state.dg_palavra:
            st.markdown(
                f"""
                <div style='text-align: center; padding: 40px; border: 4px dashed #FF4B4B; border-radius: 15px; margin-top: 20px; background-color: #fff5f5;'>
                    <h1 style='color: #FF4B4B; margin: 0; font-size: 3.5rem;'>{st.session_state.dg_palavra}</h1>
                </div>
                """,
                unsafe_allow_html=True,
            )

if __name__ == "__main__":
    app()
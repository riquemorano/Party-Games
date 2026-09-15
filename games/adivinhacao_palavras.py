import streamlit as st
import random
import os
import time
from utils.gemini import gerar_conteudo_ia

# --- CARREGAMENTO DE DADOS ---


# O cache evita que os arquivos CSV sejam lidos do disco a cada interação (rerun) na tela
@st.cache_data
def carregar_palavras():
    caminho_csv = os.path.join("data", "palavrasPassword.csv")
    if os.path.exists(caminho_csv):
        try:
            import pandas as pd

            df = pd.read_csv(caminho_csv, header=None)
            # Achata o dataframe para uma lista 1D, removendo nulos e espaços vazios
            lista_total = df.values.flatten().tolist()
            return [
                str(p)
                for p in lista_total
                if str(p).lower() != "nan" and str(p).strip() != ""
            ]
        except Exception as e:
            st.warning(f"Erro ao ler CSV de palavras: {e}")

    # Fallback de segurança caso o arquivo não exista
    return [
        "Abacaxi",
        "Cachorro",
        "Avião",
        "Computador",
        "Futebol",
        "Chocolate",
        "Elefante",
        "Praia",
        "Montanha",
        "Livro",
        "Relógio",
        "Espião",
        "Sombra",
    ]


@st.cache_data
def carregar_temas_stop():
    caminho_csv = os.path.join("data", "temasStop.csv")
    if os.path.exists(caminho_csv):
        try:
            import pandas as pd

            df = pd.read_csv(caminho_csv)
            return df.iloc[:, 0].dropna().astype(str).tolist()
        except Exception as e:
            st.warning(f"Erro ao ler CSV de temas do Stop: {e}")

    return [
        "Nome de Animal",
        "Profissão",
        "Marca de Carro",
        "Fruta",
        "Cor",
        "País ou Cidade",
        "Objeto",
        "Filme ou Série",
    ]


@st.cache_data
def carregar_palavras_mimica():
    caminho_csv = os.path.join("data", "palavrasMimica.csv")
    if os.path.exists(caminho_csv):
        try:
            import pandas as pd

            df = pd.read_csv(caminho_csv)
            return df.iloc[:, 0].dropna().astype(str).tolist()
        except Exception as e:
            st.warning(f"Erro ao ler CSV de Mímica: {e}")

    return [
        "Tocar violão",
        "Andar de bicicleta",
        "Pinguim",
        "Zumbi",
        "Tirar uma selfie",
        "Lavar louça",
        "Dinossauro",
        "Macaco",
    ]


# Dicionário estático para fallback caso a IA falhe na geração do jogo Tabu
DICIONARIO_TABU = {
    "Praia": ["Areia", "Mar", "Sol", "Verão", "Onda"],
    "Cachorro": ["Gato", "Latir", "Animal", "Estimação", "Osso"],
    "Futebol": ["Bola", "Gol", "Campo", "Esporte", "Time"],
    "Cinema": ["Filme", "Pipoca", "Tela", "Ator", "Assistir"],
}


def tocar_som_fim():
    # Injeta um componente HTML invisível rodando uma tag de áudio em autoplay.
    # Essa é uma forma de tocar sons no Streamlit sem travar a execução do Python.
    audio_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    html_string = f"""
        <audio autoplay>
          <source src="{audio_url}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(html_string, height=0)


def inicializar_estado():
    # Prepara o dicionário de sessão para manter o estado dos jogos persistente
    if "jogo_adivinhacao_ativo" not in st.session_state:
        st.session_state.jogo_adivinhacao_ativo = None
    if "banco_palavras" not in st.session_state:
        st.session_state.banco_palavras = carregar_palavras()
    if "banco_temas_stop" not in st.session_state:
        st.session_state.banco_temas_stop = carregar_temas_stop()
    if "banco_mimica" not in st.session_state:
        st.session_state.banco_mimica = carregar_palavras_mimica()

    if "pw_game" not in st.session_state:
        st.session_state.pw_game = {
            "iniciado": False,
            "palavras": [],
            "tempo_total": 0,
            "jogo_finalizado": False,
        }

    if "stop_letra" not in st.session_state:
        st.session_state.stop_letra = None
    if "stop_tema" not in st.session_state:
        st.session_state.stop_tema = None

    if "mimica_palavra" not in st.session_state:
        st.session_state.mimica_palavra = None

    # Inicialização para jogos que precisam de tabuleiro montado e validação de turno
    if "cs_iniciado" not in st.session_state:
        st.session_state.cs_iniciado = False
    if "jo_iniciado" not in st.session_state:
        st.session_state.jo_iniciado = False
    if "tabu_iniciado" not in st.session_state:
        st.session_state.tabu_iniciado = False


def app():
    inicializar_estado()

    st.header("🗣️ Adivinhação e Palavras")
    st.markdown("Comunicação é a chave. Teste sua criatividade e sintonia!")

    # Menu de seleção dos jogos da categoria
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🕵️‍♂️ Código Secreto", use_container_width=True):
            st.session_state.jogo_adivinhacao_ativo = "codigo_secreto"
        if st.button("⏱️ Megasenha", use_container_width=True):
            st.session_state.jogo_adivinhacao_ativo = "megasenha"
    with col2:
        if st.button("☝️ Just One", use_container_width=True):
            st.session_state.jogo_adivinhacao_ativo = "just_one"
        if st.button("🛑 Stop / Adedonha", use_container_width=True):
            st.session_state.jogo_adivinhacao_ativo = "stop"
    with col3:
        if st.button("🚫 Tabu", use_container_width=True):
            st.session_state.jogo_adivinhacao_ativo = "tabu"
        if st.button("🎭 Mímica", use_container_width=True):
            st.session_state.jogo_adivinhacao_ativo = "mimica"

    st.divider()

    # --- LÓGICA: CÓDIGO SECRETO ---
    if st.session_state.jogo_adivinhacao_ativo == "codigo_secreto":
        st.subheader("🕵️‍♂️ Código Secreto (Codenames)")

        tema_usuario = st.text_input(
            "Gerar tabuleiro com IA? Digite um tema (ou deixe em branco)", key="tema_cs"
        )

        if st.button("Gerar Novo Tabuleiro", type="primary"):
            palavras = []
            if (
                "api_key" in st.session_state
                and st.session_state["api_key"]
                and tema_usuario
            ):
                with st.spinner("IA criando tabuleiro temático..."):
                    try:
                        palavras = gerar_conteudo_ia(
                            "palavras_gerais", tema=tema_usuario, quantidade=25
                        )
                    except Exception as e:
                        st.error(f"Erro na IA. Usando palavras originais...")

            # A regra do Código Secreto exige exatamente um grid de 5x5 (25 palavras)
            if len(palavras) < 25:
                palavras = random.sample(
                    st.session_state.banco_palavras,
                    min(25, len(st.session_state.banco_palavras)),
                )
            else:
                palavras = random.sample(palavras, 25)

            # Distribuição base oficial: 9 da equipe primária, 8 da secundária, 7 neutros e 1 assassino
            cores = (
                ["🔴 Vermelho"] * 9
                + ["🔵 Azul"] * 8
                + ["⚪ Neutro"] * 7
                + ["⚫ ASSASSINO"] * 1
            )
            random.shuffle(cores)

            st.session_state.cs_palavras = palavras
            st.session_state.cs_cores = cores
            st.session_state.cs_reveladas = [False] * 25
            st.session_state.cs_iniciado = True

        if st.session_state.cs_iniciado:
            # O Mestre Espião precisa ver o gabarito. Este toggle desabilita as restrições visuais para ele.
            modo_mestre = st.toggle("👁️ Modo Mestre Espião (Ver Cores)")
            st.write("---")

            # Montagem do grid visual (5x5) do tabuleiro
            for i in range(5):
                cols = st.columns(5)
                for j in range(5):
                    idx = i * 5 + j
                    palavra = st.session_state.cs_palavras[idx]
                    cor = st.session_state.cs_cores[idx]
                    revelada = st.session_state.cs_reveladas[idx]

                    with cols[j]:
                        if revelada or modo_mestre:
                            st.button(
                                f"{cor}\n\n**{palavra}**",
                                key=f"cs_{idx}",
                                disabled=True,
                                use_container_width=True,
                            )
                        else:
                            if st.button(
                                f"❔\n\n**{palavra}**",
                                key=f"cs_{idx}",
                                use_container_width=True,
                            ):
                                st.session_state.cs_reveladas[idx] = True
                                st.rerun()

    # --- LÓGICA: JUST ONE ---
    elif st.session_state.jogo_adivinhacao_ativo == "just_one":
        st.subheader("☝️ Just One")

        col1, col2 = st.columns([2, 1])
        with col1:
            tema_usuario = st.text_input("Tema opcional com IA:", key="tema_jo")
        with col2:
            st.write("")
            st.write("")
            if st.button("Gerar Nova Palavra"):
                palavra = None
                if (
                    "api_key" in st.session_state
                    and st.session_state["api_key"]
                    and tema_usuario
                ):
                    with st.spinner("Pensando..."):
                        try:
                            lista = gerar_conteudo_ia(
                                "palavras_gerais", tema=tema_usuario, quantidade=5
                            )
                            palavra = random.choice(lista)
                        except:
                            st.error("Falha na IA. Usando lista padrão.")

                if not palavra:
                    palavra = random.choice(st.session_state.banco_palavras)

                st.session_state.jo_palavra = palavra
                st.session_state.jo_dicas = {}
                st.session_state.jo_fase = "escrever_dicas"
                st.session_state.jo_iniciado = True

        st.divider()

        if st.session_state.jo_iniciado:
            # Fase 1: Coleta cega de dicas da equipe enquanto o jogador principal não vê a tela
            if st.session_state.jo_fase == "escrever_dicas":
                st.error(
                    "⚠️ O jogador que vai adivinhar deve fechar os olhos ou virar de costas agora!"
                )
                st.markdown(
                    f"### A Palavra Secreta é: **{st.session_state.jo_palavra}**"
                )
                num_jogadores = st.number_input(
                    "Quantos jogadores vão dar dicas?",
                    min_value=2,
                    max_value=8,
                    value=4,
                )

                dicas = []
                for i in range(num_jogadores):
                    dica = (
                        st.text_input(f"Dica do Jogador {i+1}", key=f"dica_jo_{i}")
                        .strip()
                        .lower()
                    )
                    if dica:
                        dicas.append(dica)

                if st.button("Processar Dicas", type="primary"):
                    if len(dicas) == num_jogadores:
                        # Regra principal do Just One: se duas ou mais pessoas derem a mesma dica, ela é anulada.
                        # Conta as ocorrências de cada palavra na lista de dicas enviadas.
                        st.session_state.jo_dicas_validas = [
                            d for d in dicas if dicas.count(d) == 1
                        ]
                        st.session_state.jo_dicas_anuladas = list(
                            set([d for d in dicas if dicas.count(d) > 1])
                        )
                        st.session_state.jo_fase = "revelar"
                        st.rerun()
                    else:
                        st.warning("Preencha todas as dicas antes de continuar!")

            # Fase 2: Exibição apenas das dicas validadas para o jogador adivinhar
            elif st.session_state.jo_fase == "revelar":
                st.success("O jogador que vai adivinhar já pode olhar a tela!")
                if st.session_state.jo_dicas_validas:
                    for d in st.session_state.jo_dicas_validas:
                        st.info(f"💡 **{d.upper()}**")
                else:
                    st.error("Todas as dicas foram repetidas e anuladas! 😭")

                if st.button("Revelar Palavra Secreta"):
                    st.markdown(f"### A palavra era: **{st.session_state.jo_palavra}**")

    # --- LÓGICA: TABU ---
    elif st.session_state.jogo_adivinhacao_ativo == "tabu":
        st.subheader("🚫 Tabu")

        tema_usuario = st.text_input(
            "Tema específico com IA? (Deixe em branco para aleatório)", key="tema_tabu"
        )

        if st.button("Gerar Nova Palavra", type="primary", use_container_width=True):
            sucesso_ia = False
            if "api_key" in st.session_state and st.session_state["api_key"]:
                with st.spinner("IA gerando carta de Tabu..."):
                    try:
                        # O prompt de IA retorna o formato exato que alimenta o dicionário de estado abaixo
                        tema_final = tema_usuario if tema_usuario else "aleatório"
                        resultado = gerar_conteudo_ia("tabu", tema=tema_final)
                        st.session_state.tabu_palavra = resultado["palavra"]
                        st.session_state.tabu_proibidas = resultado["proibidas"]
                        sucesso_ia = True
                    except Exception as e:
                        st.error("Falha na IA. Usando Tabu padrão.")

            if not sucesso_ia:
                palavra = random.choice(list(DICIONARIO_TABU.keys()))
                st.session_state.tabu_palavra = palavra
                st.session_state.tabu_proibidas = DICIONARIO_TABU[palavra]

            st.session_state.tabu_iniciado = True

        if st.session_state.tabu_iniciado:
            st.divider()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Usa marcação HTML/CSS explícita para centralizar as palavras e dar aspecto de "carta" ao Tabu
                st.markdown(
                    f"<h1 style='text-align: center; color: #2e7bcf;'>{st.session_state.tabu_palavra}</h1>",
                    unsafe_allow_html=True,
                )
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown(
                    "<h4 style='text-align: center; color: #d9534f;'>Palavras Proibidas (TABU):</h4>",
                    unsafe_allow_html=True,
                )
                for p in st.session_state.tabu_proibidas:
                    st.markdown(
                        f"<h3 style='text-align: center; color: #555555;'>❌ {p}</h3>",
                        unsafe_allow_html=True,
                    )

    # --- LÓGICA: MEGASENHA ---
    elif st.session_state.jogo_adivinhacao_ativo == "megasenha":
        st.subheader("🤫 Megasenha")
        if not st.session_state.pw_game["iniciado"]:
            qtd_palavras = st.number_input("Quantidade de Palavras", 3, 15, 5)
            tempo_segundos = st.slider("Tempo Total (segundos)", 30, 180, 60)
            tema_usuario = st.text_input("Deseja um tema? (IA)")

            if st.button("Gerar Lista e Iniciar", use_container_width=True):
                selecionadas = []
                if (
                    "api_key" in st.session_state
                    and st.session_state["api_key"]
                    and tema_usuario
                ):
                    with st.spinner("Gerando palavras..."):
                        try:
                            selecionadas = gerar_conteudo_ia(
                                "palavras_gerais",
                                tema=tema_usuario,
                                quantidade=qtd_palavras,
                            )
                        except:
                            st.error("Erro na IA.")

                if len(selecionadas) < qtd_palavras:
                    selecionadas = random.sample(
                        st.session_state.banco_palavras,
                        min(qtd_palavras, len(st.session_state.banco_palavras)),
                    )
                else:
                    selecionadas = selecionadas[:qtd_palavras]

                st.session_state.pw_game.update(
                    {
                        "iniciado": True,
                        "palavras": selecionadas,
                        "tempo_total": tempo_segundos,
                        "jogo_finalizado": False,
                    }
                )
                st.rerun()

        elif not st.session_state.pw_game["jogo_finalizado"]:
            palavras = st.session_state.pw_game["palavras"]
            tempo_limite = st.session_state.pw_game["tempo_total"]

            # Elementos 'empty' são usados para atualizar a métrica de tempo in-place, sem causar um rerun na UI
            col_t1, col_t2 = st.columns([1, 3])
            placeholder_tempo = col_t1.empty()
            progresso = col_t2.progress(1.0)

            st.write("### 📝 Suas Palavras:")
            for i, p in enumerate(palavras):
                st.markdown(
                    f"<div style='background-color: #262730; padding: 10px; border-radius: 10px; border-left: 5px solid #FF4B4B; margin-bottom: 5px;'><h3 style='margin: 0; color: white;'>{i+1}. {p.upper()}</h3></div>",
                    unsafe_allow_html=True,
                )

            if st.button("Finalizar Rodada (Concluí todas!)", use_container_width=True):
                st.session_state.pw_game["jogo_finalizado"] = True
                st.rerun()

            # Lógica simples de loop de decremento bloqueante atualizando o UI localmente
            for t in range(tempo_limite, -1, -1):
                placeholder_tempo.metric("Tempo", f"{t}s")
                progresso.progress(t / tempo_limite)
                if t == 0:
                    tocar_som_fim()
                    st.session_state.pw_game["jogo_finalizado"] = True
                    st.rerun()
                time.sleep(1)
        else:
            st.success("🏁 Fim do Tempo ou da Rodada!")
            if st.button("Nova Partida", use_container_width=True):
                st.session_state.pw_game = {
                    "iniciado": False,
                    "palavras": [],
                    "tempo_total": 0,
                    "jogo_finalizado": False,
                }
                st.rerun()

    # --- LÓGICA: STOP / ADEDONHA ---
    elif st.session_state.jogo_adivinhacao_ativo == "stop":
        st.subheader("🛑 Stop / Adedonha")
        st.write(
            "Sorteie uma letra para a rodada e um tema específico, ou use a letra para o jogo de papel tradicional!"
        )

        col_letra, col_tema = st.columns(2)
        with col_letra:
            if st.button("🎲 Sortear Letra", use_container_width=True):
                st.session_state.stop_letra = random.choice(
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                )
            if st.session_state.stop_letra:
                st.markdown(
                    f"<h1 style='text-align: center; color: #FF4B4B; font-size: 5rem;'>{st.session_state.stop_letra}</h1>",
                    unsafe_allow_html=True,
                )

        with col_tema:
            tema_usuario = st.text_input("Criar tema de um assunto? (Opcional)")
            if st.button("🎲 Sortear Categoria (Tema)", use_container_width=True):
                if (
                    "api_key" in st.session_state
                    and st.session_state["api_key"]
                    and tema_usuario
                ):
                    with st.spinner("Pensando..."):
                        try:
                            # Pede 5 resultados à IA para criar um pool e seleciona 1 para evitar monotonia nas respostas
                            lista_temas = gerar_conteudo_ia(
                                "stop", tema=tema_usuario, quantidade=5
                            )
                            st.session_state.stop_tema = random.choice(lista_temas)
                        except:
                            st.session_state.stop_tema = random.choice(
                                st.session_state.banco_temas_stop
                            )
                else:
                    st.session_state.stop_tema = random.choice(
                        st.session_state.banco_temas_stop
                    )

            if st.session_state.stop_tema:
                st.markdown(
                    f"<h3 style='text-align: center; color: #2e7bcf; margin-top: 30px;'>{st.session_state.stop_tema}</h3>",
                    unsafe_allow_html=True,
                )

    # --- LÓGICA: MÍMICA ---
    elif st.session_state.jogo_adivinhacao_ativo == "mimica":
        st.subheader("🎭 Mímica")
        st.write(
            "Aperte o botão e faça a sua equipe adivinhar sem dizer nenhuma palavra!"
        )

        tema_usuario = st.text_input(
            "Quer um tema específico? (Deixe em branco para aleatório)", ""
        )

        if st.button("Sortear nova Mímica", type="primary", use_container_width=True):
            if "api_key" in st.session_state and st.session_state["api_key"]:
                with st.spinner("A IA está pensando em uma mímica criativa..."):
                    try:
                        tema_final = tema_usuario if tema_usuario else "aleatório"
                        lista_ia = gerar_conteudo_ia(
                            "mimica", tema=tema_final, quantidade=10
                        )
                        st.session_state.mimica_palavra = random.choice(lista_ia)
                    except Exception as e:
                        st.error("Ops! A IA falhou. Usando palavras do jogo base...")
                        st.session_state.mimica_palavra = random.choice(
                            st.session_state.banco_mimica
                        )
            else:
                st.session_state.mimica_palavra = random.choice(
                    st.session_state.banco_mimica
                )

        if st.session_state.mimica_palavra:
            st.markdown(
                f"""
                <div style='text-align: center; padding: 50px; background-color: #f0f2f6; border-radius: 15px; margin-top: 20px; border: 3px dashed #FF4B4B;'>
                    <h1 style='color: #333; margin: 0; font-size: 3rem;'>{st.session_state.mimica_palavra}</h1>
                </div>
            """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    app()

import streamlit as st
import pandas as pd
import random
import os

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
    ],
)

# Limpar estados de outros jogos ao trocar no menu
if "ultimo_jogo" not in st.session_state:
    st.session_state.ultimo_jogo = jogo_selecionado
if st.session_state.ultimo_jogo != jogo_selecionado:
    for key in ["spy_game", "mafia_game"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.ultimo_jogo = jogo_selecionado

# --- WHO IS THE SPY? ---
if jogo_selecionado == "Who is the Spy?":
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

# --- MÁFIA (CIDADE DORME) ---
elif jogo_selecionado == "Máfia (Cidade Dorme)":
    st.header("🕵️‍♂️ Máfia / Cidade Dorme")

    if "mafia_game" not in st.session_state:
        st.session_state.mafia_game = {
            "iniciado": False,
            "papeis": [],
            "atual": 0,
            "revelado": False,
        }

    if not st.session_state.mafia_game["iniciado"]:
        st.subheader("⚙️ Configuração da Partida")

        # 1. Definição do total de jogadores
        n_jogadores = st.number_input("Total de Jogadores na roda", 3, 50, 6)

        st.divider()
        st.write("### 🎭 Distribuir Papéis")

        # Colunas para organizar os inputs
        col1, col2 = st.columns(2)

        with col1:
            n_assassinos = st.number_input("🩸 Assassinos", 1, n_jogadores, 1)
            n_detetive = st.number_input("🔍 Detetives", 0, n_jogadores, 1)

        with col2:
            n_medico = st.number_input("💊 Médicos", 0, n_jogadores, 0)
            # Input para novos papéis
            n_extras = st.number_input(
                "➕ Quantos papéis diferentes quer adicionar?", 0, 5, 0
            )

        # 2. Gerar colunas dinâmicas para papéis extras
        papeis_extras_dict = {}
        if n_extras > 0:
            st.write("#### Papéis Customizados")
            # Criamos uma linha de colunas para cada papel extra
            for i in range(n_extras):
                c1, c2 = st.columns([2, 1])
                nome_papel = c1.text_input(
                    f"Nome do Papel {i+1}", f"Papel Extra {i+1}", key=f"name_ex_{i}"
                )
                qtd_papel = c2.number_input(
                    f"Qtd", 0, n_jogadores, 1, key=f"qtd_ex_{i}"
                )
                papeis_extras_dict[nome_papel] = qtd_papel

        # 3. Cálculo de Validação
        total_especiais = (
            n_assassinos + n_detetive + n_medico + sum(papeis_extras_dict.values())
        )
        n_cidadaos = n_jogadores - total_especiais

        # --- Painel de Status ---
        st.divider()
        if n_cidadaos < 0:
            st.error(
                f"❌ **Erro na contagem!** Você distribuiu {total_especiais} papéis para apenas {n_jogadores} jogadores. Remova {abs(n_cidadaos)} papel(éis)."
            )
            btn_ready = False
        else:
            st.info(
                f"✅ **Tudo pronto!** {total_especiais} papéis especiais e {n_cidadaos} Cidadãos Comuns."
            )
            btn_ready = True

        if st.button(
            "Sortear e Começar", disabled=not btn_ready, use_container_width=True
        ):
            # Montagem do Baralho
            baralho = (
                ["🩸 ASSASSINO"] * n_assassinos
                + ["🔍 DETETIVE"] * n_detetive
                + ["💊 MÉDICO"] * n_medico
                + ["🏘️ CIDADÃO"] * n_cidadaos
            )
            # Adiciona os extras
            for nome, qtd in papeis_extras_dict.items():
                baralho.extend([nome.upper()] * qtd)

            random.shuffle(baralho)

            st.session_state.mafia_game.update(
                {"iniciado": True, "papeis": baralho, "atual": 0, "revelado": False}
            )
            st.rerun()

    else:
        # --- Interface de Revelação de Papéis ---
        atual = st.session_state.mafia_game["atual"]
        total = len(st.session_state.mafia_game["papeis"])

        if atual < total:
            st.progress((atual) / total)
            st.subheader(f"👤 Jogador {atual + 1} de {total}")

            if not st.session_state.mafia_game["revelado"]:
                st.info("Passe o dispositivo para o próximo jogador.")
                if st.button("Clique para ver seu papel", key=f"btn_rev_{atual}"):
                    st.session_state.mafia_game["revelado"] = True
                    st.rerun()
            else:
                papel = st.session_state.mafia_game["papeis"][atual]

                # Estilização baseada no papel
                if "ASSASSINO" in papel:
                    st.error(f"Seu papel é: **{papel}**")
                elif "CIDADÃO" in papel:
                    # Usando markdown com fundo cinza suave para o cidadão
                    st.markdown(f"### 🏘️ Seu papel é: **{papel}**")
                else:
                    # Verde para detetives, médicos e extras
                    st.success(f"Seu papel é: **{papel}**")

                if st.button("Entendido!", key=f"btn_next_{atual}"):
                    st.session_state.mafia_game["atual"] += 1
                    st.session_state.mafia_game["revelado"] = False
                    st.rerun()
        else:
            st.balloons()
            st.success("🏁 Todos os papéis foram distribuídos! A cidade dorme...")
            if st.button("Reiniciar Jogo"):
                st.session_state.mafia_game = {
                    "iniciado": False,
                    "papeis": [],
                    "atual": 0,
                    "revelado": False,
                }
                st.rerun()
                
# --- 6. STOP! ---
elif jogo_selecionado == "Stop!":
    st.header("🛑 Stop / Adedonha")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sortear Letra"):
            st.session_state.letra = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if "letra" in st.session_state:
            st.markdown(f"## Letra: `{st.session_state.letra}`")
    with col2:
        if st.button("Sortear Tema"):
            st.session_state.tema_stop = carregar_palavra_aleatoria("temasStop.csv")
        if "tema_stop" in st.session_state:
            st.markdown(f"## Tema: `{st.session_state.tema_stop}`")

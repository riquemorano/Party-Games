import streamlit as st
import random
import os
from utils.gemini import gerar_conteudo_ia

# --- CARREGAMENTO DE DADOS ---


# Utiliza cache para não reler o CSV do disco a cada interação na tela
@st.cache_data
def carregar_palavras_spy():
    """Tenta carregar os pares de palavras do CSV para o jogo Spy, com fallback."""
    caminho_spy = os.path.join("data", "palavrasSpy.csv")
    if os.path.exists(caminho_spy):
        try:
            import pandas as pd

            df = pd.read_csv(caminho_spy)
            return df.values.tolist()
        except Exception as e:
            st.warning(f"Erro ao ler CSV do Spy: {e}")

    # Fallback estático caso o CSV falte ou esteja corrompido
    return [
        ("Maçã", "Pera"),
        ("Carro", "Caminhão"),
        ("Cachorro", "Lobo"),
        ("Futebol", "Basquete"),
        ("Praia", "Piscina"),
        ("Cinema", "Teatro"),
        ("Rei", "Presidente"),
        ("Violão", "Guitarra"),
        ("Ouro", "Prata"),
    ]


def inicializar_estado():
    # Inicializa as variáveis no session_state para persistir os dados entre os reruns
    if "jogo_social_ativo" not in st.session_state:
        st.session_state.jogo_social_ativo = None

    # Estado para Resistência / Lobisomem
    if "jogadores_social" not in st.session_state:
        st.session_state.jogadores_social = []
    if "papeis_distribuidos" not in st.session_state:
        st.session_state.papeis_distribuidos = {}
    if "cartas_centro" not in st.session_state:
        st.session_state.cartas_centro = []
    if "jogo_iniciado" not in st.session_state:
        st.session_state.jogo_iniciado = False
    if "visualizando_jogador" not in st.session_state:
        st.session_state.visualizando_jogador = None

    # Estado para Mafia
    if "mafia_game" not in st.session_state:
        st.session_state.mafia_game = {
            "iniciado": False,
            "papeis": [],
            "atual": 0,
            "revelado": False,
        }

    # Estado para Spy
    if "spy_game" not in st.session_state:
        st.session_state.spy_game = {
            "iniciado": False,
            "palavras": [],
            "atual": 0,
            "revelado": False,
            "banco_spy": carregar_palavras_spy(),
        }


def distribuir_papeis_resistencia(jogadores):
    num_jogadores = len(jogadores)
    # Regra base do jogo: 1/3 dos jogadores (arredondado para baixo) são espiões, com um mínimo de 1.
    num_espioes = max(1, num_jogadores // 3)
    num_resistencia = num_jogadores - num_espioes

    papeis = ["🕵️ Espião (Traidor)"] * num_espioes + [
        "✊ Operativo (Resistência)"
    ] * num_resistencia
    random.shuffle(papeis)

    return dict(zip(jogadores, papeis)), []


def distribuir_papeis_lobisomem(jogadores):
    num_jogadores = len(jogadores)
    papeis_disponiveis = [
        "🐺 Lobisomem",
        "🐺 Lobisomem",
        "👁️ Vidente",
        "🦹 Ladrão",
        "🔄 Encrenqueiro",
    ]

    # No Lobisomem de Uma Noite, o baralho precisa ter sempre 3 cartas a mais que o número de jogadores.
    while len(papeis_disponiveis) < num_jogadores + 3:
        papeis_disponiveis.append("🌾 Aldeão")

    papeis_selecionados = papeis_disponiveis[: num_jogadores + 3]
    random.shuffle(papeis_selecionados)

    # Separa as cartas que vão para as mãos dos jogadores e as que sobram no centro da mesa
    papeis_distribuidos = dict(zip(jogadores, papeis_selecionados[:num_jogadores]))
    cartas_centro = papeis_selecionados[num_jogadores:]

    return papeis_distribuidos, cartas_centro


def app():
    inicializar_estado()

    st.header("🕵️ Dedução Social e Blefe")
    st.markdown("Descubra os traidores ou engane seus amigos. Escolha o seu jogo!")

    # Controle de abas/seleção de jogos do módulo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("✊ Resistência", use_container_width=True):
            st.session_state.jogo_social_ativo = "resistencia"
    with col2:
        if st.button("🐺 Lobisomem", use_container_width=True):
            st.session_state.jogo_social_ativo = "lobisomem"
    with col3:
        if st.button("🕵️‍♂️ Máfia", use_container_width=True):
            st.session_state.jogo_social_ativo = "mafia"
    with col4:
        if st.button("🕶️ Spy", use_container_width=True):
            st.session_state.jogo_social_ativo = "spy"

    st.divider()

    # --- LÓGICA: RESISTÊNCIA E LOBISOMEM ---
    # Ambos compartilham a mesma base de UI para cadastro e revelação de jogadores
    if st.session_state.jogo_social_ativo in ["resistencia", "lobisomem"]:
        nome_jogo = (
            "A Resistência"
            if st.session_state.jogo_social_ativo == "resistencia"
            else "Lobisomem de Uma Noite"
        )
        st.subheader(f"Variante: {nome_jogo}")

        if not st.session_state.jogo_iniciado:
            st.write("### 👥 Configuração de Jogadores")
            novo_jogador = st.text_input("Nome do Jogador:", key="novo_jogador_social")

            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Adicionar Jogador") and novo_jogador:
                    if novo_jogador not in st.session_state.jogadores_social:
                        st.session_state.jogadores_social.append(novo_jogador)
                        st.rerun()
            with c2:
                if st.button("Limpar Lista"):
                    st.session_state.jogadores_social = []
                    st.rerun()

            if st.session_state.jogadores_social:
                st.write(
                    "**Jogadores na partida:**",
                    ", ".join(st.session_state.jogadores_social),
                )

            # Validação do mínimo de jogadores de acordo com as regras oficiais de cada jogo
            min_jogadores = (
                5 if st.session_state.jogo_social_ativo == "resistencia" else 3
            )

            if len(st.session_state.jogadores_social) >= min_jogadores:
                if st.button(
                    "🚀 Iniciar Jogo e Sortear Papéis",
                    use_container_width=True,
                    type="primary",
                ):
                    if st.session_state.jogo_social_ativo == "resistencia":
                        papeis, centro = distribuir_papeis_resistencia(
                            st.session_state.jogadores_social
                        )
                    else:
                        papeis, centro = distribuir_papeis_lobisomem(
                            st.session_state.jogadores_social
                        )

                    st.session_state.papeis_distribuidos = papeis
                    st.session_state.cartas_centro = centro
                    st.session_state.jogo_iniciado = True
                    st.session_state.visualizando_jogador = None
                    st.rerun()
            else:
                st.info(
                    f"Adicione pelo menos {min_jogadores} jogadores para jogar esta variante."
                )

        else:
            st.success(
                "Papéis distribuídos! Passem o dispositivo para que cada um veja seu papel em segredo."
            )

            # Garante que cada jogador só consiga ver o seu próprio papel ao clicar no botão respectivo
            for jogador in st.session_state.jogadores_social:
                with st.expander(f"Visualizar papel de: {jogador}"):
                    if st.button(
                        f"👁️ Revelar meu papel ({jogador})", key=f"btn_{jogador}"
                    ):
                        st.session_state.visualizando_jogador = jogador

                    if st.session_state.visualizando_jogador == jogador:
                        papel = st.session_state.papeis_distribuidos[jogador]
                        st.markdown(f"### Seu papel é: **{papel}**")

                        # Lógica especial: Identificação mútua para facções do mal
                        if papel == "🕵️ Espião (Traidor)":
                            outros_espioes = [
                                j
                                for j, p in st.session_state.papeis_distribuidos.items()
                                if p == "🕵️ Espião (Traidor)" and j != jogador
                            ]
                            if outros_espioes:
                                st.error(
                                    f"Seus parceiros espiões são: {', '.join(outros_espioes)}"
                                )

                        elif papel == "🐺 Lobisomem":
                            outros_lobos = [
                                j
                                for j, p in st.session_state.papeis_distribuidos.items()
                                if p == "🐺 Lobisomem" and j != jogador
                            ]
                            if outros_lobos:
                                st.error(
                                    f"Seu parceiro lobisomem é: {', '.join(outros_lobos)}"
                                )

                        if st.button(
                            "🙈 Esconder e Passar a Vez", key=f"hide_{jogador}"
                        ):
                            st.session_state.visualizando_jogador = None
                            st.rerun()

            st.divider()

            if (
                st.session_state.jogo_social_ativo == "lobisomem"
                and st.session_state.cartas_centro
            ):
                with st.expander("👑 Ver Cartas do Centro (Apenas Narrador/Vidente)"):
                    st.write(
                        f"As cartas no centro são: **{', '.join(st.session_state.cartas_centro)}**"
                    )

            if st.button("🔄 Encerrar Partida"):
                st.session_state.jogo_iniciado = False
                st.session_state.papeis_distribuidos = {}
                st.session_state.cartas_centro = []
                st.rerun()

    # --- LÓGICA: MÁFIA / CIDADE DORME ---
    elif st.session_state.jogo_social_ativo == "mafia":
        st.subheader("🕵️‍♂️ Máfia / Cidade Dorme")

        if not st.session_state.mafia_game["iniciado"]:
            st.write("### ⚙️ Configuração da Partida")

            n_jogadores = st.number_input("Total de Jogadores na roda", 3, 50, 6)
            tema_mafia = st.text_input(
                "Papéis Temáticos com IA? (Ex: The Office, Harry Potter)",
                placeholder="Deixe em branco para o jogo padrão",
            )

            st.write("### 🎭 Distribuir Papéis")
            col1, col2 = st.columns(2)
            with col1:
                n_assassinos = st.number_input("🩸 Assassinos", 1, n_jogadores, 1)
                n_detetive = st.number_input("🔍 Detetives", 0, n_jogadores, 1)
            with col2:
                n_medico = st.number_input("💊 Médicos", 0, n_jogadores, 0)
                n_extras = st.number_input("➕ Papéis Customizados?", 0, 5, 0)

            # Permite estender o baralho base com papéis dinâmicos definidos pelo usuário
            papeis_extras_dict = {}
            if n_extras > 0:
                st.write("#### Criar Papéis Extras")
                for i in range(n_extras):
                    c1, c2 = st.columns([2, 1])
                    nome_papel = c1.text_input(
                        f"Nome do Papel {i+1}", f"Papel Extra {i+1}", key=f"name_ex_{i}"
                    )
                    qtd_papel = c2.number_input(
                        f"Qtd", 0, n_jogadores, 1, key=f"qtd_ex_{i}"
                    )
                    papeis_extras_dict[nome_papel] = qtd_papel

            total_especiais = (
                n_assassinos + n_detetive + n_medico + sum(papeis_extras_dict.values())
            )
            n_cidadaos = n_jogadores - total_especiais

            st.divider()

            # Valida se a soma das funções excede o número de jogadores informados
            if n_cidadaos < 0:
                st.error(
                    f"❌ **Erro!** Você distribuiu {total_especiais} papéis para apenas {n_jogadores} jogadores. Remova {abs(n_cidadaos)} papel(éis)."
                )
                btn_ready = False
            else:
                st.info(
                    f"✅ **Pronto!** {total_especiais} papéis especiais e {n_cidadaos} Cidadãos Comuns."
                )
                btn_ready = True

            if st.button(
                "Sortear e Começar",
                disabled=not btn_ready,
                use_container_width=True,
                type="primary",
            ):
                nomes_papeis = {
                    "assassino": "🩸 ASSASSINO",
                    "detetive": "🔍 DETETIVE",
                    "medico": "💊 MÉDICO",
                    "cidadao": "🏘️ CIDADÃO",
                }

                # Personalização via IA mantendo as tags de identificação para não quebrar a lógica de UI
                if (
                    "api_key" in st.session_state
                    and st.session_state["api_key"]
                    and tema_mafia.strip()
                ):
                    with st.spinner(f"Criando papéis no universo de '{tema_mafia}'..."):
                        try:
                            nomes_ia = gerar_conteudo_ia("mafia", tema=tema_mafia)
                            nomes_papeis["assassino"] = (
                                f"🩸 {nomes_ia['assassino'].upper()} (ASSASSINO)"
                            )
                            nomes_papeis["detetive"] = (
                                f"🔍 {nomes_ia['detetive'].upper()} (DETETIVE)"
                            )
                            nomes_papeis["medico"] = (
                                f"💊 {nomes_ia['medico'].upper()} (MÉDICO)"
                            )
                            nomes_papeis["cidadao"] = (
                                f"🏘️ {nomes_ia['cidadao'].upper()} (CIDADÃO)"
                            )
                        except Exception as e:
                            st.error(
                                "Falha na IA ao criar papéis temáticos. Usando papéis padrão..."
                            )

                # Constrói o baralho final multiplicando as strings pela quantidade
                baralho = (
                    [nomes_papeis["assassino"]] * n_assassinos
                    + [nomes_papeis["detetive"]] * n_detetive
                    + [nomes_papeis["medico"]] * n_medico
                    + [nomes_papeis["cidadao"]] * n_cidadaos
                )

                for nome, qtd in papeis_extras_dict.items():
                    baralho.extend([nome.upper()] * qtd)

                random.shuffle(baralho)
                st.session_state.mafia_game.update(
                    {"iniciado": True, "papeis": baralho, "atual": 0, "revelado": False}
                )
                st.rerun()

        else:
            atual = st.session_state.mafia_game["atual"]
            total = len(st.session_state.mafia_game["papeis"])

            # Fluxo iterativo: passa o dispositivo e revela papel 1 a 1
            if atual < total:
                st.progress((atual) / total)
                st.write(f"### 👤 Jogador {atual + 1} de {total}")

                if not st.session_state.mafia_game["revelado"]:
                    st.info("Passe o dispositivo para o próximo jogador da roda.")
                    if st.button(
                        "👁️ Clique para ver seu papel",
                        key=f"btn_rev_{atual}",
                        use_container_width=True,
                    ):
                        st.session_state.mafia_game["revelado"] = True
                        st.rerun()
                else:
                    papel = st.session_state.mafia_game["papeis"][atual]

                    # Usa verificação de substring nas tags mantidas "(ASSASSINO)" para definir a cor
                    if "ASSASSINO" in papel:
                        st.error(f"Seu papel é: **{papel}**")
                    elif "CIDADÃO" in papel:
                        st.markdown(f"### 🏘️ Seu papel é: **{papel}**")
                    else:
                        st.success(f"Seu papel é: **{papel}**")

                    if st.button(
                        "🙈 Entendido! Esconder e Passar",
                        key=f"btn_next_{atual}",
                        use_container_width=True,
                    ):
                        st.session_state.mafia_game["atual"] += 1
                        st.session_state.mafia_game["revelado"] = False
                        st.rerun()
            else:
                st.balloons()
                st.success("🏁 Todos os papéis foram distribuídos! A cidade dorme...")
                if st.button("🔄 Reiniciar Jogo", use_container_width=True):
                    st.session_state.mafia_game = {
                        "iniciado": False,
                        "papeis": [],
                        "atual": 0,
                        "revelado": False,
                    }
                    st.rerun()

    # --- LÓGICA: WHO IS THE SPY ---
    elif st.session_state.jogo_social_ativo == "spy":
        st.subheader("🕶️ Who is the Spy?")

        if not st.session_state.spy_game["iniciado"]:
            st.write("### ⚙️ Configuração")
            n = st.number_input("Número de Jogadores", 3, 20, 4)
            diff = st.selectbox("Dificuldade", ["Normal", "Hard"])
            tema_spy = st.text_input(
                "Tema Opcional (IA):", placeholder="Ex: Marcas Famosas, Comida..."
            )

            if st.button(
                "Sortear Palavras / Espião", use_container_width=True, type="primary"
            ):
                par = None

                # Tenta delegar a criação do par secreto (ex: Praia x Piscina) à IA
                if (
                    "api_key" in st.session_state
                    and st.session_state["api_key"]
                    and tema_spy.strip()
                ):
                    with st.spinner(f"Gerando pares secretos de '{tema_spy}'..."):
                        try:
                            par = gerar_conteudo_ia("spy", tema=tema_spy)
                        except Exception as e:
                            st.error("Erro na IA. Usando palavras aleatórias...")

                # Fallback ativado caso a IA retorne fora do padrão JSON esperado
                if not par or len(par) != 2:
                    banco = st.session_state.spy_game["banco_spy"]
                    par = random.choice(banco)

                p1, p2 = random.sample(list(par), 2)
                espiao = random.randint(0, n - 1)

                # Monta a distribuição: O espião pega p2 (ou nada no Hard), e os demais pegam p1
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
            # Fluxo iterativo, assim como na lógica da Máfia
            atual = st.session_state.spy_game["atual"]
            total_spy = len(st.session_state.spy_game["palavras"])

            if atual < total_spy:
                st.progress((atual) / total_spy)
                st.write(f"### 👤 Jogador {atual + 1} de {total_spy}")

                if not st.session_state.spy_game["revelado"]:
                    st.info("Pegue o celular para ver a sua palavra em segredo.")
                    if st.button(
                        f"👁️ Ver Minha Palavra",
                        key=f"spy_btn_{atual}",
                        use_container_width=True,
                    ):
                        st.session_state.spy_game["revelado"] = True
                        st.rerun()
                else:
                    st.success(
                        f"Sua palavra é: **{st.session_state.spy_game['palavras'][atual]}**"
                    )
                    if st.button(
                        "🙈 OK, Esconder e Passar!",
                        key=f"spy_next_{atual}",
                        use_container_width=True,
                    ):
                        st.session_state.spy_game["atual"] += 1
                        st.session_state.spy_game["revelado"] = False
                        st.rerun()
            else:
                st.balloons()
                st.success("🏁 Todos já viram! Comecem a dar suas dicas.")
                if st.button("🔄 Novo Jogo", use_container_width=True):
                    st.session_state.spy_game.update(
                        {
                            "iniciado": False,
                            "palavras": [],
                            "atual": 0,
                            "revelado": False,
                        }
                    )
                    st.rerun()


if __name__ == "__main__":
    app()

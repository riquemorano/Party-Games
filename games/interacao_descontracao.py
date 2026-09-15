import streamlit as st
import random
import os
import time
from utils.gemini import gerar_conteudo_ia

# --- CARREGAMENTO DE DADOS ---


# Utiliza cache para evitar leituras de disco a cada rerun da interface
@st.cache_data
def carregar_post_it():
    caminho_csv = os.path.join("data", "palavrasPostIt.csv")
    if os.path.exists(caminho_csv):
        try:
            import pandas as pd

            # Lê apenas a primeira coluna e remove valores nulos
            df = pd.read_csv(caminho_csv)
            return df.iloc[:, 0].dropna().astype(str).tolist()
        except Exception as e:
            st.warning(f"Erro ao ler CSV de Post-It: {e}")

    # Fallback estático caso o arquivo não exista ou ocorra erro de leitura
    return [
        "Silvio Santos",
        "Harry Potter",
        "Uma Geladeira",
        "Um Papagaio",
        "Homem-Aranha",
        "Monalisa",
        "Albert Einstein",
        "Um Micro-ondas",
        "Cleópatra",
        "Batman",
        "Um Abacaxi",
        "Michael Jackson",
        "Uma Árvore",
        "Super Mario",
        "Um Celular",
    ]


@st.cache_data
def carregar_eu_nunca():
    return [
        "Eu nunca fingi que estava no celular para evitar falar com alguém.",
        "Eu nunca cortei meu próprio cabelo e me arrependi.",
        "Eu nunca enviei uma mensagem para a pessoa errada e passei vergonha.",
        "Eu nunca comi algo que caiu no chão após a regra dos 5 segundos.",
        "Eu nunca pesquisei meu próprio nome no Google.",
    ]


@st.cache_data
def carregar_verdade_desafio():
    caminho = os.path.join("data", "sugestoesTruthOrDare.csv")
    if os.path.exists(caminho):
        try:
            import pandas as pd

            df = pd.read_csv(caminho, header=None, names=["texto", "tipo"])
            # Separa os dados em duas listas mapeadas pelas chaves do dicionário
            verdades = df[df["tipo"].str.strip().str.upper() == "VERDADE"][
                "texto"
            ].tolist()
            desafios = df[df["tipo"].str.strip().str.upper() == "DESAFIO"][
                "texto"
            ].tolist()
            return {"VERDADE": verdades, "DESAFIO": desafios}
        except Exception as e:
            st.warning("Erro ao ler o CSV de sugestões. Usando base padrão.")

    return {
        "VERDADE": [
            "Qual foi a maior mentira que você já contou?",
            "De quem você tem mais ciúmes?",
            "Qual foi o seu momento mais constrangedor?",
        ],
        "DESAFIO": [
            "Imite um animal escolhido pelo grupo por 1 minuto.",
            "Deixe a pessoa à sua direita enviar uma mensagem do seu celular.",
            "Dance sem música por 30 segundos.",
        ],
    }


def inicializar_estado():
    # Estrutura inicial do session_state para persistir dados durante os reruns do Streamlit
    if "jogo_interacao_ativo" not in st.session_state:
        st.session_state.jogo_interacao_ativo = None
    if "banco_post_it" not in st.session_state:
        st.session_state.banco_post_it = carregar_post_it()
    if "banco_eu_nunca" not in st.session_state:
        st.session_state.banco_eu_nunca = carregar_eu_nunca()
    if "banco_td" not in st.session_state:
        st.session_state.banco_td = carregar_verdade_desafio()

    # Controle de estado específico: Post-it
    if "postit_revelado" not in st.session_state:
        st.session_state.postit_revelado = False
        st.session_state.postit_palavra_atual = ""

    # Controle de estado específico: Verdade ou Desafio
    if "td_game" not in st.session_state:
        st.session_state.td_game = {
            "jogadores": [],
            "resultado_dado": "",
            "pergunta_de": "",
            "pergunta_para": "",
            "sugestao_atual": "",
        }


# --- FUNÇÕES DE SETUP RÁPIDO ---
def iniciar_duas_verdades():
    st.session_state.dv_fase = "preencher"
    st.session_state.jogo_interacao_ativo = "duas_verdades"


def iniciar_eu_nunca():
    if "en_frase_atual" not in st.session_state:
        st.session_state.en_frase_atual = random.choice(st.session_state.banco_eu_nunca)
    st.session_state.jogo_interacao_ativo = "eu_nunca"


def iniciar_vinte_perguntas():
    if "vp_palavra" not in st.session_state:
        st.session_state.vp_palavra = random.choice(st.session_state.banco_post_it)
    st.session_state.vp_contador = 0
    st.session_state.jogo_interacao_ativo = "vinte_perguntas"


def app():
    inicializar_estado()

    st.header("🍻 Interação e Descontração")
    st.markdown("Hora de quebrar o gelo, dar risadas e descobrir segredos dos amigos!")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🤥 2 Verdades 1 Mentira", use_container_width=True):
            iniciar_duas_verdades()
        if st.button("🏷️ Post-it na Testa", use_container_width=True):
            st.session_state.jogo_interacao_ativo = "post_it"
    with col2:
        if st.button("🫣 Eu Nunca", use_container_width=True):
            iniciar_eu_nunca()
        if st.button("🎲 Verdade ou Desafio", use_container_width=True):
            st.session_state.jogo_interacao_ativo = "truth_or_dare"
    with col3:
        if st.button("❓ 20 Perguntas", use_container_width=True):
            iniciar_vinte_perguntas()

    st.divider()

    # --- LÓGICA: DUAS VERDADES E UMA MENTIRA ---
    # Jogo estritamente manual. Não consome recursos de IA.
    if st.session_state.jogo_interacao_ativo == "duas_verdades":
        st.subheader("🤥 Duas Verdades e uma Mentira")

        if st.session_state.dv_fase == "preencher":
            st.info(
                "Preencha duas coisas verdadeiras sobre você e uma falsa. O app vai embaralhá-las!"
            )
            v1 = st.text_input("Verdade 1:")
            v2 = st.text_input("Verdade 2:")
            m1 = st.text_input("Mentira:")

            if st.button("Embaralhar e Desafiar o Grupo", type="primary"):
                if v1 and v2 and m1:
                    # Empacota e embaralha as opções para esconder a mentira
                    afirmacoes = [
                        {"texto": v1, "tipo": "Verdade", "cor": "green"},
                        {"texto": v2, "tipo": "Verdade", "cor": "green"},
                        {"texto": m1, "tipo": "Mentira", "cor": "red"},
                    ]
                    random.shuffle(afirmacoes)

                    st.session_state.dv_afirmacoes = afirmacoes
                    st.session_state.dv_fase = "jogar"
                    st.rerun()
                else:
                    st.warning("Preencha todos os campos antes de continuar.")

        elif st.session_state.dv_fase == "jogar":
            st.write("### Qual destas é a mentira?")
            for i, af in enumerate(st.session_state.dv_afirmacoes):
                with st.expander(f"Opção {i+1}: {af['texto']}"):
                    st.markdown(
                        f"<h3 style='color: {af['cor']};'>{af['tipo']}!</h3>",
                        unsafe_allow_html=True,
                    )

            if st.button("Nova Rodada (Novo Jogador)"):
                iniciar_duas_verdades()
                st.rerun()

    # --- LÓGICA: EU NUNCA ---
    elif st.session_state.jogo_interacao_ativo == "eu_nunca":
        st.subheader("🫣 Eu Nunca")

        tema_en = st.text_input(
            "Deseja um tema? (IA)",
            placeholder="Ex: Trabalho, Infância, Coisas constrangedoras...",
        )

        st.markdown(
            f"""
        <div style="background-color: #f0f2f6; padding: 40px; border-radius: 15px; text-align: center; margin: 20px 0; border: 2px dashed #2e7bcf;">
            <h2 style="color: #333;">{st.session_state.en_frase_atual}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🎲 Sortear Próxima Frase", use_container_width=True, type="primary"
        ):
            nova_frase = ""
            if (
                "api_key" in st.session_state
                and st.session_state["api_key"]
                and tema_en.strip()
            ):
                with st.spinner("Relembrando histórias..."):
                    try:
                        # Requisita múltiplas frases da IA para garantir variedade local, exibindo apenas uma
                        frases = gerar_conteudo_ia(
                            "eu_nunca", tema=tema_en, quantidade=3
                        )
                        nova_frase = random.choice(frases)
                    except Exception as e:
                        st.error("Erro na IA, usando frases padrão...")

            if not nova_frase:
                nova_frase = random.choice(st.session_state.banco_eu_nunca)
                # Garante que a mesma frase não se repita logo em seguida, se houver outras opções
                while (
                    nova_frase == st.session_state.en_frase_atual
                    and len(st.session_state.banco_eu_nunca) > 1
                ):
                    nova_frase = random.choice(st.session_state.banco_eu_nunca)

            st.session_state.en_frase_atual = nova_frase
            st.rerun()

    # --- LÓGICA: VINTE PERGUNTAS ---
    elif st.session_state.jogo_interacao_ativo == "vinte_perguntas":
        st.subheader("❓ 20 Perguntas")

        tema_vp = st.text_input(
            "Sugerir palavra temática? (IA)",
            placeholder="Ex: Filmes, Animais, Objetos Históricos...",
        )
        if st.button("🔄 Sortear Nova Palavra"):
            nova_palavra = ""
            if (
                "api_key" in st.session_state
                and st.session_state["api_key"]
                and tema_vp.strip()
            ):
                with st.spinner("Procurando algo desafiador..."):
                    try:
                        palavras = gerar_conteudo_ia(
                            "palavras_gerais", tema=tema_vp, quantidade=5
                        )
                        nova_palavra = random.choice(palavras)
                    except:
                        st.error("Falha na IA.")

            if not nova_palavra:
                nova_palavra = random.choice(st.session_state.banco_post_it)

            st.session_state.vp_palavra = nova_palavra
            st.session_state.vp_contador = 0
            st.rerun()

        with st.expander(
            "👀 Revelar Palavra Secreta (Apenas para quem vai responder)",
            expanded=False,
        ):
            st.markdown(
                f"<h1 style='text-align: center; color: #2e7bcf;'>{st.session_state.vp_palavra}</h1>",
                unsafe_allow_html=True,
            )

        # Limita visualmente o progresso em 1.0 (100%) para não quebrar a UI
        progresso = st.session_state.vp_contador / 20.0
        st.progress(min(progresso, 1.0))
        st.markdown(
            f"<h2 style='text-align: center;'>{st.session_state.vp_contador} / 20</h2>",
            unsafe_allow_html=True,
        )

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_a:
            if st.button(
                "➖ Desfazer",
                use_container_width=True,
                disabled=(st.session_state.vp_contador <= 0),
            ):
                st.session_state.vp_contador -= 1
                st.rerun()
        with col_b:
            if st.button(
                "➕ Fizeram Pergunta",
                type="primary",
                use_container_width=True,
                disabled=(st.session_state.vp_contador >= 20),
            ):
                st.session_state.vp_contador += 1
                st.rerun()
        with col_c:
            if st.button("🔄 Zerar", use_container_width=True):
                st.session_state.vp_contador = 0
                st.rerun()

        if st.session_state.vp_contador >= 20:
            st.error("🚨 Tempo esgotado! O grupo chegou a 20 perguntas.")

    # --- LÓGICA: POST-IT NA TESTA ---
    elif st.session_state.jogo_interacao_ativo == "post_it":
        st.subheader("🏷️ Post-it na Testa")
        st.write(
            "Digite um tema (opcional), clique no botão e vire a tela para sua testa! O grupo dará as dicas."
        )

        tema_postit = st.text_input(
            "Tema específico? (IA)",
            placeholder="Ex: Celebridades, Personagens de Desenho...",
        )

        if st.button("🚀 Sortear e Preparar", use_container_width=True, type="primary"):
            st.session_state.postit_revelado = False
            palavra_sorteada = ""

            # Resolve a chamada da IA antes do cronômetro para evitar lag enquanto o usuário já está aguardando
            if (
                "api_key" in st.session_state
                and st.session_state["api_key"]
                and tema_postit.strip()
            ):
                with st.spinner("Preparando Post-It..."):
                    try:
                        lista = gerar_conteudo_ia(
                            "palavras_gerais", tema=tema_postit, quantidade=5
                        )
                        palavra_sorteada = random.choice(lista)
                    except:
                        pass

            if not palavra_sorteada:
                palavra_sorteada = random.choice(st.session_state.banco_post_it)

            st.session_state.postit_palavra_atual = palavra_sorteada

            # Executa contador regressivo usando um placeholder para limpar a tela dinamicamente
            placeholder = st.empty()
            for i in range(3, 0, -1):
                placeholder.markdown(
                    f"<h1 style='text-align: center; color: #FF4B4B;'>Vire a tela em {i}...</h1>",
                    unsafe_allow_html=True,
                )
                time.sleep(1)
            placeholder.empty()

            st.session_state.postit_revelado = True
            st.rerun()

        if st.session_state.postit_revelado:
            st.markdown(
                f"""
                <div style='border: 5px dashed yellow; padding: 40px; background-color: #ffffcc; color: black; text-align: center; border-radius: 15px; box-shadow: 10px 10px 5px rgba(0,0,0,0.2);'>
                    <h1 style='font-size: 4rem; margin: 0;'>{st.session_state.postit_palavra_atual}</h1>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Limpar Tela / Próximo Jogo"):
                st.session_state.postit_revelado = False
                st.rerun()

    # --- LÓGICA: VERDADE OU DESAFIO ---
    elif st.session_state.jogo_interacao_ativo == "truth_or_dare":
        st.subheader("🎲 Verdade ou Desafio")

        tema_td = st.text_input(
            "Tema para as perguntas/desafios? (IA)",
            placeholder="Ex: Leve, Pesado, Engraçado, Romântico...",
        )

        st.write("### ⚡ Sorteio Rápido")
        if st.button("🔥 RODAR O DADO", use_container_width=True, type="primary"):
            st.session_state.td_game["resultado_dado"] = random.choice(
                ["VERDADE", "DESAFIO"]
            )

            # Realiza pareamento automático caso a lista de jogadores tenha nomes suficientes
            if len(st.session_state.td_game["jogadores"]) >= 2:
                dupla = random.sample(st.session_state.td_game["jogadores"], 2)
                st.session_state.td_game["pergunta_de"] = dupla[0]
                st.session_state.td_game["pergunta_para"] = dupla[1]

            st.session_state.td_game["sugestao_atual"] = ""

        if st.session_state.td_game["resultado_dado"]:
            res = st.session_state.td_game["resultado_dado"]
            cor = "#28a745" if res == "VERDADE" else "#dc3545"

            st.markdown(
                f"""
                <div style="text-align: center; padding: 30px; border-radius: 15px; border: 5px solid {cor}; background-color: rgba(0,0,0,0.05);">
                    <h1 style="color: {cor}; font-size: 3rem; margin: 0;">{res}</h1>
                </div>
            """,
                unsafe_allow_html=True,
            )

            if st.session_state.td_game["pergunta_de"]:
                st.info(
                    f"🎤 **{st.session_state.td_game['pergunta_de']}** pergunta para **{st.session_state.td_game['pergunta_para']}**"
                )

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.td_game["resultado_dado"]:
                tipo_atual = st.session_state.td_game["resultado_dado"]
                if st.button(
                    f"✨ Sugestão de {tipo_atual.capitalize()}",
                    use_container_width=True,
                ):
                    sugestao = ""

                    if (
                        "api_key" in st.session_state
                        and st.session_state["api_key"]
                        and tema_td.strip()
                    ):
                        with st.spinner("Criando sugestão..."):
                            try:
                                json_td = gerar_conteudo_ia(
                                    "truth_or_dare", tema=tema_td, quantidade=2
                                )
                                sugestao = random.choice(json_td[tipo_atual])
                            except Exception as e:
                                pass

                    # Fallback sequencial: Falha IA -> Busca no CSV local -> String padrão de erro
                    if not sugestao:
                        lista_sugestoes = st.session_state.banco_td.get(tipo_atual, [])
                        if lista_sugestoes:
                            sugestao = random.choice(lista_sugestoes)
                        else:
                            sugestao = f"Sem sugestões disponíveis para {tipo_atual}."

                    st.session_state.td_game["sugestao_atual"] = sugestao

        with col2:
            with st.popover("👥 Cadastrar Nomes (Opcional)", use_container_width=True):
                nomes_input = st.text_area("Nomes (um por linha):")
                if st.button("Salvar Lista de Jogadores"):
                    # Processa o bloco de texto convertendo em uma lista limpa
                    st.session_state.td_game["jogadores"] = [
                        n.strip() for n in nomes_input.split("\n") if n.strip()
                    ]
                    st.rerun()

        if st.session_state.td_game["sugestao_atual"]:
            st.chat_message("assistant").write(
                st.session_state.td_game["sugestao_atual"]
            )


if __name__ == "__main__":
    app()

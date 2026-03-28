import streamlit as st
import pandas as pd
import random
import os


def render_mafia_game():
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

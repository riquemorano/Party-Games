import streamlit as st

# Configuração da página (Deve ser o primeiro comando Streamlit do script)
st.set_page_config(
    page_title="Party Games Hub",
    page_icon="🎲",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Importando os 4 módulos dos jogos.
# Nota: Se você salvou os arquivos dentro da pasta 'games', 
# altere os imports para: from games import deducao_social, etc.
from games import deducao_social
from games import adivinhacao_palavras
from games import desenho_criatividade
from games import interacao_descontracao

def main():
    # --- MENU LATERAL (SIDEBAR) ---
    st.sidebar.title("🎲 Party Games")
    st.sidebar.markdown("Escolha a categoria:")

    pagina = st.sidebar.radio(
        "Navegação",
        [
            "🏠 Início",
            "🕵️ Dedução Social e Blefe",
            "🗣️ Adivinhação e Palavras",
            "🎨 Desenho e Criatividade",
            "🍻 Interação e Descontração"
        ],
        label_visibility="collapsed"
    )

    st.sidebar.divider()
    st.sidebar.info("💡 **Dica:** Alguns jogos precisam que os participantes não olhem a tela ao mesmo tempo. Siga as instruções de cada jogo!")

    # --- ROTEAMENTO DE PÁGINAS ---
    if pagina == "🏠 Início":
        st.title("🎲 Bem-vindo ao Party Games Hub!")
        st.markdown("""
        Esta é a sua central de jogos para festas e reuniões com amigos! 
        Navegue pelo menu lateral para explorar as categorias:
        
        * **🕵️ Dedução Social e Blefe:** Descubra quem é o traidor em *A Resistência* ou *Lobisomem de Uma Noite*.
        * **🗣️ Adivinhação e Palavras:** Teste sua sintonia com *Código Secreto*, *Just One*, *Tabu* e *Megasenha*.
        * **🎨 Desenho e Criatividade:** Dê risadas com *Gartic Phone (Telefone Sem Fio)* ou adivinhe ícones no *Concept*.
        * **🍻 Interação e Descontração:** Quebre o gelo com *2 Verdades e 1 Mentira*, *Eu Nunca* ou *20 Perguntas*.
        
        Reúna o grupo e divirtam-se!
        """)
        
    elif pagina == "🕵️ Dedução Social e Blefe":
        deducao_social.app()
        
    elif pagina == "🗣️ Adivinhação e Palavras":
        adivinhacao_palavras.app()
        
    elif pagina == "🎨 Desenho e Criatividade":
        desenho_criatividade.app()
        
    elif pagina == "🍻 Interação e Descontração":
        interacao_descontracao.app()

if __name__ == "__main__":
    main()
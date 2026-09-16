# 🎉 Party Games Hub

Bem-vindo ao **Party Games Hub**! Esta é a sua central de jogos interativa ideal para festas, reuniões com amigos e quebra-gelos. Construída com [Streamlit](https://streamlit.io/), a aplicação reúne diversos minigames clássicos e modernos, enriquecidos com o poder da Inteligência Artificial do Google Gemini para gerar temas e palavras personalizadas de forma infinita!

## 🎮 Categorias de Jogos

O aplicativo está dividido em 4 categorias principais para facilitar a diversão da sua turma:

1. **🕵️ Dedução Social e Blefe**
   - Descubra quem são os traidores, blefe para sobreviver e engane seus amigos.
   - *Exemplos:* A Resistência, Lobisomem, Máfia (Cidade Dorme), Who is the Spy.

2. **🧠 Adivinhação e Palavras**
   - Teste sua sintonia, raciocínio rápido e vocabulário.
   - *Exemplos:* Código Secreto (Codenames), Just One, Tabu, Megasenha, Stop/Adedonha, Mímica.

3. **🎨 Desenho e Criatividade**
   - Mostre suas habilidades artísticas (ou a falta delas) e divirta-se com interpretações hilárias.
   - *Exemplos:* Gartic (Telefone Sem Fio Desenhado), Concept, Draw & Guess.

4. **🤝 Interação e Descontração**
   - Perfeito para quebrar o gelo e dar boas risadas descobrindo segredos do grupo.
   - *Exemplos:* 2 Verdades e 1 Mentira, Eu Nunca, Verdade ou Desafio, 20 Perguntas, Post-it na Testa.

## 🤖 Integração com IA (Google Gemini)

O Party Games Hub utiliza a biblioteca `google-genai` para se conectar ao modelo **Gemini 3.1 Flash Lite**. Isso permite que você digite temas customizados (ex: "Séries dos anos 90", "Coisas de Escritório") e a IA gera na hora as palavras, cartas, ou situações para o jogo. 

Caso você não tenha internet ou a cota da API acabe, o aplicativo possui um sistema de *fallback* robusto, carregando palavras offline através de arquivos CSV locais.

## 🚀 Como Instalar e Rodar

### Pré-requisitos
- Python 3.8 ou superior instalado.
- Conta no [Google AI Studio](https://aistudio.google.com/) para obter a chave da API (opcional, mas recomendado).

### Passos de Instalação

1. Clone este repositório ou baixe os arquivos do projeto.
2. Navegue até o diretório do projeto via terminal:
   ```bash
   cd PartyGames
   ```
3. Instale as dependências listadas no arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   *(As principais dependências incluem `streamlit`, `pandas` e `google-genai`)*

4. Inicie a aplicação Streamlit:
   ```bash
   streamlit run app.py
   ```
5. O seu navegador abrirá automaticamente na página inicial do Hub (geralmente em `http://localhost:8501`).

## 🔑 Configurando a API Key do Gemini

A configuração da chave da API foi feita para ser simples e segura, sem precisar mexer no código:

1. Gere a sua API Key gratuita no [Google AI Studio](https://aistudio.google.com/).
2. Abra o Party Games Hub no seu navegador (rodando localmente).
3. No **Menu Lateral (Sidebar)** esquerdo, cole a sua chave no campo **"Insira sua API Key do Gemini"**.
4. Pressione "Enter". Uma mensagem de sucesso informará que a IA está pronta para uso em todos os minigames!
*(Nota: A chave é armazenada apenas na sessão atual do seu navegador).*

## 📁 Estrutura do Projeto

```text
PartyGames/
├── app.py                      # Arquivo principal que gerencia o menu e o roteamento.
├── requirements.txt            # Lista de dependências Python.
├── utils/
│   └── gemini.py               # Módulo responsável pelos prompts e comunicação com a API do Gemini.
├── games/
│   ├── adivinhacao_palavras.py # Lógica dos jogos de adivinhação.
│   ├── deducao_social.py       # Lógica dos jogos de blefe e papéis ocultos.
│   ├── desenho_criatividade.py # Lógica dos jogos envolvendo desenho e imagens.
│   └── interacao_descontracao.py # Lógica dos jogos casuais e de conversa.
└── data/                       # Arquivos .csv atuando como banco de dados offline (fallback).
    ├── palavrasDraw.csv
    ├── palavrasMimica.csv
    ├── palavrasPassword.csv
    ├── palavrasPostIt.csv
    ├── palavrasSpy.csv
    ├── sugestoesTruthOrDare.csv
    └── temasStop.csv
```

---
Feito com 💻 e muita diversão! Chame a galera e bom jogo!
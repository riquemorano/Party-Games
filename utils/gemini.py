from google import genai
import json
import streamlit as st


def gerar_conteudo_ia(jogo, tema="geral", quantidade=10):
    """
    Gera conteúdo via IA com base no jogo, tema e quantidade.
    Retorna uma lista de strings ou um dicionário JSON.
    """
    # Garante que a chave da API foi configurada no menu lateral (app.py) antes de prosseguir
    if "api_key" not in st.session_state or not st.session_state["api_key"]:
        raise ValueError(
            "Por favor, insira sua API Key do Gemini no menu lateral antes de jogar."
        )

    client = genai.Client(api_key=st.session_state["api_key"])

    # Centraliza as regras de negócio dos prompts para manter o formato de saída consistente (JSON)
    prompts = {
        # Adivinhação de Palavras
        "mimica": f"Gere {quantidade} palavras ou expressões curtas para um jogo de Mímica. Tema: {tema}. Responda APENAS com um array JSON de strings, sem formatação Markdown.",
        "stop": f"Gere {quantidade} categorias criativas para o jogo Stop/Adedanha. Tema: {tema}. Responda APENAS com um array JSON de strings.",
        "palavras_gerais": f"Gere {quantidade} palavras ou nomes (substantivos) para um jogo de adivinhação/post-it. Tema: {tema}. Responda APENAS com um array JSON de strings.",
        "tabu": f'Gere 1 palavra principal e 5 palavras proibidas (que não podem ser ditas) para o jogo Tabu. Tema: {tema}. Responda APENAS com um objeto JSON. Exemplo: {{"palavra": "Praia", "proibidas": ["Areia", "Mar", "Sol", "Verão", "Onda"]}}',
        # Dedução Social
        "spy": f'Gere 1 par de palavras ou expressões curtas que sejam semelhantes, mas diferentes, para o jogo Who is the Spy. Tema: {tema}. Responda APENAS com um array JSON de strings com EXATAMENTE 2 itens. Exemplo: ["Praia", "Piscina"]',
        "mafia": f'Gere nomes temáticos para os 4 papéis base do jogo Máfia (Cidade Dorme) baseados no tema: {tema}. Responda APENAS com um objeto JSON válido. Exemplo: {{"assassino": "Darth Vader", "detetive": "Mestre Yoda", "medico": "Princesa Leia", "cidadao": "Ewok"}}',
        # Desenho e Criatividade
        "desenho_situacao": f"Gere {quantidade} frases curtas descrevendo situações inusitadas, engraçadas ou absurdas para desenhar (ex: 'Um dinossauro andando de skate'). Tema: {tema}. Responda APENAS com um array JSON de strings.",
        # Interação e Descontração
        "eu_nunca": f"Gere {quantidade} frases inusitadas, criativas e divertidas para o jogo 'Eu Nunca' (Never have I ever). Tema: {tema}. Todas devem obrigatoriamente começar com 'Eu nunca'. Responda APENAS com um array JSON de strings.",
        "truth_or_dare": f"Gere {quantidade} perguntas de 'Verdade' e {quantidade} de 'Desafio' divertidas para uma festa. Tema: {tema}. Responda APENAS com um objeto JSON válido com as chaves exatas 'VERDADE' e 'DESAFIO' contendo arrays de strings. Exemplo: {{\"VERDADE\": [\"Qual seu maior segredo?\"], \"DESAFIO\": [\"Dance uma música no mudo.\"]}}",
        "perguntas_conexao": f"Gere {quantidade} perguntas criativas, profundas, reflexivas ou hipotéticas para amigos, namorados ou casais se conhecerem melhor. Tema/Estilo: {tema}. Responda APENAS com um array JSON de strings.",    
    }

    prompt = prompts.get(jogo)
    if not prompt:
        raise ValueError("Jogo não reconhecido para geração de IA.")

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite", contents=prompt
        )

        # Remove formatação Markdown caso a IA retorne blocos de código (ex: ```json ... ```)
        texto_limpo = response.text.replace("```json", "").replace("```", "").strip()
        resultado = json.loads(texto_limpo)

        return resultado

    except Exception as e:
        raise Exception(f"Erro ao gerar com IA: {e}")

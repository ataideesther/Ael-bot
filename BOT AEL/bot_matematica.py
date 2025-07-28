from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

llm = OllamaLLM(model="mistral")

# 1. Apresentação inicial
intro = """
Você é um professor de matemática sarcástico, provocador e debochado, com um único objetivo: ensinar sem nunca dar a 
resposta pronta, além disso ,ajuda os alunos a entender conceitos, explicando ideias e fazendo perguntas aos alunos.
Você instiga, provoca e desafia o aluno a pensar por si só. Sua missão é desenvolver o raciocínio lógico e a autonomia
do estudante, mesmo que ele insista em "facilitar".
"""

print("\n  Bem-vindo ao Bot de Matemática Provocador!")
print("Digite 'sair' para encerrar.\n")

# 2. Perguntas sequenciais com controle de estado
etapas = [
    {
        "pergunta": "Primeiro, me diga: o que você gostaria de aprender hoje?",
        "variavel": "topico"
    },
    {
        "pergunta": "Você é do ensino médio, universitário ou profissional?",
        "variavel": "nivel"
    },
    {
        "pergunta": "O que você já sabe sobre esse tópico?",
        "variavel": "conhecimento_previo"
    }
]

contexto = {}

for etapa in etapas:
    while True:
        resposta = input(f"\nProfessor: {etapa['pergunta']}\nVocê: ")

        if resposta.lower() in ['sair', 'exit', 'quit']:
            print("Professor: Desistir já? Nem chegamos à parte divertida!")
            exit()

        if resposta.strip():  # Verifica se a resposta não está vazia
            contexto[etapa['variavel']] = resposta
            break
        else:
            print("Professor: Não vai responder? Tá com medo do desafio?")

# 3. Fase de ensino personalizado
template_ensino = """
Você é um professor de matemática sarcástico. 
Contexto do aluno:
- Tópico: {topico}
- Nível: {nivel}
- Conhecimento prévio: {conhecimento_previo}

Agora, comece a ensinar sobre {topico} para um aluno de nível {nivel} que sabe {conhecimento_previo}.
Use seu estilo  ironico e provocador, mas pedagógico. Faça UMA pergunta por vez e espere a resposta.
"""

prompt_ensino = PromptTemplate.from_template(template_ensino)
chain = prompt_ensino | llm

print("\nProfessor: Excelente! Agora vamos começar...\n")

while True:
    # Gera a próxima pergunta do professor
    resposta_prof = chain.invoke(contexto)

    # Pega a resposta do aluno
    resposta_aluno = input(f"Professor: {resposta_prof}\nVocê: ")

    if resposta_aluno.lower() in ['sair', 'exit', 'quit']:
        print("Professor: Fugindo no meio do desafio? Típico!")
        break

    # Atualiza o contexto com a última interação
    contexto["ultima_resposta"] = resposta_aluno
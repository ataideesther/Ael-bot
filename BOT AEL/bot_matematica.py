from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

llm = OllamaLLM(model="mistral")

# Template com foco em não dar respostas e sarcasmo controlado
template = """
Você é um professor de matemática extremamente sarcástico, mas que NUNCA dá respostas prontas.
Seu objetivo é fazer o aluno pensar por si mesmo através de perguntas provocativas e orientações.

REGRAS ABSOLUTAS:
1. NUNCA dê a resposta final ou solução completa
2. Faça perguntas que guiem o raciocínio do aluno
3. Use sarcasmo leve que não atrapalhe o entendimento
4. Dê dicas, pistas e caminhos, nunca respostas
5. Foque no processo de pensamento, não no resultado

Estilo de ensino:
- Perguntas orientadoras que quebram o problema em partes
- Dicas sutis sobre onde procurar a solução
- Críticas humorísticas mas construtivas
- Analogias mínimas e apenas quando realmente úteis

Histórico recente:
{historico}

Usuário: {input}
Professor: 
"""

prompt = PromptTemplate.from_template(template)
chain = prompt | llm

print("\n Professor de Matemática (Sarcástico mas Útil)")
print("Digite 'sair' para encerrar\n")
print("Professor: Então quer aprender matemática? Prepare-se para pensar de verdade!")
print("Professor: Não espere respostas prontas - vou fazer você suar os neurônios!")

historico_conversa = ""

while True:
    pergunta_usuario = input("\nVocê: ")
    
    if pergunta_usuario.lower() in ['sair', 'exit', 'quit', 'bye']:
        print("Professor: Desistindo já? Matemática não é para os fracos!")
        break
        
    if not pergunta_usuario.strip():
        print("Professor: O silêncio não resolve equações, meu caro!")
        continue
    
    try:
        resposta = chain.invoke({
            "input": pergunta_usuario,
            "historico": historico_conversa
        })
        
        print(f"\nProfessor: {resposta}")
        
        # Atualiza o histórico mantendo contexto
        historico_conversa += f"Aluno: {pergunta_usuario}\nProfessor: {resposta}\n"
        
        # Limita o histórico
        if len(historico_conversa.split('\n')) > 8:
            historico_conversa = '\n'.join(historico_conversa.split('\n')[-6:])
            
    except Exception as e:
        print("Professor: Meus circuitos estão com preguiça... Tente outra pergunta!")
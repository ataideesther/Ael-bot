import ollama
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate

class MathBot:
    def __init__(self):
        self.llm = Ollama(model="mistral")
        self.contexto = {}
        
    def iniciar_conversa(self, topico, nivel, conhecimento_previo):
        """Inicia a conversa com o contexto do aluno"""
        self.contexto = {
            "topico": topico,
            "nivel": nivel,
            "conhecimento_previo": conhecimento_previo
        }
        
        template_ensino = """
        Você é um professor de matemática sarcástico, provocador e debochado, com um único objetivo: ensinar sem nunca dar a 
        resposta pronta, além disso, ajuda os alunos a entender conceitos, explicando ideias e fazendo perguntas aos alunos.
        Você instiga, provoca e desafia o aluno a pensar por si só. Sua missão é desenvolver o raciocínio lógico e a autonomia
        do estudante, mesmo que ele insista em "facilitar".

        Contexto do aluno:
        - Tópico: {topico}
        - Nível: {nivel}
        - Conhecimento prévio: {conhecimento_previo}

        Agora, comece a ensinar sobre {topico} para um aluno de nível {nivel} que sabe {conhecimento_previo}.
        Use seu estilo irônico e provocador, mas pedagógico. Faça UMA pergunta por vez.
        """
        
        prompt_ensino = PromptTemplate.from_template(template_ensino)
        chain = prompt_ensino | self.llm
        
        # Primeira mensagem do professor
        resposta_prof = chain.invoke(self.contexto)
        return resposta_prof
    
    def responder_aluno(self, resposta_aluno):
        """Processa a resposta do aluno e retorna a próxima pergunta do professor"""
        # Atualiza o contexto com a última resposta
        self.contexto["ultima_resposta"] = resposta_aluno
        
        template_resposta = """
        Você é um professor de matemática sarcástico e provocador. 
        Contexto do aluno:
        - Tópico: {topico}
        - Nível: {nivel}
        - Conhecimento prévio: {conhecimento_previo}
        - Última resposta do aluno: {ultima_resposta}

        Continue ensinando sobre {topico}. Analise a resposta do aluno, corrija se necessário de forma provocadora,
        e faça a próxima pergunta para continuar o aprendizado. Seja irônico mas pedagógico.
        """
        
        prompt_resposta = PromptTemplate.from_template(template_resposta)
        chain = prompt_resposta | self.llm
        
        resposta_prof = chain.invoke(self.contexto)
        return resposta_prof
    
    def ask_question(self, question, session_data=None):
        """Método simplificado para perguntas diretas"""
        if session_data:
            self.contexto = session_data
        
        template_simples = """
        Você é um professor de matemática sarcástico, provocador e debochado.
        Responda à pergunta do aluno de forma educada mas com ironia, sem dar a resposta pronta.
        Instigue o aluno a pensar por si mesmo.
        
        Pergunta: {question}
        
        Resposta:
        """
        
        prompt = PromptTemplate.from_template(template_simples)
        chain = prompt | self.llm
        
        response = chain.invoke({"question": question})
        return response
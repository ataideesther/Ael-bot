import re
import os
import json
from datetime import datetime
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from typing import List, Dict, Any

class MathBot:
    def __init__(self, persist_directory="./math_knowledge_db"):
        self.llm = OllamaLLM(model="deepseek-r1:latest")
        self.embeddings = OllamaEmbeddings(model="deepseek-r1:latest")
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.contexto = {}
        self.historico_conversa = []
        self.exercicio_atual = None
        self._inicializar_banco_conhecimento()
        
    def _inicializar_banco_conhecimento(self):
        """Inicializa o banco de conhecimento matemático para RAG com persistência"""
        documentos_matematica = [
            Document(page_content="Teorema de Pitágoras: a² + b² = c², onde c é a hipotenusa de um triângulo retângulo"),
            Document(page_content="Área do círculo: A = π * r², onde r é o raio do círculo"),
            Document(page_content="Fórmula de Bhaskara: x = [-b ± √(b² - 4ac)] / 2a, para equações quadráticas ax² + bx + c = 0"),
            Document(page_content="Logaritmo: log_b(a) = c significa b^c = a. Logaritmo natural usa base e (≈2.718)"),
            Document(page_content="Derivada: medida da taxa de variação instantânea de uma função f'(x) = lim(h→0)[f(x+h)-f(x)]/h"),
            Document(page_content="Integral: operação inversa da derivada, calcula área sob a curva ∫f(x)dx = F(x) + C"),
            Document(page_content="Números primos: números naturais maiores que 1 divisíveis apenas por 1 e por si mesmos"),
            Document(page_content="Teorema Fundamental da Aritmética: todo número natural >1 pode ser escrito como produto único de primos"),
            Document(page_content="Função quadrática: f(x) = ax² + bx + c, gráfico é uma parábola com vértice em x = -b/2a"),
            Document(page_content="Progressão aritmética: a_n = a₁ + (n-1)*r, onde r é a razão constante entre termos"),
            Document(page_content="Progressão geométrica: a_n = a₁ * r^(n-1), onde r é a razão constante entre termos"),
            Document(page_content="Teorema de Tales: retas paralelas cortadas por transversais formam segmentos proporcionais"),
            Document(page_content="Seno, cosseno e tangente: razões trigonométricas em triângulos retângulos"),
            Document(page_content="Matrizes: arranjos retangulares de números, usadas em álgebra linear e transformações"),
            Document(page_content="Estatística básica: média, mediana, moda, desvio padrão e variância")
        ]
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        docs_split = text_splitter.split_documents(documentos_matematica)
        
        self.vectorstore = Chroma.from_documents(
            documents=docs_split,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    def _buscar_contexto_relevante(self, pergunta, k=3):
        """Busca informações relevantes no banco de conhecimento usando RAG"""
        try:
            documentos_relevantes = self.vectorstore.similarity_search(pergunta, k=k)
            contexto = "\n".join([f"• {doc.page_content}" for doc in documentos_relevantes])
            return contexto
        except Exception as e:
            print(f"Erro na busca RAG: {e}")
            return ""

    def _limpar_pensamento(self, texto):
        """Remove blocos de pensamento (<think>...</think>) das respostas."""
        if not isinstance(texto, str):
            return texto
        texto_sem_think = re.sub(r"<think>[\s\S]*?</think>", "", texto, flags=re.IGNORECASE)
        texto_sem_think = re.sub(r"<think>[\s\S]*$", "", texto_sem_think, flags=re.IGNORECASE)
        return texto_sem_think.strip()
    
    def _avaliar_resposta(self, resposta_aluno, pergunta_original):
        """Avalia se a resposta do aluno está correta baseada no contexto"""
        contexto_avaliacao = self._buscar_contexto_relevante(pergunta_original, k=2)
        
        prompt_avaliacao = """
        Você é um professor de matemática sarcástico. Avalie a resposta do aluno de forma provocadora.
        
        Contexto matemático:
        {contexto}
        
        Pergunta original: {pergunta}
        Resposta do aluno: {resposta}
        
        Responda de forma sarcástica e debochada, indicando se está CORRETO ou INCORRETO.
        """
        
        prompt = PromptTemplate.from_template(prompt_avaliacao)
        chain = prompt | self.llm
        
        avaliacao = chain.invoke({
            "contexto": contexto_avaliacao,
            "pergunta": pergunta_original,
            "resposta": resposta_aluno
        })
        
        return self._limpar_pensamento(avaliacao)
    
    def _adicionar_ao_historico(self, papel: str, mensagem: str):
        """Adiciona mensagem ao histórico da conversa"""
        self.historico_conversa.append({
            "papel": papel,
            "mensagem": mensagem,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.historico_conversa) > 20:
            self.historico_conversa = self.historico_conversa[-20:]

    def iniciar_conversa(self):
        """Inicia a conversa com o professor sarcástico de forma direta"""
        self.contexto = {}
        self.historico_conversa = []
        
        template_ensino = """
        Você é um professor de matemática EXTREMAMENTE sarcástico, provocador e debochado. 
        Seu estilo é irritantemente inteligente e você adora humilhar alunos preguiçosos.
        
        Sua primeira mensagem deve ser CURTA e DIRETA:
        - Uma apresentação arrogante e sarcástica em 1-2 linhas
        - Uma ordem direta para o aluno enviar um exercício
        - Deixar claro que você NUNCA dará respostas prontas
        - Terminar com uma provocação rápida
        
        NÃO explique conceitos matemáticos!
        NÃO dê exemplos!
        NÃO fale sobre fórmulas específicas!
        
        Apenas se apresente e peça o exercício de forma sarcástica.
        """
        
        prompt_ensino = PromptTemplate.from_template(template_ensino)
        chain = prompt_ensino | self.llm
        
        resposta_prof = chain.invoke({})
        
        resposta_limpa = self._limpar_pensamento(resposta_prof)
        self._adicionar_ao_historico("professor", resposta_limpa)
        
        return resposta_limpa
    
    def processar_exercicio(self, exercicio_aluno):
        """Processa o exercício enviado pelo aluno com muito sarcasmo"""
        self.exercicio_atual = exercicio_aluno
        self._adicionar_ao_historico("aluno", f"Exercício: {exercicio_aluno}")
        
        # Buscar contexto relevante para o exercício
        contexto_rag = self._buscar_contexto_relevante(exercicio_aluno)
        
        template_exercicio = """
        Você é o professor de matemática mais sarcástico e debochado do universo.
        
        EXERCÍCIO DO ALUNO: {exercicio}
        
        Conhecimento matemático relevante:
        {conhecimento}
        
        Sua resposta deve:
        1. Ser extremamente sarcástica sobre o exercício
        2. NEGAR dar a resposta pronta
        3. PERGUNTAR se o aluno sabe por onde começar
        4. Oferecer ajuda para entender conceitos, não respostas
        5. Ser provocativo mas focado em guiar o raciocínio
        
        Exemplo do que NÃO fazer:
        - Explicar fórmulas sem ser perguntado
        - Dar a resposta ou passo a passo
        - Fazer todo o raciocínio pelo aluno
        
        Exemplo do que fazer:
        - "Ah, Pitágoras? Você ao menos sabe o que é um triângulo retângulo?"
        - "Vou te ajudar a pensar, não a copiar. Por onde você acha que começa?"
        - "Que tal tentar lembrar qual teorema se aplica aqui?"
        """
        
        prompt_exercicio = PromptTemplate.from_template(template_exercicio)
        chain = prompt_exercicio | self.llm
        
        resposta_prof = chain.invoke({
            "exercicio": exercicio_aluno,
            "conhecimento": contexto_rag
        })
        
        resposta_limpa = self._limpar_pensamento(resposta_prof)
        self._adicionar_ao_historico("professor", resposta_limpa)
        
        return resposta_limpa
    
    def responder_aluno(self, resposta_aluno):
        """Processa a resposta do aluno com sarcasmo máximo"""
        self.contexto["ultima_resposta"] = resposta_aluno
        self._adicionar_ao_historico("aluno", resposta_aluno)
        
        # Avaliar a resposta do aluno com sarcasmo
        avaliacao = self._avaliar_resposta(resposta_aluno, self.exercicio_atual)
        
        # Buscar contexto relevante
        contexto_rag = self._buscar_contexto_relevante(self.exercicio_atual)
        
        template_resposta = """
        Você é um professor de matemática insuportavelmente sarcástico.
        
        EXERCÍCIO EM ANDAMENTO: {exercicio}
        Avaliação da última resposta: {avaliacao}
        
        Conhecimento relevante:
        {conhecimento}
        
        Última resposta do aluno: {ultima_resposta}

        Sua resposta deve:
        1. Analisar a resposta do aluno de forma sarcástica mas construtiva
        2. Se estiver errado, explicar o erro sem dar a resposta
        3. Fazer perguntas que guiem para o próximo passo
        4. Oferecer dicas conceituais se necessário
        5. Manter o foco no raciocínio, não na resposta final
        6. Ser provocativo mas pedagógico
        
        Lembre-se: você é sarcástico mas quer que o aluno aprenda a pensar.
        """
        
        prompt_resposta = PromptTemplate.from_template(template_resposta)
        chain = prompt_resposta | self.llm
        
        resposta_prof = chain.invoke({
            "exercicio": self.exercicio_atual,
            "ultima_resposta": resposta_aluno,
            "conhecimento": contexto_rag,
            "avaliacao": avaliacao
        })
        
        resposta_limpa = self._limpar_pensamento(resposta_prof)
        self._adicionar_ao_historico("professor", resposta_limpa)
        
        return resposta_limpa
    
    def ask_question(self, question, session_data=None):
        """Método para perguntas diretas com sarcasmo"""
        if session_data:
            self.contexto = session_data
        
        contexto_rag = self._buscar_contexto_relevante(question)
        
        template_simples = """
        Você é um professor de matemática sarcástico, provocador e debochado.
        
        Conhecimento relevante:
        {conhecimento}
        
        Responda à pergunta do aluno da forma mais sarcástica possível.
        NUNCA dê a resposta pronta. Instigue o aluno a pensar por si mesmo.
        
        Pergunta: {question}
        
        Resposta sarcástica:
        """
        
        prompt = PromptTemplate.from_template(template_simples)
        chain = prompt | self.llm
        
        response = chain.invoke({
            "question": question,
            "conhecimento": contexto_rag
        })
        
        resposta_limpa = self._limpar_pensamento(response)
        self._adicionar_ao_historico("aluno", question)
        self._adicionar_ao_historico("professor", resposta_limpa)
        
        return resposta_limpa

    # ... (os outros métodos permanecem iguais)

# Exemplo de uso CORRETO
if __name__ == "__main__":
    bot = MathBot()
    
    # Iniciar conversa de forma direta e sarcástica
    print("Professor:", bot.iniciar_conversa())
    
    # Aluno envia um exercício
    exercicio = "Preciso resolver: Calcule a hipotenusa de um triângulo retângulo com catetos 3 e 4"
    print("Aluno:", exercicio)
    print("Professor:", bot.processar_exercicio(exercicio))
    
    # Aluno tenta responder
    resposta = "Acho que é a² + b² = c²"
    print("Aluno:", resposta)
    print("Professor:", bot.responder_aluno(resposta))
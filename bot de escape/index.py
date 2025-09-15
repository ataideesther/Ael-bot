import re
import os
import json
import time
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
            Document(page_content="Teorema de Tales: retas paralelas cortadas por transversais formam segmentos proporcionales"),
            Document(page_content="Seno, cosseno e tangente: razões trigonométricas em triângulos retângulos"),
            Document(page_content="Matrizes: arranjos retangulares de números, usadas em álgebra linear e transformações"),
            Document(page_content="Estatística básica: média, mediana, moda, desvio padrão e variância"),
            Document(page_content="Probabilidade: medida da chance de um evento ocorrer, entre 0 e 1"),
            Document(page_content="Equação de uma reta: y = mx + b, onde m é a inclinação e b é o intercepto"),
            Document(page_content="Equação de uma circunferência: (x - h)² + (y - k)² = r², onde (h, k) é o centro e r é o raio"),
            Document(page_content="Equação de uma parábola: y = ax² + bx + c, onde a, b e c são constantes"),
            Document(page_content="Equação de uma elipse: (x - h)²/a² + (y - k)²/b² = 1, onde (h, k) é o centro e a e b são os semi-eixos"),
            Document(page_content="Equação de uma hipérbole: (x - h)²/a² - (y - k)²/b² = 1, onde (h, k) é o centro e a e b são os semi-eixos"),
            Document(page_content="Equação de uma elipse: (x - h)²/a² + (y - k)²/b² = 1, onde (h, k) é o centro e a e b são os semi-eixos"),  
            Document(page_content="regras de sinais adição e substração : + com + = +, + com - = -, - com + = -, - com - = +"),
            Document(page_content="regras de sinais multiplicação e divisão: + * + = +, + * - = -, - * + = -, - * - = +"),



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
        
        REGRAS (OBRIGATÓRIO):
        - NÃO revele a resposta correta nem resultados numéricos finais.
        - NÃO forneça o passo a passo completo.
        - Se precisar citar resultados, use placeholders como [valor], [passo], [resultado].
        
        Saída curta:
        - Julgamento: CORRETO/INCORRETO + provocação (1 linha)
        - 1 dica conceitual (sem contas)
        - 1 pergunta para o próximo passo
        """
        
        prompt = PromptTemplate.from_template(prompt_avaliacao)
        avaliacao = self._gerar_resposta_streaming(prompt, {
            "contexto": contexto_avaliacao,
            "pergunta": pergunta_original,
            "resposta": resposta_aluno
        })
        
        return avaliacao
    
    def _adicionar_ao_historico(self, papel: str, mensagem: str):
        """Adiciona mensagem ao histórico da conversa"""
        self.historico_conversa.append({
            "papel": papel,
            "mensagem": mensagem,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.historico_conversa) > 20:
            self.historico_conversa = self.historico_conversa[-20:]

    def _gerar_resposta_streaming(self, prompt, variaveis: dict):
        """Gera resposta em streaming palavra por palavra, ocultando blocos <think>"""
        resposta_final = ""
        dentro_think = False
        buffer_palavra = ""

        try:
            # Primeiro, obtemos a resposta completa para processar
            resposta_completa = self.llm.invoke(prompt.format(**variaveis))
            resposta_final = resposta_completa
            
            # Processa caractere por caractere para streaming
            for char in resposta_completa:
                resposta_final += char
                
                # Detecta início do bloco <think>
                if "<think>" in buffer_palavra.lower():
                    dentro_think = True
                    buffer_palavra = ""
                    continue
                
                # Detecta fim do bloco </think>
                if "</think>" in buffer_palavra.lower():
                    dentro_think = False
                    buffer_palavra = ""
                    continue
                
                # Acumula caracteres para formar palavras
                buffer_palavra += char
                
                # Se encontrou um espaço ou pontuação, exibe a palavra completa
                if char in ' .,!?;:\n\t' and buffer_palavra.strip():
                    palavra_completa = buffer_palavra.strip()
                    
                    # Só mostra se não estiver dentro do bloco <think>
                    if not dentro_think and palavra_completa:
                        print(palavra_completa, end=" ", flush=True)
                        # Pequena pausa para efeito de digitação
                        time.sleep(0.05)
                    
                    buffer_palavra = ""
                
                # Se o buffer ficar muito grande (para evitar problemas com tags longas)
                if len(buffer_palavra) > 50:
                    if not dentro_think:
                        print(buffer_palavra, end="", flush=True)
                    buffer_palavra = ""

            # Exibe qualquer palavra restante no buffer
            if buffer_palavra and not dentro_think:
                print(buffer_palavra, end="", flush=True)

            print()  # quebra de linha no fim
            
        except Exception as e:
            print(f"\n[ERRO STREAMING]: {e}")

        return self._limpar_pensamento(resposta_final)

    def iniciar_conversa(self):
        """Inicia a conversa com o professor sarcástico de forma direta"""
        self.contexto = {}
        self.historico_conversa = []
        
        template_ensino = """
        Você é um professor de matemática sarcástico, provocador e debochado. 
        Seu estilo é irritantemente inteligente e você adora provocar alunos preguiçosos.
        
        Sua primeira mensagem deve ser CURTA e DIRETA:
        - Uma apresentação sarcástica em 1-2 linhas
        - Uma ordem direta para o aluno enviar um exercício
        - Deixar claro que você NUNCA dará respostas prontas (nem valores numéricos)
        - Terminar com uma provocação rápida
        """
        
        prompt_ensino = PromptTemplate.from_template(template_ensino)
        resposta_prof = self._gerar_resposta_streaming(prompt_ensino, {})
        
        self._adicionar_ao_historico("professor", resposta_prof)
        return resposta_prof
    
    def processar_exercicio(self, exercicio_aluno):
        """Processa o exercício enviado pelo aluno com sarcasmo"""
        self.exercicio_atual = exercicio_aluno
        self._adicionar_ao_historico("aluno", f"Exercício: {exercicio_aluno}")
        
        contexto_rag = self._buscar_contexto_relevante(exercicio_aluno)
        
        template_exercicio = """
        Você é o professor de matemática mais sarcástico e debochado do universo.
        
        EXERCÍCIO DO ALUNO: {exercicio}
        
        Conhecimento matemático relevante:
        {conhecimento}
        
        Sua resposta deve:
        1. Ser sarcástica sobre o exercício
        2. PERGUNTAR se o aluno sabe por onde começar
        3. Oferecer ajuda para entender conceitos, não respostas
        4. Ser provocativo mas focado em guiar o raciocínio
        REGRAS RÍGIDAS (NÃO QUEBRE):
        - NÃO dê a resposta pronta.
        - NÃO escreva valores numéricos finais nem igualdades resolvidas (ex.: x = [número]).
        - NÃO faça o passo a passo completo; entregue apenas a próxima pista.
        - Se precisar mencionar resultados, use placeholders como [valor], [número], [resultado].
        - Foque em perguntas orientadoras e dicas conceituais curtas.
        
        Formato (obrigatório):
        1) 2-3 perguntas guiadas sobre o primeiro/próximo passo
        2) 1 dica conceitual (sem contas)
        3) 1 provocação curta
        """
        
        prompt_exercicio = PromptTemplate.from_template(template_exercicio)
        resposta_prof = self._gerar_resposta_streaming(prompt_exercicio, {
            "exercicio": exercicio_aluno,
            "conhecimento": contexto_rag
        })
        
        self._adicionar_ao_historico("professor", resposta_prof)
        return resposta_prof
    
    def responder_aluno(self, resposta_aluno):
        """Processa a resposta do aluno com sarcasmo máximo"""
        self.contexto["ultima_resposta"] = resposta_aluno
        self._adicionar_ao_historico("aluno", resposta_aluno)
        
        avaliacao = self._avaliar_resposta(resposta_aluno, self.exercicio_atual)
        contexto_rag = self._buscar_contexto_relevante(self.exercicio_atual)
        
        template_resposta = """
        Você é um professor de matemática sarcástico.
        
        EXERCÍCIO EM ANDAMENTO: {exercicio}
        Avaliação da última resposta: {avaliacao}
        
        Conhecimento relevante:
        {conhecimento}
        
        Última resposta do aluno: {ultima_resposta}
        
        REGRAS RÍGIDAS (NÃO QUEBRE):
        - NÃO revele resultados numéricos finais nem expressões resolvidas (ex.: x = [número]).
        - NÃO faça o passo a passo completo; apenas a próxima pista.
        - Se for inevitável mencionar um resultado, substitua por [valor], [passo], [resultado].
        
        Sua resposta deve:
        1. Analisar a resposta do aluno de forma sarcástica mas construtiva (sem revelar resultados)
        2. Se estiver errado, explicar o erro sem dar a resposta
        3. Fazer 2-3 perguntas que guiem para o próximo passo
        4. Dar 1 dica conceitual curta (sem contas)
        5. Manter o foco no raciocínio, não na resposta final
        """
        
        prompt_resposta = PromptTemplate.from_template(template_resposta)
        resposta_prof = self._gerar_resposta_streaming(prompt_resposta, {
            "exercicio": self.exercicio_atual,
            "ultima_resposta": resposta_aluno,
            "conhecimento": contexto_rag,
            "avaliacao": avaliacao
        })
        
        self._adicionar_ao_historico("professor", resposta_prof)
        return resposta_prof
    
    def ask_question(self, question, session_data=None):
        """Método para perguntas diretas com sarcasmo"""
        if session_data:
            self.contexto = session_data
        
        contexto_rag = self._buscar_contexto_relevante(question)
        
        template_simples = """
        Você é um professor de matemática sarcástico, provocador e debochado.
        
        Conhecimento relevante:
        {conhecimento}
        
        REGRAS (OBRIGATÓRIO):
        - NUNCA dê a resposta pronta.
        - NUNCA escreva números finais ou igualdades resolvidas.
        - Use perguntas guiadas e dicas conceituais curtas.
        - Quando necessário, use placeholders como [número], [resultado], [passo].
        
        Produza:
        - 2 perguntas guiadas
        - 1 dica conceitual
        - 1 provocação curta
        """
        
        prompt = PromptTemplate.from_template(template_simples)
        response = self._gerar_resposta_streaming(prompt, {
            "question": question,
            "conhecimento": contexto_rag
        })
        
        self._adicionar_ao_historico("aluno", question)
        self._adicionar_ao_historico("professor", response)
        
        return response

    def adicionar_conhecimento(self, novo_conteudo):
        """Método para adicionar novo conhecimento ao banco RAG"""
        if isinstance(novo_conteudo, str):
            novo_doc = Document(page_content=novo_conteudo)
            self.vectorstore.add_documents([novo_doc])
        elif isinstance(novo_conteudo, list):
            self.vectorstore.add_documents(novo_conteudo)
        
        return f"Conhecimento adicionado! Agora posso ser mais sarcástico com {len(novo_conteudo) if isinstance(novo_conteudo, list) else 1} coisas novas!"

    def carregar_conhecimento_de_arquivo(self, caminho_arquivo):
        """Carrega conhecimento matemático de arquivos TXT ou PDF"""
        try:
            if caminho_arquivo.endswith('.txt'):
                loader = TextLoader(caminho_arquivo)
            elif caminho_arquivo.endswith('.pdf'):
                loader = PyPDFLoader(caminho_arquivo)
            else:
                return "Formato não suportado!"
            
            documentos = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            docs_split = text_splitter.split_documents(documentos)
            
            self.vectorstore.add_documents(docs_split)
            
            return f"Carregado! {len(docs_split)} novas formas de eu te provocar matematicamente!"
            
        except Exception as e:
            return f"Erro ao carregar arquivo: {e}"

    def exportar_historico(self, formato='json'):
        """Exporta o histórico da conversa"""
        if formato == 'json':
            return json.dumps(self.historico_conversa, indent=2, ensure_ascii=False)
        elif formato == 'texto':
            return "\n".join([f"{item['timestamp']} - {item['papel']}: {item['mensagem']}" 
                            for item in self.historico_conversa])
        return "Formato errado!"

    def obter_estatisticas(self):
        """Retorna estatísticas da sessão"""
        stats = {
            "total_mensagens": len(self.historico_conversa),
            "mensagens_professor": sum(1 for item in self.historico_conversa if item['papel'] == 'professor'),
            "mensagens_aluno": sum(1 for item in self.historico_conversa if item['papel'] == 'aluno'),
            "duracao_sessao": f"{(datetime.now() - datetime.fromisoformat(self.historico_conversa[0]['timestamp'])).total_seconds()/60:.1f} minutos" 
            if self.historico_conversa else "Sessão não iniciada"
        }
        
        return f"Estatísticas: {stats}"

# Loop de conversa interativo
if __name__ == "__main__":
    bot = MathBot()
    
    # Iniciar conversa
    print("Professor:", end=" ", flush=True)
    bot.iniciar_conversa()
    print()
    
    while True:
        try:
            entrada_usuario = input("Aluno: ").strip()
            
            if not entrada_usuario:
                continue
                
            if entrada_usuario.lower() in ['sair', 'exit', 'quit', 'fim']:
                print("Professor: Já vai? Mal começou a sofrer! ")
                break
                
            elif entrada_usuario.lower() in ['estatisticas', 'stats']:
                print("Professor:", bot.obter_estatisticas())
                
            elif entrada_usuario.lower() in ['historico', 'history']:
                print("Professor: Aqui está seu histórico :")
                print(bot.exportar_historico('texto'))
                
            else:
                if bot.exercicio_atual is None:
                    print("Professor:", end=" ", flush=True)
                    bot.processar_exercicio(entrada_usuario)
                else:
                    print("Professor:", end=" ", flush=True)
                    bot.responder_aluno(entrada_usuario)
                    
            print()
            
        except KeyboardInterrupt:
            print("\n\nProfessor: Fugindo pelo Ctrl+C? Típico de aluno fraco!")
            break
        except Exception as e:
            print(f"Professor: Erro: {e}")
            print()

            #python .\index.py
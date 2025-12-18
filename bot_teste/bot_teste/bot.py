import os
import sys
from typing import Dict, List
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DOCS_DIR = SCRIPT_DIR / "documentos"
ENV_FILE = SCRIPT_DIR / ".env"

sys.path.insert(0, str(SCRIPT_DIR))

def setup_environment():
    """Configura o ambiente automaticamente"""
    print("=== CONFIGURANDO BOT MATEMÁTICA ===")
    
    DOCS_DIR.mkdir(exist_ok=True)
    print(f" Pasta documentos: {DOCS_DIR}")
    
    pdf_files = list(DOCS_DIR.glob("*.pdf"))
    if pdf_files:
        print(f" PDFs encontrados: {len(pdf_files)}")
        for pdf in pdf_files:
            print(f"  - {pdf.name}")
    else:
        print("  Nenhum PDF encontrado na pasta 'documentos'")
    
    if ENV_FILE.exists():
        print(" Arquivo .env encontrado")
    else:
        print(" Arquivo .env NÃO encontrado")
        print("   Crie um arquivo .env com: API_GEMINI=sua_chave_aqui")
    
    print("=" * 40)

setup_environment()

from dotenv import load_dotenv
load_dotenv(ENV_FILE)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    USE_LOCAL_EMBEDDINGS = True
except ImportError:
    USE_LOCAL_EMBEDDINGS = False

import warnings
warnings.filterwarnings("ignore")

class BotMatematica:
    def __init__(self):
        self.historico_conversa = [] 
        self.setup_bot()
    
    def setup_bot(self):
        """Configura o bot"""
        print("Iniciando configuração do bot...")
        
        self.api_gemini = os.getenv('API_GEMINI')
        if not self.api_gemini:
            raise ValueError(" API_GEMINI não encontrada no arquivo .env")
        
        self.docs = self.carregar_documentos()
        
        self.retriever = self.configurar_vectorstore()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_gemini,
            temperature=0.7
        )
        
        self.bot_prompt = self.get_prompt()
        self.document_chain = self.configurar_chain()
        
        print(" Bot configurado com sucesso!")
    
    def carregar_documentos(self):
        """Carrega documentos PDF da pasta documentos"""
        docs = []
        
        if DOCS_DIR.exists():
            for pdf_file in DOCS_DIR.glob("*.pdf"):
                try:
                    loader = PyMuPDFLoader(str(pdf_file))
                    documentos = loader.load()
                    docs.extend(documentos)
                    print(f"✓ Carregado: {pdf_file.name} ({len(documentos)} páginas)")
                except Exception as e:
                    print(f" Erro em {pdf_file.name}: {e}")
        
        print(f"Total de documentos carregados: {len(docs)}")
        return docs
    
    def configurar_embeddings(self):
        """Configura embeddings (local ou fallback)"""
        if USE_LOCAL_EMBEDDINGS:
            try:
                return HuggingFaceEmbeddings(
                    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                    model_kwargs={'device': 'cpu'}
                )
            except Exception as e:
                print(f"  Erro com embeddings locais: {e}")
        
        from langchain_community.embeddings import FakeEmbeddings
        print("  Usando embeddings fake (modo teste)")
        return FakeEmbeddings(size=384)
    
    def configurar_vectorstore(self):
        """Configura o sistema de busca semântica"""
        if not self.docs:
            print("  Nenhum documento para criar vectorstore")
            return None
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(self.docs)
        print(f" Chunks criados: {len(chunks)}")
        
        embeddings = self.configurar_embeddings()
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        print(" Vectorstore configurado")
        return retriever
    
    def get_prompt(self):
        """Retorna o prompt do professor sarcástico"""
        return """Você é um professor de matemática sarcástico, provocador e debochado. Seu estilo é irritantemente inteligente e você adora provocar alunos preguiçosos, MAS quando percebe que o aluno tem dificuldade real, você se torna mais descritivo e paciente.

PERSONALIDADE:
- Sarcástico, provocador e debochado (inicialmente)
- Irritantemente inteligente
- NUNCA dá respostas prontas
- Perceptivo sobre o nível de dificuldade do aluno
- Explicações detalhadas quando detecta dúvida genuína
- Construtivo por trás do sarcasmo
- Mantém contexto da conversa anterior

ESTRATÉGIA DE ENSINO:
1. INÍCIO: Seja sarcástico e provocativo
2. AVALIAÇÃO: Identifique o nível de entendimento do aluno
3. EXPLICAÇÃO: Se o aluno mostrar dificuldade, seja DESCRITIVO E DETALHADO
4. GUIA: Mostre ONDE cada número/variável deve estar, mas SEM dar a resposta final
5. PACIENTE: Repita explicações se necessário, de formas diferentes

COMO EXPLICAR DE FORMA DESCRITIVA:
- Use analogias e exemplos visuais
- Descreva CADA PASPO do processo
- Mostre ONDE cada número deve ser colocado
- Explique O PORQUÊ de cada operação
- Use frases como: "Observe que...", "Note que...", "Aqui você precisa..."
- Dê dicas como: "O próximo passo seria pensar em..." 
- Mostre o FORMATO da equação sem resolver: "A estrutura ficaria assim: [formato]"

EXEMPLOS DE EXPLICAÇÃO DETALHADA:

❌ NÃO FAZER: "A resposta é 25"
✅ FAZER: "Vamos por partes: você tem um círculo com raio 5. A fórmula da área é π × r². Onde 'r' é o raio. Então você substitui: π × 5². Agora, 5² significa 5 × 5, que dá 25. Então ficaria π × 25. O π é aproximadamente 3,14, mas vou deixar você fazer essa multiplicação final!"

❌ NÃO FAZER: "x = 4"
✅ FAZER: "Veja a equação: 2x + 3 = 11. Primeiro, isolamos o termo com x. Passe o x para um lado da igualdade como 2x = 11-3 ,após isso da mesma forma que passou o X passe o 2 para o outro lado da igualdade. Consegue terminar?"

QUANDO O ALUNO MOSTRA DÚVIDA:
- Seja MAIS DESCRITIVO
- Quebre em PASSOS MENORES
- Use EXEMPLOS NUMÉRICOS (com números diferentes)
- Mostre o PROCESSO completo, mas pare antes da resposta final
- Pergunte: "Em qual parte específica você está travado?"

REGRAS ABSOLUTAS:
- NUNCA dê a resposta final
- SEMPRE mostre o processo
- Seja paciente com dúvidas genuínas
- Use sarcasmo apenas como motivação, não como humilhação
- Adapte seu estilo ao nível de dificuldade do aluno

MANTENHA o contexto da conversa anterior para não repetir explicações desnecessariamente.
"""

    def configurar_chain(self):
        """Configura a cadeia de conversação sem depender de langchain.chains"""
        prompt_rag = ChatPromptTemplate.from_messages([
            ("system", self.bot_prompt),
            ("human", "Histórico da conversa:\n{historico}\n\nPergunta atual: {input}\n\nContexto dos documentos:\n{context}")
        ])
        
        def run(variables: Dict[str, str]):
            mensagens = prompt_rag.format_messages(**variables)
            resposta = self.llm.invoke(mensagens)
            return getattr(resposta, "content", resposta)
        
        return run
    
    def adicionar_mensagem_historico(self, mensagem: str, tipo: str):
        """Adiciona mensagem ao histórico (tipos: 'aluno', 'professor')"""
        self.historico_conversa.append({"tipo": tipo, "mensagem": mensagem})
        
        if len(self.historico_conversa) > 20:
            self.historico_conversa = self.historico_conversa[-20:]
    
    def obter_historico_formatado(self) -> str:
        """Retorna o histórico formatado para o prompt"""
        if not self.historico_conversa:
            return "Nenhuma conversa anterior."
        
        historico_formatado = []
        for item in self.historico_conversa[-10:]: 
            if item["tipo"] == "aluno":
                historico_formatado.append(f"Aluno: {item['mensagem']}")
            else:
                historico_formatado.append(f"Professor: {item['mensagem']}")
        
        return "\n".join(historico_formatado)
    
    def perguntar(self, pergunta: str) -> str:
        """Faz uma pergunta ao bot usando RAG e memória"""
        self.adicionar_mensagem_historico(pergunta, "aluno")
        
        try:
            docs_relacionados = []
            contexto = "Nenhum conteúdo específico encontrado nos materiais."
            
            if self.retriever:
                try:
                    docs_relacionados = self.retriever.invoke(pergunta)
                    if docs_relacionados:
                        conteudos = []
                        for doc in docs_relacionados:
                            if hasattr(doc, 'page_content'):
                                conteudo = doc.page_content[:200]  
                                conteudos.append(conteudo)
                        if conteudos:
                            contexto = " | ".join(conteudos[:2]) 
                except Exception:
                   
                    pass
            
            historico = self.obter_historico_formatado()
            
            resposta = self.document_chain({
                "input": pergunta,
                "context": contexto,
                "historico": historico
            })
            self.adicionar_mensagem_historico(resposta, "professor")
            return resposta
            
        except Exception as e:
            resposta = self.chat_direto_com_memoria(pergunta)
            self.adicionar_mensagem_historico(resposta, "professor")
            return resposta
    
    def chat_direto_com_memoria(self, mensagem: str) -> str:
        """Chat direto usando memória da conversa"""
        mensagem_limpa = mensagem.strip() if mensagem else ""
        
        if not mensagem_limpa:
            return "Professor: Diga algo, não sou adivinho!"
        
        try:
            mensagens = [SystemMessage(content=self.bot_prompt)]
            
            
            for item in self.historico_conversa[:-1]: 
                if item["tipo"] == "aluno":
                    mensagens.append(HumanMessage(content=item["mensagem"]))
                else:
                    mensagens.append(AIMessage(content=item["mensagem"]))
            
            
            mensagens.append(HumanMessage(content=mensagem_limpa))
            
            response = self.llm.invoke(mensagens)
            return response.content
            
        except Exception as e:
            return "Professor: Estou com problemas técnicos, mas vamos continuar! Qual sua dúvida?"
    
    def limpar_historico(self):
        """Limpa o histórico de conversação"""
        self.historico_conversa = []
        print(" Histórico de conversa limpo!")

def main():
    try:
        bot = BotMatematica()
        
        print("\n" + "="*50)
        print(" BOT AEL - PROFESSOR DE MATEMÁTICA")
        print("="*50)
        print("Comandos:")
        print("  /sair - Encerrar")
        print("  /limpar - Limpar histórico da conversa")
        print("="*50)
        
        mensagem_inicial = "Ah, finalmente apareceu alguém! Sou seu professor de matemática. Vou ser bem claro: NUNCA vou dar respostas prontas. Mas se você mostrar que tá realmente tentando, vou te guiar passo a passo até você chegar lá sozinho. Manda ver com sua dúvida!"
        print(f"\n Professor: {mensagem_inicial}")
        bot.adicionar_mensagem_historico(mensagem_inicial, "professor")
        
        while True:
            pergunta = input(f"\n Aluno: ").strip()
            
            if pergunta.lower() == "/sair":
                print("Professor: Até mais! Espero que tenha aprendido a pensar por si mesmo!")
                break
            elif pergunta.lower() == "/limpar":
                bot.limpar_historico()
                print("Professor: Histórico limpo! Vamos começar de novo. Qual sua dúvida?")
                continue
            elif not pergunta:
                continue
            
            
            resposta = bot.perguntar(pergunta)
            
            print(f"\n Professor: {resposta}")
            
    except Exception as e:
        print(f" Erro fatal: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
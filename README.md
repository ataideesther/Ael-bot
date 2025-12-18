# Ael-bot

Projeto de bot de Inteligência Artificial educacional, desenvolvido em Python, com foco no ensino de Matemática por meio de explicações guiadas, provocativas e adaptativas.

O bot atua como um professor virtual, utilizando IA generativa, busca semântica em documentos PDF (RAG) e memória de conversação, incentivando o aluno a pensar e resolver problemas sem receber respostas prontas.

# Objetivo do Projeto

Auxiliar estudantes no aprendizado de matemática de forma ativa

Estimular o raciocínio lógico em vez da simples entrega de respostas

Utilizar IA como ferramenta pedagógica de apoio ao estudo

# Funcionalidades Principais

Professor Virtual com Personalidade
Bot assume o papel de um professor sarcástico e provocador, mas paciente quando detecta dificuldades reais.

Ensino Guiado (Sem Respostas Prontas)
Explica o passo a passo do raciocínio, mostra o formato das equações e orienta o aluno até a solução final, sem resolvê-la diretamente.

Memória de Conversação
Mantém o contexto das últimas interações para evitar repetições e melhorar a continuidade do ensino.

RAG com Documentos PDF
Utiliza arquivos PDF adicionados à pasta documentos como base de conhecimento para contextualizar as respostas.

Busca Semântica
Emprega embeddings e FAISS para recuperar trechos relevantes dos materiais de estudo.

# Tecnologias Utilizadas

Python – Linguagem principal

LangChain – Orquestração do LLM e fluxo de conversa

Google Gemini (Generative AI) – Modelo de linguagem

FAISS – Banco vetorial para busca semântica

Sentence Transformers – Geração de embeddings

PyMuPDF – Leitura de arquivos PDF

python-dotenv – Gerenciamento de variáveis de ambiente

# Estrutura do Projeto

```
projeto/
├── bot.py # Código principal do bot
├── requirements.txt # Dependências do projeto
├── .env # Chave da API (não versionar)
└── documentos/ # PDFs usados como base de conhecimento
```
# Como Executar o Projeto

Instale as dependências listadas em requirements.txt

Crie um arquivo .env com sua chave da API do Google Gemini

Adicione PDFs de conteúdo matemático à pasta documentos

Execute o arquivo principal do bot

# Público-Alvo

Estudantes do Ensino Fundamental e Médio

Alunos que desejam aprender matemática de forma guiada

Professores interessados em soluções educacionais com IA

# Finalidade Educacional

Este projeto possui finalidade exclusivamente educacional, sem fins comerciais, sendo utilizado como experimento e apoio ao ensino de matemática com Inteligência Artificial.



#

#

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time
from .forms import MathQuestionForm
from .math_bot_core import MathBot
from django.views.decorators.http import require_http_methods

# Dicionário para armazenar sessões
sessoes_ativas = {}

def index(request):
    return render(request, 'math_bot/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def iniciar_conversa(request):
    try:
        data = json.loads(request.body)
        topico = data.get('topico', '').strip()
        nivel = data.get('nivel', '').strip()
        conhecimento_previo = data.get('conhecimento_previo', '').strip()
        
        if not topico or not nivel or not conhecimento_previo:
            return JsonResponse({
                'success': False,
                'error': 'Todos os campos são obrigatórios'
            })
        
        # Criar session ID único com timestamp
        session_id = f"session_{hash(f'{topico}{nivel}{conhecimento_previo}{time.time()}')}"
        
        bot = MathBot()
        resposta_inicial = bot.iniciar_conversa(topico, nivel, conhecimento_previo)
        
        # Salvar sessão
        sessoes_ativas[session_id] = {
            'bot': bot,
            'contexto': bot.contexto,
            'timestamp': time.time()
        }
        
        # Limpar sessões antigas (mais de 1 hora)
        limpar_sessoes_antigas()
        
        return JsonResponse({
            'success': True,
            'resposta': resposta_inicial,
            'session_id': session_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def continuar_conversa(request):
    try:
        data = json.loads(request.body)
        resposta_aluno = data.get('resposta_aluno', '').strip()
        session_id = data.get('session_id', '').strip()
        
        if not resposta_aluno:
            return JsonResponse({
                'success': False,
                'error': 'Resposta não pode estar vazia'
            })
        
        if not session_id or session_id not in sessoes_ativas:
            return JsonResponse({
                'success': False,
                'error': 'Sessão não encontrada ou expirada'
            })
        
        session_data = sessoes_ativas[session_id]
        bot = session_data['bot']
        
        resposta_prof = bot.responder_aluno(resposta_aluno)
        
        # Atualizar sessão
        sessoes_ativas[session_id]['contexto'] = bot.contexto
        sessoes_ativas[session_id]['timestamp'] = time.time()
        
        return JsonResponse({
            'success': True,
            'resposta': resposta_prof
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def ask_question(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        session_id = data.get('session_id', '').strip()
        
        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Pergunta não pode estar vazia'
            })
        
        bot = MathBot()
        
        # Se tem session_id válida, recupera o contexto
        session_data = None
        if session_id and session_id in sessoes_ativas:
            session_data = sessoes_ativas[session_id]['contexto']
        
        response = bot.ask_question(question, session_data)
        
        return JsonResponse({
            'success': True,
            'response': response,
            'question': question
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

def limpar_sessoes_antigas():
    """Remove sessões com mais de 1 hora"""
    current_time = time.time()
    keys_to_remove = []
    
    for session_id, session_data in sessoes_ativas.items():
        if current_time - session_data['timestamp'] > 3600:  # 1 hora
            keys_to_remove.append(session_id)
    
    for key in keys_to_remove:
        del sessoes_ativas[key]

# CORREÇÃO: A função debug_sessoes deve estar FORA da função limpar_sessoes_antigas
@csrf_exempt
def debug_sessoes(request):
    """Endpoint simples para debug"""
    if request.method == 'GET':
        return JsonResponse({
            'total_sessoes_ativas': len(sessoes_ativas),
            'sessoes_ids': list(sessoes_ativas.keys()),
            'status': 'OK'
        })
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
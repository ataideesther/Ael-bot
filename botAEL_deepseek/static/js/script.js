document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const submitBtn = document.getElementById('submit-btn');
    const loadingSpinner = document.getElementById('loading-spinner');
    const startButton = document.getElementById('start-chat');
    const inicioModal = new bootstrap.Modal(document.getElementById('inicioModal'));
    let sessionId = null;
    let isConversationStarted = false;
    let typingIndicator = null;

    // Mostrar modal de início
    inicioModal.show();

    // Iniciar conversa
    startButton.addEventListener('click', function() {
        const topico = document.getElementById('topico').value;
        const nivel = document.getElementById('nivel').value;
        const conhecimento = document.getElementById('conhecimento_previo').value;

        if (!topico || !nivel || !conhecimento) {
            alert('Por favor, preencha todos os campos!');
            return;
        }

        iniciarConversa(topico, nivel, conhecimento);
        inicioModal.hide();
    });

    // Enviar mensagem
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Adicionar mensagem do usuário ao chat
        addMessage(message, 'user');
        userInput.value = '';

        // Mostrar loading no botão
        showLoading();

        try {
            let response;
            let url;
            let body;

            if (!isConversationStarted) {
                // Primeira mensagem - iniciar conversa
                url = '/iniciar/';
                body = JSON.stringify({
                    topico: message,
                    nivel: 'Ensino Médio',
                    conhecimento_previo: 'Pouco conhecimento'
                });
            } else {
                // Continuar conversa
                url = '/continuar/';
                body = JSON.stringify({
                    resposta_aluno: message,
                    session_id: sessionId
                });
            }

            response = await fetchWithTimeout(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: body
            }, 120000);

            const data = await response.json();

            if (data.success) {
                if (data.session_id) {
                    sessionId = data.session_id;
                    isConversationStarted = true;
                }
                addMessage(data.resposta || data.response, 'bot');
            } else {
                addMessage('❌ Erro: ' + data.error, 'bot');
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                addMessage('⏳ O servidor demorou para responder (timeout). Tente novamente, aguarde mais um pouco ou aumente o tempo limite.', 'bot');
            } else {
                addMessage('❌ Erro de conexão com o servidor', 'bot');
            }
            console.error('Erro:', error);
        } finally {
            hideLoading();
            userInput.focus();
            scrollToBottom();
        }
    });

    // Mostrar loading
    function showLoading() {
        loadingSpinner.classList.remove('d-none');
        submitBtn.disabled = true;
        userInput.disabled = true;
        
        // Mostrar indicador de digitação
        showTypingIndicator();
    }

    // Esconder loading
    function hideLoading() {
        loadingSpinner.classList.add('d-none');
        submitBtn.disabled = false;
        userInput.disabled = false;
        
        // Remover indicador de digitação
        hideTypingIndicator();
    }

    // Mostrar indicador de digitação
    function showTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.remove();
        }
        
        typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot-message mb-3';
        typingIndicator.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="avatar me-3">🤖</div>
                <div class="message-content">
                    <div class="alert alert-info typing-alert">
                        <strong>Professor:</strong> 
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingIndicator);
        scrollToBottom();
    }

    // Esconder indicador de digitação
    function hideTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.remove();
            typingIndicator = null;
        }
    }

    // Função para iniciar conversa
    async function iniciarConversa(topico, nivel, conhecimento) {
        try {
            showLoading();
            
            const response = await fetchWithTimeout('/iniciar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    topico: topico,
                    nivel: nivel,
                    conhecimento_previo: conhecimento
                })
            }, 120000);

            const data = await response.json();

            if (data.success) {
                sessionId = data.session_id;
                isConversationStarted = true;
                addMessage(data.resposta, 'bot');
            } else {
                addMessage('❌ Erro ao iniciar conversa: ' + data.error, 'bot');
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                addMessage('⏳ O servidor demorou para responder (timeout). Tente novamente, aguarde mais um pouco ou aumente o tempo limite.', 'bot');
            } else {
                addMessage('❌ Erro de conexão', 'bot');
            }
        } finally {
            hideLoading();
            scrollToBottom();
        }
    }

    // Adicionar mensagem ao chat
    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = type === 'bot' ? '🤖' : '👤';
        const bgClass = type === 'bot' ? 'alert-info' : 'alert-primary';
        
        messageDiv.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="avatar me-3">${avatar}</div>
                <div class="message-content">
                    <div class="alert ${bgClass}">
                        <strong>${type === 'bot' ? 'Professor' : 'Você'}:</strong> 
                        ${formatMessage(text)}
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // Formatar mensagem
    function formatMessage(text) {
        return text.replace(/\n/g, '<br>');
    }

    // Rolagem automática
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Função auxiliar para pegar CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Focar no input quando modal fechar
    document.getElementById('inicioModal').addEventListener('hidden.bs.modal', function() {
        userInput.focus();
    });
});

// Função com timeout para evitar requisições muito longas
async function fetchWithTimeout(url, options, timeout = 120000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        throw error;
    }
}
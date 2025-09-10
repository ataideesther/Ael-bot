document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const userInput = document.getElementById('user-input');
    const submitBtn = document.getElementById('submit-btn');
    const chatInput = document.getElementById('chat-input');
    const chatSubmitBtn = document.getElementById('chat-submit-btn');
    const chatContainer = document.getElementById('chat-container');
    const chatMessages = document.getElementById('chat-messages');
    let sessionId = null;
    let isConversationStarted = false;
    let typingIndicator = null;

    // Focar no input quando a página carregar
    userInput.focus();

    // Função para obter o input ativo
    function getActiveInput() {
        return chatContainer.style.display === 'flex' ? chatInput : userInput;
    }

    // Função para obter o botão ativo
    function getActiveButton() {
        return chatContainer.style.display === 'flex' ? chatSubmitBtn : submitBtn;
    }

    // Função para mostrar o chat
    function showChat() {
        chatContainer.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        // Esconder o input inicial
        document.querySelector('.container').style.display = 'none';
        // Focar no input do chat
        setTimeout(() => chatInput.focus(), 100);
    }

    // Função para esconder o chat
    function hideChat() {
        chatContainer.style.display = 'none';
        document.body.style.overflow = 'auto';
        // Mostrar o input inicial novamente
        document.querySelector('.container').style.display = 'flex';
        userInput.focus();
    }

    // Função para enviar mensagem
    async function handleSubmit() {
        const activeInput = getActiveInput();
        const activeButton = getActiveButton();
        const message = activeInput.value.trim();
        console.log('handleSubmit chamado, mensagem:', message);
        console.log('isConversationStarted:', isConversationStarted);
        
        if (!message) {
            activeInput.focus();
            return;
        }

        // Mostrar chat se ainda não estiver visível
        if (chatContainer.style.display === 'none') {
            showChat();
        }

        // Adicionar mensagem do usuário
        addMessage(message, 'user');
        activeInput.value = '';

        // Mostrar indicador de digitação
        showTypingIndicator();

        // Desabilitar input e botão
        activeInput.disabled = true;
        activeButton.disabled = true;

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
            hideTypingIndicator();
            const activeInput = getActiveInput();
            const activeButton = getActiveButton();
            activeInput.disabled = false;
            activeButton.disabled = false;
            console.log('Input reabilitado, isConversationStarted:', isConversationStarted);
            activeInput.focus();
            scrollToBottom();
        }
    }

    // Mostrar indicador de digitação
    function showTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.remove();
        }
        
        typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot-message';
        typingIndicator.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="typing-indicator">
                <strong>Professor:</strong> 
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
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

    // Adicionar mensagem ao chat
    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = type === 'bot' ? '🤖' : '👤';
        
        messageDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="message-content">
                <strong>${type === 'bot' ? 'Professor' : 'Você'}:</strong> 
                ${formatMessage(text)}
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

    // Event listeners para o input inicial
    submitBtn.addEventListener('click', handleSubmit);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSubmit();
        }
    });

    userInput.addEventListener('click', function() {
        console.log('Input inicial clicado');
        this.focus();
    });

    // Event listeners para o input do chat
    chatSubmitBtn.addEventListener('click', handleSubmit);
    
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSubmit();
        }
    });

    chatInput.addEventListener('click', function() {
        console.log('Input do chat clicado');
        this.focus();
    });

    // Fechar chat com tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && chatContainer.style.display === 'flex') {
            hideChat();
            userInput.focus();
        }
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

// FinGuard Chat Bot JavaScript
class FinGuardChat {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.messageHistory = [];
        this.ollmaStatus = null;
        
        this.init();
        this.checkOllamaHealth();
    }
    
    init() {
        this.createChatElements();
        this.bindEvents();
        this.loadSuggestions();
    }
    
    createChatElements() {
        // Create floating button
        const floatButton = document.createElement('button');
        floatButton.className = 'chat-float-button';
        floatButton.innerHTML = '<i class="fas fa-robot"></i>';
        floatButton.id = 'chatFloatButton';
        
        // Create chat popup
        const chatPopup = document.createElement('div');
        chatPopup.className = 'chat-popup';
        chatPopup.id = 'chatPopup';
        chatPopup.innerHTML = `
            <div class="chat-header">
                <div class="chat-header-info">
                    <h4><i class="fas fa-robot"></i> FinGuard Assistant</h4>
                    <div class="status">
                        <span class="status-indicator loading"></span>
                        <span id="chatStatus">Connecting...</span>
                    </div>
                </div>
                <button class="chat-close" id="chatClose">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="chat-welcome">
                    <h5>🤖 Hello! I'm your FinGuard Assistant</h5>
                    <p>I'm here to help you with budgeting, expense tracking, and financial planning. How can I assist you today?</p>
                    <div class="chat-suggestions" id="chatSuggestions"></div>
                </div>
            </div>
            <div class="chat-input-area">
                <div class="chat-input-wrapper">
                    <textarea 
                        class="chat-input" 
                        id="chatInput" 
                        placeholder="Ask me about budgeting, expenses, or FinGuard features..."
                        rows="1"
                    ></textarea>
                    <button class="chat-send-btn" id="chatSendBtn">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(floatButton);
        document.body.appendChild(chatPopup);
        
        // Store references
        this.floatButton = floatButton;
        this.chatPopup = chatPopup;
        this.messagesContainer = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('chatSendBtn');
        this.statusIndicator = document.querySelector('.status-indicator');
        this.statusText = document.getElementById('chatStatus');
    }
    
    bindEvents() {
        // Float button click
        this.floatButton.addEventListener('click', () => {
            this.toggleChat();
        });
        
        // Close button click
        document.getElementById('chatClose').addEventListener('click', () => {
            this.closeChat();
        });
        
        // Send button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enter key to send message
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (this.isOpen && 
                !this.chatPopup.contains(e.target) && 
                !this.floatButton.contains(e.target)) {
                this.closeChat();
            }
        });
    }
    
    async checkOllamaHealth() {
        try {
            const response = await fetch('/api/chat/health');
            const data = await response.json();
            
            this.ollmaStatus = data;
            this.updateStatus(data);
        } catch (error) {
            console.error('Failed to check Ollama health:', error);
            this.updateStatus({
                ollama_available: false,
                model_available: false,
                status: 'connection_error'
            });
        }
    }
    
    updateStatus(status) {
        const indicator = this.statusIndicator;
        const text = this.statusText;
        
        if (status.ollama_available && status.model_available) {
            indicator.className = 'status-indicator online';
            text.textContent = 'Online';
        } else if (status.ollama_available && !status.model_available) {
            indicator.className = 'status-indicator offline';
            text.textContent = 'Model not found';
        } else {
            indicator.className = 'status-indicator offline';
            text.textContent = 'Offline';
        }
    }
    
    async loadSuggestions() {
        try {
            const response = await fetch('/api/chat/suggestions');
            const data = await response.json();
            
            if (data.success) {
                const suggestionsContainer = document.getElementById('chatSuggestions');
                suggestionsContainer.innerHTML = '';
                
                // Show first 4 suggestions
                data.suggestions.slice(0, 4).forEach(suggestion => {
                    const chip = document.createElement('div');
                    chip.className = 'suggestion-chip';
                    chip.textContent = suggestion;
                    chip.addEventListener('click', () => {
                        this.chatInput.value = suggestion;
                        this.sendMessage();
                    });
                    suggestionsContainer.appendChild(chip);
                });
            }
        } catch (error) {
            console.error('Failed to load suggestions:', error);
        }
    }
    
    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }
    
    openChat() {
        this.isOpen = true;
        this.chatPopup.classList.add('active');
        this.floatButton.classList.add('active');
        this.floatButton.innerHTML = '<i class="fas fa-times"></i>';
        
        // Focus input
        setTimeout(() => {
            this.chatInput.focus();
        }, 300);
    }
    
    closeChat() {
        this.isOpen = false;
        this.chatPopup.classList.remove('active');
        this.floatButton.classList.remove('active');
        this.floatButton.innerHTML = '<i class="fas fa-robot"></i>';
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Add user message
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        this.autoResizeTextarea();
        
        // Show typing indicator
        this.showTyping();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            this.hideTyping();
            
            if (data.success) {
                this.addMessage(data.response, 'bot');
            } else {
                // Handle different error types
                let errorMessage = data.fallback_response || 
                    'Sorry, I encountered an error. Please try again.';
                
                if (data.error && data.error.includes('connect')) {
                    errorMessage = 'I\'m currently offline. Please make sure the AI service is running and try again.';
                }
                
                this.addMessage(errorMessage, 'bot');
                this.showError(data.error);
            }
        } catch (error) {
            this.hideTyping();
            console.error('Chat error:', error);
            this.addMessage('Sorry, I\'m having trouble connecting. Please try again later.', 'bot');
            this.showError('Network error occurred');
        }
    }
    
    addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        // Format message for better display
        const formattedMessage = this.formatMessage(message);
        messageDiv.innerHTML = formattedMessage;
        
        // Remove welcome message if this is the first real message
        const welcome = this.messagesContainer.querySelector('.chat-welcome');
        if (welcome && this.messageHistory.length === 0) {
            welcome.style.display = 'none';
        }
        
        this.messagesContainer.appendChild(messageDiv);
        this.messageHistory.push({ message, sender, timestamp: new Date() });
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    formatMessage(message) {
        // Simple markdown-like formatting
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }
    
    showTyping() {
        this.isTyping = true;
        this.sendButton.disabled = true;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message typing';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <span>FinGuard Assistant is typing</span>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTyping() {
        this.isTyping = false;
        this.sendButton.disabled = false;
        
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    showError(error) {
        // Remove any existing errors
        const existingError = this.messagesContainer.querySelector('.chat-error');
        if (existingError) {
            existingError.remove();
        }
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-error';
        errorDiv.textContent = `Error: ${error}`;
        
        this.messagesContainer.appendChild(errorDiv);
        this.scrollToBottom();
        
        // Auto-remove error after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    autoResizeTextarea() {
        const textarea = this.chatInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 80) + 'px';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
    
    // Public methods for external use
    sendQuickMessage(message) {
        this.chatInput.value = message;
        if (!this.isOpen) {
            this.openChat();
        }
        setTimeout(() => {
            this.sendMessage();
        }, 300);
    }
    
    clearHistory() {
        this.messageHistory = [];
        this.messagesContainer.innerHTML = '';
        this.messagesContainer.appendChild(document.querySelector('.chat-welcome'));
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in before initializing chat
    if (document.querySelector('body').getAttribute('data-user-logged-in') !== 'false') {
        window.finGuardChat = new FinGuardChat();
    }
});

// Add some utility functions for other parts of the app to interact with chat
window.FinGuardChatUtils = {
    sendMessage: function(message) {
        if (window.finGuardChat) {
            window.finGuardChat.sendQuickMessage(message);
        }
    },
    
    openChat: function() {
        if (window.finGuardChat) {
            window.finGuardChat.openChat();
        }
    },
    
    closeChat: function() {
        if (window.finGuardChat) {
            window.finGuardChat.closeChat();
        }
    }
};

class RobotFrameworkAssistant {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.pendingAction = null;
        
        this.initializeElements();
        this.attachEventListeners();
        this.connectWebSocket();
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.confirmationModal = document.getElementById('confirmationModal');
        this.confirmationMessage = document.getElementById('confirmationMessage');
        this.confirmYes = document.getElementById('confirmYes');
        this.confirmNo = document.getElementById('confirmNo');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        
        // Modal close buttons
        this.modalCloses = document.querySelectorAll('.modal-close');
    }
    
    attachEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key to send message
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
            this.toggleSendButton();
        });
        
        // Confirmation modal buttons
        this.confirmYes.addEventListener('click', () => this.confirmAction());
        this.confirmNo.addEventListener('click', () => this.cancelAction());
        
        // Close modal events
        this.modalCloses.forEach(close => {
            close.addEventListener('click', () => this.closeModal());
        });
        
        // Close modal on outside click
        this.confirmationModal.addEventListener('click', (e) => {
            if (e.target === this.confirmationModal) {
                this.closeModal();
            }
        });
        
        // Initial send button state
        this.toggleSendButton();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus(true);
            console.log('WebSocket connected');
        };
        
        this.socket.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus(false);
            console.log('WebSocket disconnected');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                if (!this.isConnected) {
                    this.connectWebSocket();
                }
            }, 3000);
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.addMessage('Connection error. Please refresh the page.', 'error');
        };
        
        this.socket.onmessage = (event) => {
            this.handleMessage(JSON.parse(event.data));
        };
    }
    
    updateConnectionStatus(connected) {
        if (connected) {
            this.connectionStatus.className = 'status-connected';
            this.connectionStatus.innerHTML = '<i class="fas fa-circle"></i> Connected';
        } else {
            this.connectionStatus.className = 'status-disconnected';
            this.connectionStatus.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
        }
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        this.autoResizeTextarea();
        this.toggleSendButton();
        
        // Show loading indicator
        this.showLoading();
        
        // Send to server
        this.socket.send(JSON.stringify({ message }));
    }
    
    handleMessage(data) {
        this.hideLoading();
        
        const { message, type, requires_confirmation, suggested_action } = data;
        
        if (type === 'error') {
            this.addMessage(message, 'error');
        } else {
            this.addMessage(message, 'assistant');
            
            if (requires_confirmation && suggested_action) {
                this.pendingAction = suggested_action;
                this.showConfirmationModal(message);
            }
        }
    }
    
    addMessage(text, type) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        if (type === 'user') {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        } else if (type === 'error') {
            avatar.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        } else {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        }
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        
        if (type === 'error') {
            messageText.className += ' error-message';
        }
        
        // Process message text (convert markdown-like formatting)
        messageText.innerHTML = this.formatMessage(text);
        
        content.appendChild(messageText);
        messageElement.appendChild(avatar);
        messageElement.appendChild(content);
        
        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Convert markdown-like formatting to HTML
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
            .replace(/`(.*?)`/g, '<code>$1</code>') // Inline code
            .replace(/\n/g, '<br>'); // Line breaks
        
        // Handle code blocks
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Handle lists
        formatted = formatted.replace(/^- (.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        return formatted;
    }
    
    showConfirmationModal(message) {
        this.confirmationMessage.innerHTML = `
            <div class="confirmation-content">
                ${this.formatMessage(message)}
            </div>
        `;
        this.confirmationModal.classList.add('show');
    }
    
    closeModal() {
        this.confirmationModal.classList.remove('show');
        this.pendingAction = null;
    }
    
    confirmAction() {
        if (this.pendingAction) {
            this.closeModal();
            this.showLoading();
            
            // Send confirmation message
            this.addMessage('Yes, proceed', 'user');
            this.socket.send(JSON.stringify({ 
                message: 'yes',
                action: this.pendingAction
            }));
        }
    }
    
    cancelAction() {
        if (this.pendingAction) {
            this.closeModal();
            this.addMessage('Cancel', 'user');
            this.socket.send(JSON.stringify({ message: 'no' }));
        }
    }
    
    showLoading() {
        this.loadingIndicator.classList.add('show');
    }
    
    hideLoading() {
        this.loadingIndicator.classList.remove('show');
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        const scrollHeight = this.messageInput.scrollHeight;
        const maxHeight = 120; // Max height in pixels
        
        if (scrollHeight <= maxHeight) {
            this.messageInput.style.height = scrollHeight + 'px';
        } else {
            this.messageInput.style.height = maxHeight + 'px';
        }
    }
    
    toggleSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || !this.isConnected;
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// Sample interactions for demo
class DemoMode {
    constructor(assistant) {
        this.assistant = assistant;
        this.setupDemoCommands();
    }
    
    setupDemoCommands() {
        // Add demo button (optional)
        const demoButton = document.createElement('button');
        demoButton.textContent = 'Demo Commands';
        demoButton.className = 'btn btn-secondary';
        demoButton.style.position = 'fixed';
        demoButton.style.top = '10px';
        demoButton.style.right = '10px';
        demoButton.style.zIndex = '1000';
        demoButton.style.fontSize = '0.75rem';
        demoButton.style.padding = '0.5rem';
        
        demoButton.addEventListener('click', () => {
            this.showDemoCommands();
        });
        
        // Uncomment to add demo button
        // document.body.appendChild(demoButton);
    }
    
    showDemoCommands() {
        const commands = [
            "Create an e-commerce automation project",
            "Add a login test case",
            "Create keywords resource file",
            "Add variables for API testing",
            "Create a user registration test"
        ];
        
        const commandList = commands.map(cmd => 
            `<button class="demo-command" data-command="${cmd}">${cmd}</button>`
        ).join('');
        
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Demo Commands</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Click any command to try it:</p>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        ${commandList}
                    </div>
                </div>
            </div>
        `;
        
        // Add styles for demo commands
        const style = document.createElement('style');
        style.textContent = `
            .demo-command {
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 0.75rem;
                text-align: left;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .demo-command:hover {
                background: #e5e7eb;
                border-color: #667eea;
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(modal);
        
        // Add event listeners
        modal.querySelector('.modal-close').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
        modal.querySelectorAll('.demo-command').forEach(btn => {
            btn.addEventListener('click', () => {
                const command = btn.dataset.command;
                this.assistant.messageInput.value = command;
                this.assistant.autoResizeTextarea();
                this.assistant.toggleSendButton();
                document.body.removeChild(modal);
            });
        });
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    const assistant = new RobotFrameworkAssistant();
    const demo = new DemoMode(assistant);
    
    // Add some helpful keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            assistant.messageInput.focus();
        }
        
        // Escape to close modal
        if (e.key === 'Escape') {
            assistant.closeModal();
        }
    });
    
    // Show connection status on page load
    if (!assistant.isConnected) {
        setTimeout(() => {
            if (!assistant.isConnected) {
                assistant.addMessage(
                    'Having trouble connecting to the server. Please check your connection and refresh the page.',
                    'error'
                );
            }
        }, 5000);
    }
}); 
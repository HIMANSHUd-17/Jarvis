/**
 * UI Controller for JARVIS Frontend
 * Manages animations, state visualization, and user interactions
 */

class UIController {
    constructor() {
        this.client = null;
        this.currentState = 'Idle';
        this.isListening = false;
        
        // DOM Elements
        this.statusLight = document.getElementById('statusLight');
        this.statusText = document.getElementById('statusText');
        this.audioWave = document.getElementById('audioWave');
        this.chatMessages = document.getElementById('chatMessages');
        this.inputText = document.getElementById('inputText');
        this.listenBtn = document.getElementById('listenBtn');
        this.sendBtn = document.getElementById('sendBtn');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.actionButtons = document.querySelectorAll('.action-btn');
        
        this.init();
    }

    /**
     * Initialize the UI controller
     */
    init() {
        console.log('Initializing JARVIS UI...');
        
        // Initialize WebSocket client
        this.client = new JarvisWebSocketClient('localhost', 8765);
        
        // Set up callbacks
        this.client.onStateChange = (state) => this.handleStateUpdate(state);
        this.client.onResponse = (response) => this.handleResponse(response);
        this.client.onConnectionChange = (isConnected) => this.handleConnectionChange(isConnected);
        this.client.onError = (error) => this.handleError(error);
        
        // Connect to server
        this.client.connect();
        
        // Set up event listeners
        this.setupEventListeners();
    }

    /**
     * Set up all event listeners
     */
    setupEventListeners() {
        // Listen button
        this.listenBtn.addEventListener('click', () => this.toggleListening());
        
        // Send button
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Input field - Enter key to send
        this.inputText.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Quick action buttons
        this.actionButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.getAttribute('data-action');
                this.handleQuickAction(action);
            });
        });
    }

    /**
     * Toggle listening state
     */
    toggleListening() {
        if (this.isListening) {
            this.client.stopListening();
            this.isListening = false;
        } else {
            this.client.startListening();
            this.isListening = true;
        }
        this.updateListenButton();
    }

    /**
     * Send text message to backend
     */
    sendMessage() {
        const message = this.inputText.value.trim();
        
        if (!message) {
            console.warn('Empty message');
            return;
        }
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Send to backend
        this.client.sendText(message);
        
        // Clear input
        this.inputText.value = '';
    }

    /**
     * Handle quick action button click
     */
    handleQuickAction(action) {
        console.log(`Quick action: ${action}`);
        
        switch(action) {
            case 'chrome':
            case 'notepad':
            case 'calculator':
                this.client.executeCommand(action);
                this.addMessage(`Opening ${action}...`, 'assistant');
                break;
            case 'whatsapp':
                this.showWhatsAppDialog();
                break;
            default:
                console.warn(`Unknown action: ${action}`);
        }
    }

    /**
     * Show WhatsApp message dialog
     */
    showWhatsAppDialog() {
        const contact = prompt('Enter contact name:');
        if (!contact) return;
        
        const message = prompt('Enter message:');
        if (!message) return;
        
        this.client.sendWhatsAppMessage(contact, message);
        this.addMessage(`Sending WhatsApp to ${contact}...`, 'assistant');
    }

    /**
     * Handle state update from backend
     */
    handleStateUpdate(state) {
        console.log('State update:', state);
        
        this.currentState = state.state;
        this.updateStateIndicator();
        
        if (state.context) {
            console.log('Context:', state.context);
        }
    }

    /**
     * Handle response from backend
     */
    handleResponse(response) {
        console.log('Response from backend:', response);
        
        if (response.type === 'command_result') {
            const success = response.result.success;
            const message = response.result.message || response.result.error;
            this.addMessage(message, 'assistant', success ? 'success' : 'error');
        } else if (response.response) {
            this.addMessage(response.response, 'assistant');
        }
    }

    /**
     * Update state indicator UI
     */
    updateStateIndicator() {
        const stateMap = {
            'Idle': 'idle',
            'Listening': 'listening',
            'Processing': 'processing',
            'Speaking': 'speaking',
            'Error': 'error'
        };
        
        const stateClass = stateMap[this.currentState] || 'idle';
        
        // Update status light
        this.statusLight.className = `status-light ${stateClass}`;
        
        // Update status text
        this.statusText.textContent = this.currentState;
        
        // Update audio wave animation
        this.updateAudioWave();
    }

    /**
     * Update audio wave based on state
     */
    updateAudioWave() {
        const stateAnimations = {
            'Idle': 'idle',
            'Listening': 'listening',
            'Processing': 'processing',
            'Speaking': 'speaking'
        };
        
        const animation = stateAnimations[this.currentState] || 'idle';
        
        this.audioWave.className = `audio-wave ${animation}`;
    }

    /**
     * Update listen button appearance
     */
    updateListenButton() {
        if (this.isListening) {
            this.listenBtn.style.background = 'linear-gradient(135deg, #00d4ff, #0066cc)';
            this.listenBtn.innerHTML = '<span class="btn-icon">🎤</span><span class="btn-text">Stop Listening</span>';
        } else {
            this.listenBtn.style.background = 'linear-gradient(135deg, #00d4ff, #0066cc)';
            this.listenBtn.innerHTML = '<span class="btn-icon">🎤</span><span class="btn-text">Start Listening</span>';
        }
    }

    /**
     * Add message to chat
     */
    addMessage(text, sender = 'assistant', type = 'normal') {
        // Remove welcome message on first interaction
        const welcomeMsg = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender} ${type}`;
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div>${this.escapeHtml(text)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        
        // Auto-scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Handle connection status change
     */
    handleConnectionChange(isConnected) {
        if (isConnected) {
            this.connectionStatus.textContent = '🟢 Connected';
            this.connectionStatus.className = 'connection-status connected';
            this.listenBtn.disabled = false;
            this.sendBtn.disabled = false;
            console.log('Connected to JARVIS backend');
        } else {
            this.connectionStatus.textContent = '🔴 Disconnected';
            this.connectionStatus.className = 'connection-status disconnected';
            this.listenBtn.disabled = true;
            this.sendBtn.disabled = true;
            this.isListening = false;
            this.updateListenButton();
            console.log('Disconnected from JARVIS backend');
        }
    }

    /**
     * Handle error
     */
    handleError(error) {
        console.error('Error:', error);
        this.addMessage(`Error: ${error.message}`, 'assistant', 'error');
    }
}

// Initialize UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.uiController = new UIController();
});

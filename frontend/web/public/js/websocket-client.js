/**
 * WebSocket Client for JARVIS Frontend
 * Handles real-time communication with backend
 */

class JarvisWebSocketClient {
    constructor(host = 'localhost', port = 8765) {
        this.host = host;
        this.port = port;
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        
        // Callbacks
        this.onStateChange = null;
        this.onResponse = null;
        this.onMessage = null;
        this.onConnectionChange = null;
        this.onError = null;
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        try {
            const url = `ws://${this.host}:${this.port}`;
            console.log(`Connecting to ${url}...`);
            
            this.ws = new WebSocket(url);
            
            this.ws.onopen = () => this.handleOpen();
            this.ws.onmessage = (event) => this.handleMessage(event);
            this.ws.onclose = () => this.handleClose();
            this.ws.onerror = (error) => this.handleError(error);
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Handle WebSocket open event
     */
    handleOpen() {
        console.log('WebSocket connected successfully');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        // Notify UI of connection
        if (this.onConnectionChange) {
            this.onConnectionChange(true);
        }
        
        // Request current state
        this.send({
            command: 'get_state'
        });
    }

    /**
     * Handle incoming WebSocket message
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'state_update') {
                if (this.onStateChange) {
                    this.onStateChange(data.data);
                }
            } else if (data.type === 'response') {
                if (this.onResponse) {
                    this.onResponse(data.data);
                }
            }
            
            if (this.onMessage) {
                this.onMessage(data);
            }
        } catch (error) {
            console.error('Error processing message:', error);
        }
    }

    /**
     * Handle WebSocket close event
     */
    handleClose() {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        
        // Notify UI of disconnection
        if (this.onConnectionChange) {
            this.onConnectionChange(false);
        }
        
        // Attempt to reconnect
        this.scheduleReconnect();
    }

    /**
     * Handle WebSocket error
     */
    handleError(error) {
        console.error('WebSocket error:', error);
        if (this.onError) {
            this.onError(error);
        }
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectDelay}ms`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
            if (this.onError) {
                this.onError(new Error('Failed to connect to server after multiple attempts'));
            }
        }
    }

    /**
     * Send message to server
     */
    send(data) {
        if (!this.isConnected) {
            console.warn('WebSocket not connected. Message not sent.');
            return false;
        }
        
        try {
            this.ws.send(JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Error sending message:', error);
            return false;
        }
    }

    /**
     * Start listening for audio
     */
    startListening() {
        return this.send({
            command: 'start_listening'
        });
    }

    /**
     * Stop listening for audio
     */
    stopListening() {
        return this.send({
            command: 'stop_listening'
        });
    }

    /**
     * Send text input to backend
     */
    sendText(input) {
        return this.send({
            command: 'send_text',
            input: input
        });
    }

    /**
     * Execute system command
     */
    executeCommand(commandName, args = []) {
        return this.send({
            command: 'execute_command',
            command_name: commandName,
            args: args
        });
    }

    /**
     * Send WhatsApp message
     */
    sendWhatsAppMessage(contact, message) {
        return this.send({
            command: 'send_whatsapp',
            contact: contact,
            message: message
        });
    }

    /**
     * Send WhatsApp group message
     */
    sendWhatsAppGroupMessage(group, message) {
        return this.send({
            command: 'send_group_message',
            group: group,
            message: message
        });
    }

    /**
     * Get current state from server
     */
    getState() {
        return this.send({
            command: 'get_state'
        });
    }

    /**
     * Disconnect WebSocket
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Export for use
window.JarvisWebSocketClient = JarvisWebSocketClient;

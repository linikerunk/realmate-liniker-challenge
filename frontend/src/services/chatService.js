const API_URL = 'http://localhost:8000';

export const chatService = {
    async getConversations() {
        const response = await fetch(`${API_URL}/chat/conversations/`);
        if (!response.ok) {
            throw new Error('Erro ao buscar conversas');
        }
        return response.json();
    },

    async getConversationMessages(conversationId) {
        const response = await fetch(`${API_URL}/chat/conversations/${conversationId}/`);
        if (!response.ok) {
            throw new Error('Erro ao buscar mensagens');
        }
        return response.json();
    },

    async sendMessage(conversationId, content) {
        const response = await fetch(`${API_URL}/chat/webhook/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: 'NEW_MESSAGE',
                timestamp: new Date().toISOString(),
                data: {
                    id: crypto.randomUUID(),
                    conversation_id: conversationId,
                    content: content
                }
            })
        });
        
        if (!response.ok) {
            throw new Error('Erro ao enviar mensagem');
        }
        return response.json();
    },

    async createConversation() {
        const response = await fetch(`${API_URL}/chat/webhook/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: 'NEW_CONVERSATION',
                timestamp: new Date().toISOString(),
                data: {
                    id: crypto.randomUUID()
                }
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao criar conversa');
        }
        return response.json();
    },

    async closeConversation(conversationId) {
        const response = await fetch(`${API_URL}/chat/webhook/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: 'CLOSE_CONVERSATION',
                timestamp: new Date().toISOString(),
                data: {
                    id: conversationId
                }
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao encerrar conversa');
        }
        return response.json();
    }
};

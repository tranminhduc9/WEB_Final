/**
 * Chatbot Service - API calls cho Chatbot domain
 * Base URL: http://localhost:8080/api/v1
 * 
 * Endpoints theo WEB_CK.md:
 * - POST /chatbot/message - Send message to AI
 * - GET /chatbot/history - Get conversation history
 */

import axiosClient from '../api/axiosClient';
import type {
    ChatbotResponse,
    ChatbotMessageRequest,
    ChatbotHistoryResponse,
} from '../types/models';

// ============================
// CHATBOT SERVICE
// ============================

export const chatbotService = {
    /**
     * Gửi tin nhắn đến AI chatbot
     * POST /chatbot/message
     * Body: { conversation_id?: string | null, message: string }
     * 
     * Response includes:
     * - conversation_id: ID để tiếp tục hội thoại
     * - bot_response: Phản hồi từ AI
     * - suggested_places: Địa điểm gợi ý (optional)
     */
    sendMessage: async (message: string, conversationId?: string | null): Promise<ChatbotResponse> => {
        const requestBody: ChatbotMessageRequest = {
            conversation_id: conversationId,
            message
        };

        const response = await axiosClient.post<ChatbotMessageRequest, ChatbotResponse>(
            '/chatbot/message',
            requestBody
        );
        return response;
    },

    /**
     * Lấy lịch sử hội thoại
     * GET /chatbot/history?conversation_id=xxx
     */
    getHistory: async (conversationId?: string): Promise<ChatbotHistoryResponse> => {
        const url = conversationId
            ? `/chatbot/history?conversation_id=${conversationId}`
            : '/chatbot/history';

        const response = await axiosClient.get<never, ChatbotHistoryResponse>(url);
        return response;
    },
};

export default chatbotService;

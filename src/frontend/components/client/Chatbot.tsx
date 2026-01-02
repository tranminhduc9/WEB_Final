import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Icons } from '../../config/constants';
import { chatbotService } from '../../services';
import type { PlaceCompact } from '../../types/models';
import logo from '../../assets/images/logo.png';
import chatbotIcon from '../../assets/images/chatbot.png';
import unionBg from '../../assets/images/Union.png';
import '../../assets/styles/components/Chatbot.css';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  suggestedPlaces?: PlaceCompact[];
}

// Storage key for chat history
const CHAT_STORAGE_KEY = 'hanoivivu_chat_history';
const CHAT_EXPIRY_MINUTES = 15;

// Helper to check if chat history is expired
const isChatExpired = (lastMessageTime: string): boolean => {
  const lastTime = new Date(lastMessageTime).getTime();
  const now = Date.now();
  const diffMinutes = (now - lastTime) / (1000 * 60);
  return diffMinutes > CHAT_EXPIRY_MINUTES;
};

// Helper to load chat from localStorage
const loadChatFromStorage = (): { messages: Message[], conversationId: string | null } | null => {
  try {
    const stored = localStorage.getItem(CHAT_STORAGE_KEY);
    if (!stored) return null;

    const data = JSON.parse(stored);

    // Check if expired
    if (data.lastMessageTime && isChatExpired(data.lastMessageTime)) {
      localStorage.removeItem(CHAT_STORAGE_KEY);
      return null;
    }

    // Restore message timestamps as Date objects
    const messages = data.messages.map((msg: Message & { timestamp: string }) => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    }));

    return { messages, conversationId: data.conversationId };
  } catch {
    localStorage.removeItem(CHAT_STORAGE_KEY);
    return null;
  }
};

// Helper to save chat to localStorage
const saveChatToStorage = (messages: Message[], conversationId: string | null) => {
  try {
    const data = {
      messages,
      conversationId,
      lastMessageTime: new Date().toISOString()
    };
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(data));
  } catch (e) {
    console.error('Failed to save chat history:', e);
  }
};

const defaultMessage: Message = {
  id: 1,
  text: 'Xin chào! Tôi là trợ lý du lịch Hà Nội. Bạn cần hỗ trợ gì?',
  isUser: false,
  timestamp: new Date(),
};

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([defaultMessage]);
  const [inputValue, setInputValue] = useState('');
  const [userAvatar, setUserAvatar] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load chat history from localStorage on mount
  useEffect(() => {
    const stored = loadChatFromStorage();
    if (stored && stored.messages.length > 0) {
      setMessages(stored.messages);
      setConversationId(stored.conversationId);
    }
  }, []);

  // Save chat history to localStorage when messages change
  useEffect(() => {
    if (messages.length > 1) { // Only save if there's more than the default message
      saveChatToStorage(messages, conversationId);
    }
  }, [messages, conversationId]);

  // Lấy avatar người dùng từ localStorage
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        setUserAvatar(user.avatar || null);
      } catch (e) {
        setUserAvatar(null);
      }
    }
  }, [isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fallback response khi API fail
  const getFallbackResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();

    if (lowerMessage.includes('hồ gươm') || lowerMessage.includes('hồ hoàn kiếm')) {
      return 'Hồ Gươm là một địa điểm du lịch nổi tiếng ở Hà Nội! Bạn có thể đi dạo quanh hồ, thăm đền Ngọc Sơn và cầu Thê Húc. Thời điểm đẹp nhất là sáng sớm hoặc chiều tối.';
    }
    if (lowerMessage.includes('phố cổ')) {
      return 'Phố cổ Hà Nội nổi tiếng với 36 phố phường. Bạn nên thử các món ăn đường phố như phở, bún chả, và bánh mì. Đừng quên ghé thăm chợ Đồng Xuân!';
    }
    if (lowerMessage.includes('ăn gì') || lowerMessage.includes('đồ ăn')) {
      return 'Hà Nội có rất nhiều món ngon! Phở Bát Đàn, Bún chả Hương Liên, Bánh cuốn Thanh Vân... Bạn muốn tôi gợi ý địa điểm cụ thể không?';
    }
    if (lowerMessage.includes('khách sạn') || lowerMessage.includes('ở đâu')) {
      return 'Khu vực quanh Hồ Gươm và phố cổ có nhiều khách sạn tốt. Nếu muốn tiết kiệm, bạn có thể tìm homestay ở khu Tây Hồ hoặc Cầu Giấy.';
    }
    if (lowerMessage.includes('cảm ơn') || lowerMessage.includes('thank')) {
      return 'Không có gì! Chúc bạn có chuyến du lịch vui vẻ tại Hà Nội! 🎉';
    }

    return 'Cảm ơn bạn đã hỏi! Tôi có thể giúp bạn tìm địa điểm du lịch, nhà hàng, khách sạn tại Hà Nội. Bạn muốn tìm hiểu về điều gì?';
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    const newMessage: Message = {
      id: messages.length + 1,
      text: userMessage,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call real API
      const response = await chatbotService.sendMessage(userMessage, conversationId);

      // Save conversation ID for continuing the conversation
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add bot response with defensive coding
      const botResponse: Message = {
        id: messages.length + 2,
        text: response.bot_response || 'Xin lỗi, tôi không thể xử lý yêu cầu này.',
        isUser: false,
        timestamp: new Date(),
        suggestedPlaces: Array.isArray(response.suggested_places) ? response.suggested_places : [],
      };
      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error('Chatbot API error:', error);

      // Fallback to mock response
      const fallbackResponse: Message = {
        id: messages.length + 2,
        text: getFallbackResponse(userMessage),
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, fallbackResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleResetMessages = () => {
    // Xóa localStorage
    localStorage.removeItem(CHAT_STORAGE_KEY);
    
    // Reset messages về default
    setMessages([defaultMessage]);
    
    // Reset conversation ID
    setConversationId(null);
    
    // Scroll to top
    scrollToBottom();
  };

  return (
    <>
      {/* Floating Button */}
      <button
        className={`chatbot-toggle ${isOpen ? 'chatbot-toggle--open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle chatbot"
      >
        {isOpen ? (
          <Icons.Close className="chatbot-toggle__icon" />
        ) : (
          <img src={chatbotIcon} alt="Chatbot" className="chatbot-toggle__img" />
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div
          className="chatbot-window"
          style={{ backgroundImage: `url(${unionBg})` }}
        >
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header__avatar">
              <img src={logo} alt="Hanoivivu" />
            </div>
            <div className="chatbot-header__info">
              <h3>Trợ lý Hanoivivu</h3>
              <span className="chatbot-header__status">● Online</span>
            </div>
            <div className="chatbot-header__actions">
              <button 
                className="chatbot-header__reset" 
                onClick={handleResetMessages}
                title="Xóa tất cả tin nhắn"
                aria-label="Reset chat"
              >
                <Icons.Trash />
              </button>
              <button className="chatbot-header__close" onClick={() => setIsOpen(false)}>
                <Icons.Close />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`chatbot-message ${message.isUser ? 'chatbot-message--user' : 'chatbot-message--bot'
                  }`}
              >
                {/* Avatar cho bot (logo) */}
                {!message.isUser && (
                  <div className="chatbot-message__avatar chatbot-message__avatar--bot">
                    <img src={logo} alt="Bot" />
                  </div>
                )}

                {/* Nội dung tin nhắn */}
                <div className="chatbot-message__content">
                  {message.isUser ? (
                    <p>{message.text}</p>
                  ) : (
                    <div className="chatbot-markdown">
                      <ReactMarkdown>{message.text}</ReactMarkdown>
                    </div>
                  )}

                  {/* Suggested Places */}
                  {message.suggestedPlaces && message.suggestedPlaces.length > 0 && (
                    <div className="chatbot-suggestions">
                      <p className="chatbot-suggestions__title">Có thể bạn sẽ thích:</p>
                      <div className="chatbot-suggestions__list">
                        {message.suggestedPlaces.slice(0, 3).map((place) => (
                          <a
                            key={place.id}
                            href={`/location/${place.id}`}
                            className="chatbot-suggestion-card"
                            onClick={(e) => {
                              e.preventDefault();
                              setIsOpen(false);
                              window.location.href = `/location/${place.id}`;
                            }}
                          >
                            {place.main_image_url && (
                              <img
                                src={place.main_image_url}
                                alt={place.name}
                                className="chatbot-suggestion-card__image"
                              />
                            )}
                            <div className="chatbot-suggestion-card__info">
                              <span className="chatbot-suggestion-card__name">{place.name}</span>
                              {(place.rating_average ?? 0) > 0 && (
                                <span className="chatbot-suggestion-card__rating">
                                  ⭐ {Number(place.rating_average || 0).toFixed(1)}
                                </span>
                              )}
                            </div>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Avatar cho user */}
                {message.isUser && (
                  <div className="chatbot-message__avatar chatbot-message__avatar--user">
                    {userAvatar ? (
                      <img src={userAvatar} alt="User" />
                    ) : (
                      <div className="chatbot-message__avatar-placeholder">
                        U
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="chatbot-message chatbot-message--bot">
                <div className="chatbot-message__avatar chatbot-message__avatar--bot">
                  <img src={logo} alt="Bot" />
                </div>
                <div className="chatbot-message__content chatbot-message__typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="chatbot-input">
            <input
              type="text"
              placeholder="Nhập tin nhắn..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button onClick={handleSendMessage} disabled={!inputValue.trim() || isLoading}>
              <Icons.Send className="chatbot-input__icon" />
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Chatbot;

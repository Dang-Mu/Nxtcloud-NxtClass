// 📁 src/hooks/useChatbot.js
import { useState, useCallback } from "react";
import { findAnswer } from "../utils/faqMatcher";

export const useChatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "안녕하세요! 교학팀 FAQ 챗봇입니다. 궁금한 것을 물어보세요!",
      isBot: true,
      timestamp: new Date().toLocaleTimeString("ko-KR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    },
  ]);

  const [isTyping, setIsTyping] = useState(false);

  /**
   * 새 메시지 추가
   */
  const addMessage = useCallback((text, isBot = false) => {
    const newMessage = {
      id: Date.now() + Math.random(),
      text,
      isBot,
      timestamp: new Date().toLocaleTimeString("ko-KR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, newMessage]);
    return newMessage;
  }, []);

  /**
   * 사용자 메시지 전송 및 봇 응답 처리
   */
  const sendMessage = useCallback(
    async (userInput) => {
      if (!userInput || !userInput.trim()) return;

      // 사용자 메시지 추가
      addMessage(userInput.trim(), false);

      // 타이핑 인디케이터 표시
      setIsTyping(true);

      // 봇 응답 시뮬레이션 (1초 지연)
      setTimeout(() => {
        const response = findAnswer(userInput.trim());
        addMessage(response, true);
        setIsTyping(false);
      }, 1000);
    },
    [addMessage]
  );

  /**
   * 채팅 기록 초기화
   */
  const clearChat = useCallback(() => {
    setMessages([
      {
        id: 1,
        text: "안녕하세요! 교학팀 FAQ 챗봇입니다. 궁금한 것을 물어보세요!",
        isBot: true,
        timestamp: new Date().toLocaleTimeString("ko-KR", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
    ]);
    setIsTyping(false);
  }, []);

  return {
    messages,
    isTyping,
    sendMessage,
    clearChat,
    messageCount: messages.length,
  };
};

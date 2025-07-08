// 📁 src/components/ChatMessage.js
import React from "react";

const ChatMessage = ({ message }) => {
  const { text, isBot, timestamp } = message;

  return (
    <div className={`flex ${isBot ? "justify-start" : "justify-end"} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg shadow-sm ${
          isBot ? "bg-gray-100 text-gray-800" : "bg-blue-600 text-white"
        }`}
      >
        <p className="whitespace-pre-line text-sm leading-relaxed">{text}</p>
        <p
          className={`text-xs mt-2 ${
            isBot ? "text-gray-500" : "text-blue-200"
          }`}
        >
          {timestamp}
        </p>
      </div>
    </div>
  );
};

export default ChatMessage;

// 📁 src/components/ChatHeader.js
import React from "react";
import { MessageCircle, RotateCcw } from "lucide-react";

const ChatHeader = ({ onClearChat }) => {
  return (
    <div className="bg-blue-600 text-white p-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <MessageCircle size={24} />
        <div>
          <h1 className="text-lg font-bold">교학팀 FAQ 챗봇</h1>
          <p className="text-sm opacity-90">
            학사 관련 궁금한 점을 물어보세요!
          </p>
        </div>
      </div>
      <button
        onClick={onClearChat}
        className="p-2 hover:bg-blue-700 rounded-lg transition-colors duration-200"
        title="채팅 초기화"
      >
        <RotateCcw size={20} />
      </button>
    </div>
  );
};

export default ChatHeader;

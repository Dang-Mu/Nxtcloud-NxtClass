// 📁 src/App.js
import React from "react";
import ChatHeader from "./components/ChatHeader";
import ChatContainer from "./components/ChatContainer";
import QuickQuestions from "./components/QuickQuestions";
import ChatInput from "./components/ChatInput";
import ChatStats from "./components/ChatStats";
import { useChatbot } from "./hooks/useChatbot";

function App() {
  const { messages, isTyping, sendMessage, clearChat, messageCount } =
    useChatbot();

  return (
    <div className="flex flex-col h-screen max-w-6xl mx-auto bg-white shadow-lg">
      <ChatHeader onClearChat={clearChat} />
      <ChatContainer messages={messages} isTyping={isTyping} />
      <QuickQuestions onQuestionClick={sendMessage} />
      <ChatInput onSendMessage={sendMessage} disabled={isTyping} />
      <ChatStats messageCount={messageCount} />
    </div>
  );
}

export default App;

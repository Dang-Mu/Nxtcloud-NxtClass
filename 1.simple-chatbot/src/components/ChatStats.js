// 📁 src/components/ChatStats.js
import React from "react";
import { Book, MessageCircle, Clock, Star } from "lucide-react";
import { faqDatabase } from "../data/faqData";

const ChatStats = ({ messageCount }) => {
  const stats = [
    {
      icon: Book,
      label: `FAQ 데이터: ${faqDatabase.length}개`,
      color: "text-blue-600",
    },
    {
      icon: MessageCircle,
      label: `대화 수: ${messageCount}`,
      color: "text-green-600",
    },
    {
      icon: Clock,
      label: "응답속도: ~1초",
      color: "text-purple-600",
    },
    {
      icon: Star,
      label: "키워드 기반",
      color: "text-orange-600",
    },
  ];

  return (
    <div className="p-4 bg-gray-100 border-t">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const IconComponent = stat.icon;
          return (
            <div
              key={index}
              className="flex items-center justify-center gap-2 text-sm"
            >
              <IconComponent size={16} className={stat.color} />
              <span className="text-gray-700">{stat.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ChatStats;

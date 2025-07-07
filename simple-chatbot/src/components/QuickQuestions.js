// 📁 src/components/QuickQuestions.js
import React from "react";

const QuickQuestions = ({ onQuestionClick }) => {
  const quickQuestions = [
    "수강신청 언제?",
    "졸업요건 알려줘",
    "재학증명서 발급",
    "휴학 어떻게?",
    "도서관 운영시간",
    "성적 언제 나와요?",
    "복수전공 신청",
  ];

  return (
    <div className="p-4 border-t bg-gray-50">
      <p className="text-sm text-gray-600 mb-3 font-medium">빠른 질문:</p>
      <div className="flex flex-wrap gap-2">
        {quickQuestions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionClick(question)}
            className="px-3 py-2 bg-white border border-gray-300 rounded-full text-sm hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 shadow-sm"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickQuestions;

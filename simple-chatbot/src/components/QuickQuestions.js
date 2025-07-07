import React from "react";

import React from "react";

const QuickQuestions = ({ onQuestionClick }) => {
  const quickQuestions = [
    // 더 구체적이고 명확한 질문들
    "수강신청 기간", // 기간 문의
    "수강신청 방법", // 방법 문의
    "재학증명서 발급", // 증명서
    "졸업 학점", // 졸업요건
    "휴학 신청", // 휴학
    "성적 발표일", // 성적
    "도서관 운영시간", // 기타
    "복수전공 신청", // 학적변경
  ];

  return (
    <div className="p-4 border-t bg-gray-50">
      <p className="text-sm text-gray-600 mb-3 font-medium">
        빠른 질문 (클릭하세요):
      </p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {quickQuestions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionClick(question)}
            className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 shadow-sm text-left"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickQuestions;

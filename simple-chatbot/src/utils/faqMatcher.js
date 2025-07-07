// 📁 src/utils/faqMatcher.js
import { faqDatabase } from "../data/faqData";

/**
 * 사용자 입력에서 가장 적합한 FAQ 답변을 찾는 함수
 * @param {string} userInput - 사용자 입력 텍스트
 * @returns {string} FAQ 답변 또는 기본 메시지
 */
export const findAnswer = (userInput) => {
  if (!userInput || typeof userInput !== "string") {
    return getDefaultMessage();
  }

  const input = userInput.toLowerCase().trim();
  const matches = [];

  // 각 FAQ 항목에 대해 매칭 점수 계산
  for (const faq of faqDatabase) {
    let score = 0;
    let matchedKeywords = 0;

    // 키워드 매칭 검사
    for (const keyword of faq.keywords) {
      if (input.includes(keyword.toLowerCase())) {
        score += 10; // 기본 키워드 매칭 점수
        matchedKeywords++;

        // 정확한 매칭일 경우 추가 점수
        if (input === keyword.toLowerCase()) {
          score += 20;
        }
      }
    }

    // 매칭된 키워드가 있는 경우만 결과에 포함
    if (matchedKeywords > 0) {
      matches.push({
        faq,
        score: score + faq.priority * 5, // 우선순위 반영
        matchedKeywords,
      });
    }
  }

  // 점수 순으로 정렬
  matches.sort((a, b) => b.score - a.score);

  // 가장 높은 점수의 답변 반환
  if (matches.length > 0) {
    return matches[0].faq.answer;
  }

  return getDefaultMessage();
};

/**
 * 기본 안내 메시지 반환
 * @returns {string} 기본 안내 메시지
 */
const getDefaultMessage = () => {
  return `죄송합니다. 해당 질문에 대한 답변을 찾을 수 없습니다.

자주 묻는 질문 카테고리:
• 수강신청 관련
• 졸업요건 관련  
• 증명서 발급
• 성적 관련
• 휴학/복학
• 학적변경

더 자세한 상담이 필요하시면:
📞 교학과: 02-123-4567
📧 academic@university.ac.kr
🕐 상담시간: 평일 09:00-18:00`;
};

/**
 * 카테고리별 FAQ 목록 반환
 * @param {string} category - 카테고리명
 * @returns {Array} 해당 카테고리의 FAQ 목록
 */
export const getFAQsByCategory = (category) => {
  return faqDatabase.filter((faq) => faq.category === category);
};

/**
 * 모든 카테고리 목록 반환
 * @returns {Array} 유니크한 카테고리 목록
 */
export const getAllCategories = () => {
  return [...new Set(faqDatabase.map((faq) => faq.category))];
};

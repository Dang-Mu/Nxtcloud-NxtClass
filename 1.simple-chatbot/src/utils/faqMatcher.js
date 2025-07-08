// 📁 src/utils/faqMatcher.js - 개선된 매칭 알고리즘
import { faqDatabase } from "../data/faqData";
/**
 * 개선된 FAQ 매칭 알고리즘
 * 더 정확한 의도 파악을 위한 고급 매칭
 */

export const findAnswer = (userInput) => {
  if (!userInput || typeof userInput !== "string") {
    return getDefaultMessage();
  }

  const input = userInput.toLowerCase().trim();
  const matches = [];

  // 각 FAQ 항목에 대해 정교한 매칭 점수 계산
  for (const faq of faqDatabase) {
    let score = 0;
    let matchedKeywords = [];

    // 1. 정확한 문구 매칭 (최고 점수)
    for (const keyword of faq.keywords) {
      if (input === keyword.toLowerCase()) {
        score += 50; // 정확한 매칭
        matchedKeywords.push(keyword);
      }
    }

    // 2. 완전 포함 매칭
    for (const keyword of faq.keywords) {
      if (
        input.includes(keyword.toLowerCase()) &&
        input !== keyword.toLowerCase()
      ) {
        score += 30; // 포함 매칭
        matchedKeywords.push(keyword);
      }
    }

    // 3. 부분 매칭
    for (const keyword of faq.keywords) {
      if (keyword.toLowerCase().includes(input) && input.length > 2) {
        score += 15; // 부분 매칭
        matchedKeywords.push(keyword);
      }
    }

    // 4. 복합 키워드 매칭 (예: "수강신청 방법")
    const inputWords = input.split(" ");
    if (inputWords.length > 1) {
      for (const keyword of faq.keywords) {
        const keywordWords = keyword.toLowerCase().split(" ");
        const matchingWords = inputWords.filter((word) =>
          keywordWords.some((kw) => kw.includes(word) || word.includes(kw))
        );

        if (matchingWords.length === inputWords.length) {
          score += 40; // 모든 단어 매칭
          matchedKeywords.push(keyword);
        } else if (matchingWords.length > 1) {
          score += 20; // 부분 단어 매칭
          matchedKeywords.push(keyword);
        }
      }
    }

    // 5. 우선순위 보너스
    if (score > 0) {
      score += (4 - faq.priority) * 5; // 우선순위가 높을수록 보너스

      matches.push({
        faq,
        score,
        matchedKeywords: [...new Set(matchedKeywords)], // 중복 제거
      });
    }
  }

  // 점수 순으로 정렬
  matches.sort((a, b) => b.score - a.score);

  // 디버깅을 위한 로그 (개발용)
  if (process.env.NODE_ENV === "development" && matches.length > 0) {
    console.log("매칭 결과:", {
      query: userInput,
      topMatch: matches[0],
      allMatches: matches.slice(0, 3),
    });
  }

  // 가장 높은 점수의 답변 반환
  if (matches.length > 0) {
    return matches[0].faq.answer;
  }

  return getDefaultMessage();
};

/**
 * 기본 안내 메시지 - 더 도움이 되는 내용으로 개선
 */
const getDefaultMessage = () => {
  return `죄송합니다. 해당 질문에 대한 답변을 찾을 수 없습니다.

💡 검색 팁:
• "수강신청 방법" (구체적으로)
• "졸업 학점" (간단하게)
• "증명서 발급" (명확하게)

📋 주요 카테고리:
• 수강신청 관련 (기간, 방법, 정정, 오류)
• 졸업요건 관련 (학점, 논문)  
• 증명서 발급 (재학, 성적, 졸업)
• 성적 관련 (발표, 이의신청, 재수강)
• 휴학/복학 (신청방법, 기간)
• 학적변경 (전과, 복수전공)

📞 직접 상담:
• 교학과: 02-123-4567
• 이메일: academic@university.ac.kr
• 상담시간: 평일 09:00-18:00`;
};

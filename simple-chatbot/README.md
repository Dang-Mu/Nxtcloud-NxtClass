# 교학팀 FAQ 챗봇

학교 교학팀에서 자주 받는 질문들에 대한 자동 응답 챗봇 시스템입니다.

## 🚀 주요 기능

- **키워드 기반 FAQ 매칭**: 사용자 질문을 분석하여 가장 적합한 답변 제공
- **실시간 채팅 인터페이스**: 직관적이고 사용하기 쉬운 대화형 UI
- **빠른 질문 버튼**: 자주 묻는 질문들을 빠르게 선택할 수 있는 버튼
- **카테고리별 FAQ 관리**: 수강신청, 졸업요건, 증명서 등 카테고리별로 체계적 관리
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 모든 기기에서 최적화된 경험

## 📁 프로젝트 구조

```
src/
├── components/           # React 컴포넌트들
│   ├── ChatHeader.js    # 헤더 컴포넌트
│   ├── ChatContainer.js # 메시지 컨테이너
│   ├── ChatMessage.js   # 개별 메시지 컴포넌트
│   ├── ChatInput.js     # 입력 인터페이스
│   ├── QuickQuestions.js # 빠른 질문 버튼들
│   ├── TypingIndicator.js # 타이핑 인디케이터
│   └── ChatStats.js     # 통계 표시
├── data/
│   └── faqData.js       # FAQ 데이터베이스
├── hooks/
│   └── useChatbot.js    # 챗봇 로직 훅
├── utils/
│   └── faqMatcher.js    # FAQ 매칭 유틸리티
├── App.js               # 메인 앱 컴포넌트
└── index.js             # 앱 진입점
```

## 🛠 설치 및 실행

### 1. 프로젝트 생성

```bash
npx create-react-app faq-chatbot
cd faq-chatbot
```

### 2. 의존성 설치

```bash
npm install lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 3. 파일 복사

위의 코드들을 각각 해당 파일에 복사

### 4. 개발 서버 실행

```bash
npm start
```

### 5. 빌드 (배포용)

```bash
npm run build
```

## 🎯 FAQ 데이터 추가/수정하기

### 새로운 FAQ 추가

`src/data/faqData.js` 파일에서 `faqDatabase` 배열에 새 객체 추가:

```javascript
{
  id: 16, // 유니크한 ID
  category: "새카테고리", // 카테고리명
  keywords: ['키워드1', '키워드2', '키워드3'], // 검색 키워드들
  question: "질문 제목",
  answer: "답변 내용\n• 항목1\n• 항목2",
  priority: 1 // 우선순위 (1이 가장 높음)
}
```

### 카테고리 색상 추가

같은 파일의 `categoryColors` 객체에 새 카테고리 색상 추가:

```javascript
export const categoryColors = {
  // ... 기존 색상들
  새카테고리: "#색상코드",
};
```

## 📊 성능 최적화

### 키워드 매칭 알고리즘

- 정확한 키워드 매칭: +30점
- 부분 키워드 매칭: +10점
- 우선순위 반영: priority \* 5점
- 최고 점수의 답변 선택

### 컴포넌트 최적화

- `useCallback`으로 함수 메모이제이션
- `useRef`로 DOM 직접 조작 최소화
- 불필요한 리렌더링 방지

## 🚀 배포 방법

### Netlify 배포

```bash
npm run build
# dist 폴더를 Netlify에 드래그 앤 드롭
```

### Vercel 배포

```bash
npm install -g vercel
vercel --prod
```

### AWS S3 + CloudFront 배포

```bash
npm run build
aws s3 sync build/ s3://your-bucket-name
```

## 🔧 커스터마이징 가이드

### 1. 브랜딩 변경

- `src/components/ChatHeader.js`에서 제목과 설명 수정
- `tailwind.config.js`에서 색상 테마 변경
- `public/index.html`에서 페이지 제목과 메타 정보 수정

### 2. 스타일링 변경

- `src/index.css`에서 전역 스타일 수정
- 각 컴포넌트의 Tailwind 클래스 수정
- 애니메이션과 인터랙션 효과 조정

### 3. 기능 확장

- `src/utils/faqMatcher.js`에서 매칭 알고리즘 개선
- `src/hooks/useChatbot.js`에서 챗봇 로직 확장
- 새로운 컴포넌트 추가로 기능 확장

## 🧪 테스트

### 단위 테스트 실행

```bash
npm test
```

### E2E 테스트 (Cypress)

```bash
npm install -D cypress
npx cypress open
```

## 📈 모니터링 및 분석

### 사용자 행동 분석

- Google Analytics 연동 가능
- 자주 묻는 질문 패턴 분석
- 응답 만족도 피드백 수집

### 성능 모니터링

- 응답 시간 측정
- 키워드 매칭 정확도 분석
- 사용자 이탈률 추적

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🎓 교육 목적

이 프로젝트는 다음 학습 목표를 가지고 있습니다:

### 1단계 학습 포인트

- **장점**: 빠른 응답, 24시간 서비스, 일관된 정보 제공
- **한계**: 미리 정의된 질문만 처리, 복잡한 질의 처리 불가
- **다음 단계 필요성**: "문서에서 찾아서 답변해주면 좋겠다"

### 실습 과제

1. **FAQ 데이터 추가하기**

   - 새로운 카테고리 "장학금" 추가
   - 장학금 관련 질문 5개 이상 작성
   - 키워드 최적화하여 검색 정확도 향상

2. **사용자 경험 개선**

   - 새로운 빠른 질문 버튼 추가
   - 카테고리별 색상 테마 변경
   - 모바일 반응형 디자인 개선

3. **기능 확장**
   - 이전 대화 기록 저장 기능
   - 즐겨찾기 질문 기능
   - 피드백 수집 시스템

### 학습 후 느껴야 할 한계점

- "개인 맞춤형 답변이 안 돼"
- "복잡한 계산이나 분석이 필요한 질문은 못 해"
- "실시간 정보나 변경되는 정보는 반영 안 돼"

이러한 한계점을 체험한 후 다음 단계인 **RAG 시스템**의 필요성을 자연스럽게 느끼게 됩니다.

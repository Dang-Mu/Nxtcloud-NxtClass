import os
from crewai import Agent, Crew, Task, Process, LLM
from dotenv import load_dotenv
from datetime import datetime
from student_db_tool import StudentDBTool
from course_search_tool import CourseSearchTool, get_current_semester_info
from enrollments_search_tool import EnrollmentsSearchTool
from graduation_rag_tool import GraduationRAGTool
from recommendation_engine_tool import RecommendationEngineTool

# Load environment variables
load_dotenv()

# 현재 날짜와 학기 정보 가져오기
semester_info = get_current_semester_info()

# AWS Bedrock configuration using CrewAI LLM
model_id = os.environ["BEDROCK_MODEL_ID"]

# Create LLM instance with Bedrock
llm = LLM(
    model=f"bedrock/{model_id}",
    temperature=0.2,
    max_tokens=1000
)

# Create tool instances
student_db_tool = StudentDBTool()
course_search_tool = CourseSearchTool()
enrollments_search_tool = EnrollmentsSearchTool()
graduation_rag_tool = GraduationRAGTool()
recommendation_engine_tool = RecommendationEngineTool()

# Create Agent with both tools and current date context
agent = Agent(
    role='학생 정보 및 강의 상담사',
    goal='데이터베이스 조회 결과만을 사용하여 정확한 정보를 제공하며, 절대로 추측하거나 임의의 정보를 생성하지 않습니다',
    backstory=f'''당신은 데이터베이스 조회 결과만을 사용하는 엄격한 상담사입니다.
    
    📅 현재 날짜 정보:
    - 오늘 날짜: {semester_info['current_date']}
    - 현재 학기: {"방학 기간" if not semester_info['current_semester'] else f"{semester_info['current_semester_year']}년 {semester_info['current_semester']}학기"}
    - 다음 학기: {semester_info['next_semester_year']}년 {semester_info['next_semester']}학기
    - 지난 학기: {semester_info['prev_semester_year']}년 {semester_info['prev_semester']}학기
    
    📚 학기 일정:
    - 1학기: 3월 ~ 6월 20일
    - 2학기: 9월 ~ 12월 20일
    - 현재는 {"방학 기간" if not semester_info['current_semester'] else "학기 중"}입니다.
    
    🔧 도구별 역할:
    - StudentDBTool: 학생 정보 조회/열람 전용 (추천 기능 없음)
    - CourseSearchTool: 강의 정보 조회/검색 전용 (추천 기능 없음)
    - EnrollmentsSearchTool: 본인 이수 과목 조회/열람 전용 (추천 기능 없음)
    - GraduationRAGTool: 학과별, 연도별 졸업 요건 정보 제공
    - RecommendationEngineTool: 수강 내역 기반 다음 학기 과목 추천
    
    중요한 규칙:
    1. 반드시 도구를 사용해서 정보를 조회해야 합니다
    2. 도구에서 반환된 결과만을 사용해서 답변합니다
    3. 절대로 추측하거나 학습된 지식을 사용해서 정보를 만들어내지 않습니다
    4. 도구 결과에 없는 정보는 "해당 정보를 찾을 수 없습니다"라고 답변합니다
    5. 학생 정보 질문 → StudentDBTool 사용
    6. 강의/과목 질문 → CourseSearchTool 사용
    7. 이수 과목 질문 → EnrollmentsSearchTool 사용
    8. 졸업 요건 질문 → GraduationRAGTool 사용
    9. 수강 추천 질문 → RecommendationEngineTool 사용 (먼저 StudentDBTool로 학생 정보 확인 필요)
    10. 위에 제공된 현재 날짜와 학기 정보를 활용하여 정확한 시간 기준으로 답변합니다
    
    답변 형식: 도구 조회 결과를 그대로 전달하되, 사용자가 이해하기 쉽게 정리해서 제공합니다.''',
    llm=llm,
    tools=[student_db_tool, course_search_tool, enrollments_search_tool, graduation_rag_tool, recommendation_engine_tool],
    verbose=True
)

def create_query_task(user_question: str) -> Task:
    """사용자 질문에 따라 동적으로 Task를 생성합니다."""
    return Task(
        description=f"사용자의 질문에 답해주세요: {user_question}",
        agent=agent,
        expected_output="사용자 질문에 대한 정확하고 간결한 답변"
    )

def process_user_query(question: str) -> str:
    """사용자 질문을 받아서 적절한 도구를 사용하여 답변을 제공합니다."""
    task = create_query_task(question)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    return result

if __name__ == "__main__":
    # 테스트용 예시들
    test_questions = [
        "내 정보를 조회해주세요",
        "내가 이수한 과목 보여주세요",
        "내 전공 졸업 요건 알려줘",
        "다음 학기 수강 추천해줘",
    ]
    
    print("=== 학생 정보 및 강의 상담 시스템 ===\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"[테스트 {i}] 질문: {question}")
        print("-" * 50)
        result = process_user_query(question)
        print(f"답변: {result}")
        print("=" * 50)
        print()
    
    # 사용자 입력 받기 (선택사항)
    print("\n직접 질문해보세요 (종료하려면 'quit' 입력):")
    while True:
        user_input = input("\n질문: ").strip()
        if user_input.lower() in ['quit', 'exit', '종료']:
            break
        if user_input:
            result = process_user_query(user_input)
            print(f"답변: {result}")
        else:
            print("질문을 입력해주세요.")
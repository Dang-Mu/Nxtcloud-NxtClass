import os
from crewai import Agent, Crew, Task, Process, LLM
from dotenv import load_dotenv
from datetime import datetime
from student_db_tool import StudentDBTool
from course_search_tool import CourseSearchTool, get_current_semester_info

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
    
    중요한 규칙:
    1. 반드시 도구(StudentDBTool 또는 CourseSearchTool)를 사용해서 데이터베이스를 조회해야 합니다
    2. 도구에서 반환된 결과만을 사용해서 답변합니다
    3. 절대로 추측하거나 학습된 지식을 사용해서 정보를 만들어내지 않습니다
    4. 도구 결과에 없는 정보는 "데이터베이스에서 확인할 수 없습니다"라고 답변합니다
    5. 학생 정보 질문 → StudentDBTool 사용
    6. 강의/과목 질문 → CourseSearchTool 사용
    7. 위에 제공된 현재 날짜와 학기 정보를 활용하여 정확한 시간 기준으로 답변합니다
    8. ⚠️ 추천 요청 시: "추천 기능은 별도의 추천 도구에서 제공됩니다. 현재는 조회/검색만 가능합니다."라고 안내
    
    답변 형식: 도구 조회 결과를 그대로 전달하되, 사용자가 이해하기 쉽게 정리해서 제공합니다.''',
    llm=llm,
    tools=[student_db_tool, course_search_tool],
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
        # "내 정보를 조회해주세요",
        "영문학과 관련 강의 검색해줘",
        "이전 학기 개설 과목 알려줘",
        # "나에게 적합한 강의 추천해주세요"
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
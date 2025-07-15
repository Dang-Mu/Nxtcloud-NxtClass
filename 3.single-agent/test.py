import os
import mysql.connector
from crewai import Agent, Crew, Task, Process, LLM
from crewai.tools import BaseTool
from dotenv import load_dotenv
from typing import Type
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Custom Tool for Student DB queries
class StudentDBToolInput(BaseModel):
    """Input schema for StudentDBTool."""
    query: str = Field(..., description="SQL query or natural language description of what student information to retrieve")

class StudentDBTool(BaseTool):
    name: str = "student_db_tool"
    description: str = """
    학생 데이터베이스 조회 도구입니다. 
    사용 가능한 테이블: students, major
    - students 테이블: student_id, name, major_code, completed_semester, admission_year
    - major 테이블: college, department, dept_code, major_name, major_code
    학생 정보 조회 시 자동으로 전공 정보와 함께 제공됩니다.
    """
    args_schema: Type[BaseModel] = StudentDBToolInput

    def _run(self, query: str) -> str:
        """Execute database query to get student information."""
        try:
            # Database connection
            connection = mysql.connector.connect(
                host=os.environ["RDS_HOST"],
                port=int(os.environ["RDS_PORT"]),
                database=os.environ["RDS_DATABASE"],
                user=os.environ["RDS_USERNAME"],
                password=os.environ["RDS_PASSWORD"]
            )
            cursor = connection.cursor(dictionary=True)
            
            # 자연어 쿼리 처리
            if "학생" in query and ("정보" in query or "찾" in query):
                # 학생 이름 추출
                student_name = None
                words = query.split()
                for word in words:
                    if len(word) >= 2 and word not in ["학생", "정보", "찾아", "알려", "조회"]:
                        student_name = word
                        break
                
                if student_name:
                    # 학생 정보와 전공 정보를 JOIN해서 조회
                    sql_query = """
                    SELECT 
                        s.name as 학생이름,
                        s.student_id as 학번,
                        s.major_code as 전공코드,
                        s.completed_semester as 이수학기,
                        s.admission_year as 입학년도,
                        m.major_name as 전공명,
                        m.department as 학과,
                        m.college as 단과대학
                    FROM students s
                    LEFT JOIN major m ON s.major_code = m.major_code
                    WHERE s.name = %s
                    """
                    cursor.execute(sql_query, (student_name,))
                    results = cursor.fetchall()
                else:
                    return "학생 이름을 찾을 수 없습니다. 구체적인 학생 이름을 제공해주세요."
            
            elif "입학년도" in query or "입학" in query:
                # 입학년도별 학생 조회
                year = None
                words = query.split()
                for word in words:
                    if word.isdigit() and len(word) == 4:
                        year = int(word)
                        break
                
                if year:
                    sql_query = """
                    SELECT 
                        s.name as 학생이름,
                        s.student_id as 학번,
                        s.major_code as 전공코드,
                        s.completed_semester as 이수학기,
                        s.admission_year as 입학년도,
                        COALESCE(m.major_name, '전공정보없음') as 전공명,
                        COALESCE(m.department, '학과정보없음') as 학과,
                        COALESCE(m.college, '단과대학정보없음') as 단과대학
                    FROM students s
                    LEFT JOIN major m ON s.major_code = m.major_code
                    WHERE s.admission_year = %s
                    ORDER BY s.student_id
                    """
                    cursor.execute(sql_query, (year,))
                    results = cursor.fetchall()
                else:
                    return "입학년도를 찾을 수 없습니다. 4자리 연도를 포함해서 질문해주세요."
            
            elif "전체" in query or "모든" in query or "리스트" in query:
                # 전체 학생 목록 조회 (제한적으로)
                sql_query = """
                SELECT 
                    s.name as 학생이름,
                    s.student_id as 학번,
                    m.department as 학과,
                    m.college as 단과대학
                FROM students s
                LEFT JOIN major m ON s.major_code = m.major_code
                LIMIT 10
                """
                cursor.execute(sql_query)
                results = cursor.fetchall()
            
            elif query.strip().upper().startswith("SELECT"):
                # 직접 SQL 쿼리 (students, major 테이블만 허용)
                if "students" in query.lower() or "major" in query.lower():
                    cursor.execute(query)
                    results = cursor.fetchall()
                else:
                    return "students와 major 테이블만 사용할 수 있습니다."
            
            else:
                return """
                사용 가능한 명령어:
                - '학생이름 학생의 정보를 찾아주세요' (예: 다인장 학생의 정보를 찾아주세요)
                - '전체 학생 리스트를 보여주세요'
                - 직접 SQL 쿼리 (SELECT 문만, students/major 테이블만)
                """
            
            if not results:
                return "조회된 데이터가 없습니다."
            
            # 결과 포맷팅
            if len(results) == 1:
                # 단일 학생 정보 상세 표시
                student = results[0]
                formatted_result = "=== 학생 정보 ===\n"
                for key, value in student.items():
                    if value is not None:
                        formatted_result += f"{key}: {value}\n"
                return formatted_result
            else:
                # 여러 학생 목록 표시
                formatted_results = []
                for i, row in enumerate(results, 1):
                    formatted_results.append(f"{i}. {dict(row)}")
                return "조회 결과:\n" + "\n".join(formatted_results)
            
        except Exception as e:
            return f"데이터베이스 오류: {str(e)}"
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

# AWS Bedrock configuration using CrewAI LLM
model_id = os.environ["BEDROCK_MODEL_ID"]

# Create LLM instance with Bedrock
llm = LLM(
    model=f"bedrock/{model_id}",
    temperature=0.7,
    max_tokens=1000
)

# Create StudentDBTool instance
student_db_tool = StudentDBTool()

# Create CourseSearchTool instance
course_search_tool = CourseSearchTool()

# Create Agent with StudentDBTool
agent = Agent(
    role='학생 정보 상담사',
    goal='학생 정보를 정확하고 간결하게 제공하며, 불확실한 정보는 솔직하게 모른다고 답변합니다',
    backstory='''데이터베이스를 조회해서 정확한 정보만 제공하는 상담사입니다. 
    인사말이나 자기소개는 하지 않고, "질문에 답해드릴게요" 정도의 간단한 멘트로 시작합니다.
    확실하지 않은 정보는 추측하지 않고 "잘 모르겠습니다"라고 솔직하게 답변합니다.
    모든 답변은 한국어로, 정중하면서도 간결하게 제공합니다.''',
    llm=llm,
    tools=[student_db_tool],
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
        "2020년도 입학한 학생들 정보를 조회해주세요",
        "다인장 학생의 정보를 찾아주세요",
        "전체 학생 리스트를 보여주세요"
    ]
    
    print("=== 학생 정보 조회 시스템 테스트 ===\n")
    
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
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

# Custom Tool for Course Search queries
class CourseSearchToolInput(BaseModel):
    """Input schema for CourseSearchTool."""
    query: str = Field(..., description="강의 검색을 위한 SQL 쿼리 또는 자연어 설명")

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
                    # 학생 정보와 전공 정보를 JOIN해서 조회 (major_code 제외)
                    sql_query = """
                    SELECT 
                        s.name as 학생이름,
                        s.student_id as 학번,
                        s.completed_semester as 이수학기,
                        s.admission_year as 입학년도,
                        COALESCE(m.major_name, '전공정보없음') as 전공명,
                        COALESCE(m.department, '학과정보없음') as 학과,
                        COALESCE(m.college, '단과대학정보없음') as 단과대학
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

class CourseSearchTool(BaseTool):
    name: str = "course_search_tool"
    description: str = """
    강의 정보 조회 도구입니다.
    사용 가능한 테이블: courses, major
    - courses 테이블: course_code, course_name, credits, course_type, department, professor, note, target_grade, offered_year, offered_semester
    - major 테이블: college, department, dept_code, major_name, major_code
    강의 검색, 교수별 강의 조회, 학기별 강의 조회, 전공별 강의 조회가 가능합니다.
    target_grade는 특정 학년 외에 2-4의 경우 2학년부터 4학년까지라는 의미이며, 어떤 과목은 전체 학년이 수강 가능하기도 합니다.
    """
    args_schema: Type[BaseModel] = CourseSearchToolInput

    def _parse_query_conditions(self, query: str) -> dict:
        """자연어 쿼리에서 조건들을 추출합니다."""
        import re
        
        conditions = {
            'grade': None,
            'department': None,
            'subject_keyword': None,
            'professor': None,
            'course_type': None
        }
        
        # 학년 추출 (1학년, 2학년, 3학년, 4학년)
        grade_match = re.search(r'([1-4])학년', query)
        if grade_match:
            conditions['grade'] = grade_match.group(1)
        
        # 학과명 추출 (~~학과, ~~과)
        dept_patterns = [
            r'(\w+학과)',
            r'(\w+과)(?!목)',  # '과목'의 '과'는 제외
            r'(\w+)학과',
            r'(\w+)과(?!목)'
        ]
        for pattern in dept_patterns:
            dept_match = re.search(pattern, query)
            if dept_match:
                dept_name = dept_match.group(1)
                # 일반적인 단어들 제외
                if dept_name not in ['과목', '학과', '전공', '강의']:
                    conditions['department'] = dept_name
                    break
        
        # 과목 키워드 추출 (심리학, 수학, 영어 등)
        subject_keywords = ['심리학', '심리', '수학', '영어', '물리학', '화학', '생물학', 
                          '역사', '철학', '경제학', '경영학', '컴퓨터', '프로그래밍',
                          '데이터', '인공지능', 'AI', '머신러닝', '통계']
        
        for keyword in subject_keywords:
            if keyword in query:
                conditions['subject_keyword'] = keyword
                break
        
        # 교수명 추출 (교수 앞의 이름)
        prof_match = re.search(r'(\w+)\s*교수', query)
        if prof_match:
            conditions['professor'] = prof_match.group(1)
        
        return conditions
    
    def _build_sql_query(self, conditions: dict) -> tuple:
        """조건들을 바탕으로 SQL 쿼리를 동적으로 생성합니다."""
        base_query = """
        SELECT 
            course_code as 과목코드,
            course_name as 과목명,
            credits as 학점,
            course_type as 과목구분,
            department as 개설학과,
            professor as 교수,
            target_grade as 대상학년,
            note as 비고
        FROM courses
        WHERE 1=1
        """
        
        params = []
        
        # 학년 조건
        if conditions['grade']:
            base_query += " AND (target_grade = %s OR target_grade LIKE %s OR target_grade = '전체')"
            params.extend([conditions['grade'], f"%{conditions['grade']}%"])
        
        # 학과 조건
        if conditions['department']:
            base_query += " AND department LIKE %s"
            params.append(f"%{conditions['department']}%")
        
        # 과목 키워드 조건
        if conditions['subject_keyword']:
            base_query += " AND (course_name LIKE %s OR department LIKE %s)"
            params.extend([f"%{conditions['subject_keyword']}%", f"%{conditions['subject_keyword']}%"])
        
        # 교수 조건
        if conditions['professor']:
            base_query += " AND professor LIKE %s"
            params.append(f"%{conditions['professor']}%")
        
        base_query += " ORDER BY department, course_name"
        
        return base_query, params

    def _run(self, query: str) -> str:
        """Execute database query to get course information."""
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
            
            # 특별한 케이스들 먼저 처리
            if "다음 학기" in query or "다음학기" in query or "전체" in query or "모든" in query:
                sql_query = """
                SELECT 
                    course_code as 과목코드,
                    course_name as 과목명,
                    credits as 학점,
                    course_type as 과목구분,
                    department as 개설학과,
                    professor as 교수,
                    target_grade as 대상학년
                FROM courses
                ORDER BY department, course_name
                LIMIT 30
                """
                cursor.execute(sql_query)
                results = cursor.fetchall()
                
            elif query.strip().upper().startswith("SELECT"):
                # 직접 SQL 쿼리
                if "courses" in query.lower():
                    cursor.execute(query)
                    results = cursor.fetchall()
                else:
                    return "courses 테이블만 사용할 수 있습니다."
                    
            else:
                # 자연어 쿼리 파싱 및 동적 SQL 생성
                conditions = self._parse_query_conditions(query)
                
                # 조건이 하나도 없으면 안내 메시지
                if not any(conditions.values()):
                    return """
                    강의 검색 예시:
                    - '3학년 과목 중 한국역사학과 개설 강의 알려줘'
                    - '심리학 관련 강의 검색해줘'
                    - '김철수 교수의 강의를 알려줘'
                    - '소프트웨어학과 2학년 과목 알려줘'
                    - '컴퓨터 관련 강의 찾아줘'
                    - '다음 학기 개설 과목 알려줘'
                    """
                
                sql_query, params = self._build_sql_query(conditions)
                cursor.execute(sql_query, params)
                results = cursor.fetchall()
            
            if not results:
                return "조회된 강의가 없습니다."
            
            # 결과 포맷팅
            formatted_results = []
            for i, course in enumerate(results, 1):
                course_info = f"{i}. "
                course_info += f"[{course.get('과목코드', 'N/A')}] {course.get('과목명', 'N/A')}"
                if course.get('학점'):
                    course_info += f" ({course['학점']}학점)"
                if course.get('개설학과'):
                    course_info += f" - {course['개설학과']}"
                if course.get('교수'):
                    course_info += f" - {course['교수']} 교수"
                if course.get('대상학년'):
                    course_info += f" - {course['대상학년']}학년"
                formatted_results.append(course_info)
            
            return f"조회된 강의 ({len(results)}개):\n" + "\n".join(formatted_results)
            
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

# Create Agent with both tools
agent = Agent(
    role='학생 정보 및 강의 상담사',
    goal='학생 정보와 강의 정보를 정확하고 간결하게 제공하며, 불확실한 정보는 솔직하게 모른다고 답변합니다',
    backstory='''데이터베이스를 조회해서 정확한 정보만 제공하는 상담사입니다. 
    학생 정보 질문에는 StudentDBTool을, 강의/과목 관련 질문에는 CourseSearchTool을 사용합니다.
    학생의 정보가 주어지고, 강의/과목 관련 질문이 들어온다면, StudentDBTool에서 학생의 정보를 조회하고 강의/과목을 CourseSearchTool을 이용하여 개설된 과목을 찾아옵니다.
    인사말이나 자기소개는 하지 않고, "질문에 답해드릴게요" 정도의 간단한 멘트로 시작합니다.
    확실하지 않은 정보는 추측하지 않고 "잘 모르겠습니다"라고 솔직하게 답변합니다.
    모든 답변은 한국어로, 정중하면서도 간결하게 제공합니다.''',
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
        "2020년도 입학한 학생들 정보를 조회해주세요",
        "다인장 학생의 정보를 찾아주세요",
        "전체 학생 리스트를 보여주세요",
        "4학년 1학기 수업 중 국문학과 수업을 조회해주세요.",
        "체육과 관련된 교양 수업을 추천해주세요.",
        "언어와 관련된 비전공 수업을 찾아주세요.",
        "신입생이 들을 교양 과목을 보여주세요.",
        "다인장 학생이 다음 학기에 들을 적절한 과목을 찾아주세요."
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
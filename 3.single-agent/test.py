import os
import mysql.connector
from crewai import Agent, Crew, Task, Process, LLM
from crewai.tools import BaseTool
from dotenv import load_dotenv
from typing import Type
from pydantic import BaseModel, Field
from datetime import datetime

# Load environment variables
load_dotenv()

def get_current_semester_info():
    """현재 날짜를 기준으로 학기 정보를 반환합니다."""
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    current_day = now.day
    
    # 1학기: 3월 ~ 6월 20일
    # 2학기: 9월 ~ 12월 20일
    
    if (current_month == 3) or (current_month == 4) or (current_month == 5) or (current_month == 6 and current_day <= 20):
        # 현재 1학기
        current_semester = 1
        current_semester_year = current_year
        next_semester = 2
        next_semester_year = current_year
        prev_semester = 2
        prev_semester_year = current_year - 1
        
    elif (current_month == 9) or (current_month == 10) or (current_month == 11) or (current_month == 12 and current_day <= 20):
        # 현재 2학기
        current_semester = 2
        current_semester_year = current_year
        next_semester = 1
        next_semester_year = current_year + 1
        prev_semester = 1
        prev_semester_year = current_year
        
    elif current_month in [1, 2] or (current_month == 6 and current_day > 20) or current_month in [7, 8]:
        # 방학 기간
        if current_month in [1, 2] or (current_month == 6 and current_day > 20) or current_month in [7, 8]:
            if current_month in [1, 2]:
                # 겨울방학 (1-2월)
                current_semester = None
                next_semester = 1
                next_semester_year = current_year
                prev_semester = 2
                prev_semester_year = current_year - 1
            else:
                # 여름방학 (6월 21일 이후 ~ 8월)
                current_semester = None
                next_semester = 2
                next_semester_year = current_year
                prev_semester = 1
                prev_semester_year = current_year
    else:
        # 12월 21일 이후
        current_semester = None
        next_semester = 1
        next_semester_year = current_year + 1
        prev_semester = 2
        prev_semester_year = current_year
    
    return {
        'current_date': now.strftime('%Y년 %m월 %d일'),
        'current_semester': current_semester,
        'current_semester_year': current_semester_year if current_semester else None,
        'next_semester': next_semester,
        'next_semester_year': next_semester_year,
        'prev_semester': prev_semester,
        'prev_semester_year': prev_semester_year
    }

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
    인증된 본인의 학생 정보 조회 및 맞춤형 추천 도구입니다.
    개인정보 보호를 위해 본인 인증된 학생의 정보만 조회 가능합니다.
    
    주요 기능:
    1. 본인의 학적 정보 조회 (전공, 학년, 이수학기 등)
    2. 본인 조건에 맞는 강의 추천을 위한 기초 데이터 제공
    3. 비슷한 조건 학생들의 익명화된 통계 정보 제공
    
    사용법: "내 정보 조회", "나와 비슷한 학생들이 듣는 과목" 등
    """
    args_schema: Type[BaseModel] = StudentDBToolInput

    def _run(self, query: str) -> str:
        """Execute database query for authenticated student information."""
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
            
            # 현재 인증된 학생 (시뮬레이션용 - 실제로는 세션에서 가져옴)
            # 테스트를 위해 다인장 학생으로 설정
            authenticated_student = "다인장"
            
            # 자연어 쿼리 처리 - 개인정보 보호 준수
            if "내" in query and ("정보" in query or "학적" in query):
                # 본인 정보 조회
                sql_query = """
                SELECT 
                    s.name as 학생이름,
                    s.student_id as 학번,
                    s.completed_semester as 이수학기,
                    s.admission_year as 입학년도,
                    CASE 
                        WHEN m.major_name IS NOT NULL THEN 
                            CONCAT(COALESCE(m.college, ''), ' ', COALESCE(m.department, ''), ' ', m.major_name)
                        ELSE 
                            CONCAT(COALESCE(m.college, ''), ' ', COALESCE(m.department, ''))
                    END as 소속
                FROM students s
                LEFT JOIN major m ON s.major_code = m.major_code
                WHERE s.name = %s
                """
                cursor.execute(sql_query, (authenticated_student,))
                results = cursor.fetchall()
                
            elif "나와 비슷한" in query or "같은 조건" in query:
                # 본인과 비슷한 조건의 학생들 통계 (익명화)
                # 먼저 본인 정보 조회
                sql_query = """
                SELECT s.major_code, s.completed_semester, s.admission_year
                FROM students s
                WHERE s.name = %s
                """
                cursor.execute(sql_query, (authenticated_student,))
                my_info = cursor.fetchone()
                
                if my_info:
                    # 비슷한 조건의 학생 수 조회 (개인정보 제외)
                    sql_query = """
                    SELECT 
                        COUNT(*) as 학생수,
                        CASE 
                            WHEN m.major_name IS NOT NULL THEN 
                                CONCAT(COALESCE(m.college, ''), ' ', COALESCE(m.department, ''), ' ', m.major_name)
                            ELSE 
                                CONCAT(COALESCE(m.college, ''), ' ', COALESCE(m.department, ''))
                        END as 소속,
                        AVG(s.completed_semester) as 평균이수학기
                    FROM students s
                    LEFT JOIN major m ON s.major_code = m.major_code
                    WHERE s.major_code = %s AND s.admission_year = %s
                    GROUP BY s.major_code, m.college, m.department, m.major_name
                    """
                    cursor.execute(sql_query, (my_info['major_code'], my_info['admission_year']))
                    results = cursor.fetchall()
                else:
                    return "본인 정보를 찾을 수 없습니다."
                    
            elif "추천" in query or "수강" in query:
                # 본인 조건에 맞는 강의 추천을 위한 기초 정보 제공
                sql_query = """
                SELECT 
                    s.completed_semester,
                    s.admission_year,
                    m.college,
                    m.department,
                    m.major_name
                FROM students s
                LEFT JOIN major m ON s.major_code = m.major_code
                WHERE s.name = %s
                """
                cursor.execute(sql_query, (authenticated_student,))
                results = cursor.fetchall()
                
                if results:
                    student_info = results[0]
                    current_grade = (student_info['completed_semester'] + 1) // 2  # 대략적인 학년 계산
                    return f"""
                    강의 추천을 위한 회원님의 기본 정보:
                    - 현재 학기: {student_info['completed_semester']}학기 (약 {current_grade}학년)
                    - 소속: {student_info['college']} {student_info['department']}
                    - 입학년도: {student_info['admission_year']}년
                    
                    이 정보를 바탕으로 CourseSearchTool을 통해 적합한 강의를 검색해드릴 수 있습니다.
                    """
            
            else:
                return """
                개인정보 보호를 위해 본인 인증된 정보만 조회 가능합니다.
                
                사용 가능한 명령어:
                - '내 정보 조회해주세요' - 본인의 학적 정보 확인
                - '나와 비슷한 학생들 정보' - 같은 조건 학생들의 익명화된 통계
                - '강의 추천을 위한 내 정보' - 맞춤형 강의 추천을 위한 기초 정보
                
                다른 학생의 개인정보는 개인정보보호법에 따라 조회할 수 없습니다.
                """
            
            if not results:
                return "조회된 데이터가 없습니다."
            
            # 결과 포맷팅
            if len(results) == 1:
                # 단일 정보 상세 표시
                info = results[0]
                formatted_result = "=== 조회 결과 ===\n"
                for key, value in info.items():
                    if value is not None:
                        formatted_result += f"{key}: {value}\n"
                return formatted_result
            else:
                # 통계 정보 표시
                formatted_results = []
                for i, row in enumerate(results, 1):
                    formatted_results.append(f"{i}. {dict(row)}")
                return "통계 결과:\n" + "\n".join(formatted_results)
            
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
            
            # 현재 날짜 기반 학기 정보 가져오기
            semester_info = get_current_semester_info()
            
            # 특별한 케이스들 먼저 처리
            if "다음 학기" in query or "다음학기" in query:
                # 다음 학기 정보를 쿼리에 포함
                next_semester = semester_info['next_semester']
                next_year = semester_info['next_semester_year']
                
                sql_query = """
                SELECT 
                    course_code as 과목코드,
                    course_name as 과목명,
                    credits as 학점,
                    course_type as 과목구분,
                    department as 개설학과,
                    professor as 교수,
                    target_grade as 대상학년,
                    offered_year as 개설년도,
                    offered_semester as 개설학기
                FROM courses
                WHERE offered_year = %s AND offered_semester = %s
                ORDER BY department, course_name
                LIMIT 30
                """
                cursor.execute(sql_query, (next_year, next_semester))
                results = cursor.fetchall()
                
                # 결과에 학기 정보 추가
                semester_context = f"\n📅 현재 날짜: {semester_info['current_date']}\n📚 다음 학기: {next_year}년 {next_semester}학기\n\n"
                
            elif "지난 학기" in query or "이전 학기" in query:
                # 지난 학기 정보를 쿼리에 포함
                prev_semester = semester_info['prev_semester']
                prev_year = semester_info['prev_semester_year']
                
                sql_query = """
                SELECT 
                    course_code as 과목코드,
                    course_name as 과목명,
                    credits as 학점,
                    course_type as 과목구분,
                    department as 개설학과,
                    professor as 교수,
                    target_grade as 대상학년,
                    offered_year as 개설년도,
                    offered_semester as 개설학기
                FROM courses
                WHERE offered_year = %s AND offered_semester = %s
                ORDER BY department, course_name
                LIMIT 30
                """
                cursor.execute(sql_query, (prev_year, prev_semester))
                results = cursor.fetchall()
                
                # 결과에 학기 정보 추가
                semester_context = f"\n📅 현재 날짜: {semester_info['current_date']}\n📚 지난 학기: {prev_year}년 {prev_semester}학기\n\n"
                
            elif "이번 학기" in query or "현재 학기" in query:
                # 현재 학기 정보를 쿼리에 포함
                if semester_info['current_semester']:
                    current_semester = semester_info['current_semester']
                    current_year = semester_info['current_semester_year']
                    
                    sql_query = """
                    SELECT 
                        course_code as 과목코드,
                        course_name as 과목명,
                        credits as 학점,
                        course_type as 과목구분,
                        department as 개설학과,
                        professor as 교수,
                        target_grade as 대상학년,
                        offered_year as 개설년도,
                        offered_semester as 개설학기
                    FROM courses
                    WHERE offered_year = %s AND offered_semester = %s
                    ORDER BY department, course_name
                    LIMIT 30
                    """
                    cursor.execute(sql_query, (current_year, current_semester))
                    results = cursor.fetchall()
                    
                    semester_context = f"\n📅 현재 날짜: {semester_info['current_date']}\n📚 현재 학기: {current_year}년 {current_semester}학기\n\n"
                else:
                    return f"""
                    📅 현재 날짜: {semester_info['current_date']}
                    현재는 방학 기간입니다.
                    
                    📚 다음 학기: {semester_info['next_semester_year']}년 {semester_info['next_semester']}학기
                    📚 지난 학기: {semester_info['prev_semester_year']}년 {semester_info['prev_semester']}학기
                    
                    "다음 학기" 또는 "지난 학기" 강의를 검색해보세요.
                    """
                    
            elif "전체" in query or "모든" in query:
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
                semester_context = f"\n📅 현재 날짜: {semester_info['current_date']}\n\n"
                
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
            
            # 학기 정보가 있으면 포함해서 반환
            result_text = f"조회된 강의 ({len(results)}개):\n" + "\n".join(formatted_results)
            if 'semester_context' in locals():
                result_text = semester_context + result_text
            
            return result_text
            
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
    temperature=0.1,
    max_tokens=1000
)

# Create StudentDBTool instance
student_db_tool = StudentDBTool()

# Create CourseSearchTool instance
course_search_tool = CourseSearchTool()

# Create Agent with both tools
agent = Agent(
    role='학생 정보 및 강의 상담사',
    goal='데이터베이스 조회 결과만을 사용하여 정확한 정보를 제공하며, 절대로 추측하거나 임의의 정보를 생성하지 않습니다',
    backstory='''당신은 데이터베이스 조회 결과만을 사용하는 엄격한 상담사입니다.
    
    중요한 규칙:
    1. 반드시 도구(StudentDBTool 또는 CourseSearchTool)를 사용해서 데이터베이스를 조회해야 합니다
    2. 도구에서 반환된 결과만을 사용해서 답변합니다
    3. 절대로 추측하거나 학습된 지식을 사용해서 정보를 만들어내지 않습니다
    4. 도구 결과에 없는 정보는 "데이터베이스에서 확인할 수 없습니다"라고 답변합니다
    5. 학생 정보 질문 → StudentDBTool 사용
    6. 강의/과목 질문 → CourseSearchTool 사용
    
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
        "2020년도 입학한 학생들 정보를 조회해주세요",
        "내 정보를 찾아주세요",
        "4학년 1학기 수업 중 국문학과 수업을 조회해주세요.",
        # "체육과 관련된 교양 수업을 추천해주세요.",
        # "언어와 관련된 비전공 수업을 찾아주세요.",
        # "신입생이 들을 교양 과목을 보여주세요.",
        # "다인장 학생이 다음 학기에 들을 적절한 과목을 찾아주세요."
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
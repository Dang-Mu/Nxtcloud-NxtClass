import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_enrollment_data():
    """데이터베이스의 이수 과목 데이터를 확인합니다."""
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
        
        print("=== 학생 목록 확인 ===")
        cursor.execute("SELECT student_id, name FROM students LIMIT 10")
        students = cursor.fetchall()
        for student in students:
            print(f"학번: {student['student_id']}, 이름: {student['name']}")
        
        print("\n=== 이수 과목 데이터 확인 ===")
        cursor.execute("""
            SELECT s.name, s.student_id, COUNT(e.course_code) as 이수과목수
            FROM students s
            LEFT JOIN enrollments e ON s.student_id = e.student_id
            GROUP BY s.student_id, s.name
            ORDER BY 이수과목수 DESC
        """)
        enrollment_stats = cursor.fetchall()
        
        for stat in enrollment_stats:
            print(f"학생: {stat['name']} (학번: {stat['student_id']}) - 이수과목: {stat['이수과목수']}개")
        
        print("\n=== 다인장 학생의 이수 과목 확인 ===")
        cursor.execute("""
            SELECT e.course_code, c.course_name, e.grade, e.enrollment_semester
            FROM enrollments e
            LEFT JOIN courses c ON e.course_code = c.course_code
            LEFT JOIN students s ON e.student_id = s.student_id
            WHERE s.name = '다인장'
            ORDER BY e.enrollment_semester
        """)
        dain_courses = cursor.fetchall()
        
        if dain_courses:
            print("다인장 학생의 이수 과목:")
            for course in dain_courses:
                print(f"- {course['course_code']}: {course['course_name']} ({course['grade']}, {course['enrollment_semester']})")
        else:
            print("다인장 학생의 이수 과목 데이터가 없습니다!")
        
    except Exception as e:
        print(f"데이터베이스 오류: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_enrollment_data()
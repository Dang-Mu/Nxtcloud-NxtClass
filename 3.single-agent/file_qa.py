from main import process_user_query

if __name__ == "__main__":
    question = input("질문을 입력하세요: ").strip()
    if question:
        answer = process_user_query(question)
        print(f"답변: {answer}") 
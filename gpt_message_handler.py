from router_llm import app

def handle_response(content, user, message_id, content_type) -> str:
    print(content, user, message_id, content_type)
    query = {"question": content}
    response = app.invoke(query)
    answer = response.get("answer")
    answer = f"{response.get('next_step')}: {answer}"
    if not answer:
        return "Sorry, I couldn't find an answer to your question."
    return answer

if __name__ == "__main__":
    question = "do CRAG . How is the weather in Ankara. "
    res = handle_response(question, "user", "123", "text")
    print(res)
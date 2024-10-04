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
from router_llm import app
from vectordb import add_to_vectorstore

REMEMBER = True


def filter_chat(username, user_id, docs):
    res = [
        doc
        for doc in docs
        if (
            doc.metadata.get("source") == "chatbot"
            and doc.metadata.get("username") == username
            and doc.metadata.get("user_id") == user_id
        )
    ]

    strres = "\n\n".join(doc.page_content for doc in res)
    return strres


def handle_response(content, user, message_id, content_type) -> str:
    print(content, user, message_id, content_type)
    if REMEMBER:
        # imported here to update the retriever in memory every time
        from vectordb import retriever

        docs = retriever.invoke(content)
        username = user.username
        user_id = user.id
        user_dict = {"username": username, "id": user_id}
        chat_history = filter_chat(username, user_id, docs)
        query = {"question": f"chat_history: {chat_history} Question: {content} Ai:"}
        response = app.invoke(query)
        add_to_vectorstore(content, response.get("answer"), user_dict, retriever)
    else:
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

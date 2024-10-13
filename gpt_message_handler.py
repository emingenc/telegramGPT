from router import router
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
    route = router.route(content)
    
    if REMEMBER:
        # imported here to update the retriever in memory every time
        from vectordb import retriever

        docs = retriever.invoke(content)
        username = user.username
        user_id = user.id
        user_dict = {"username": username, "id": user_id}
        chat_history = filter_chat(username, user_id, docs)
        if chat_history:
            query = f"chat_history: {chat_history} Question: {content} Ai:"
        else:
            query =  content
        print(query)
        print("model::::", route.name)
        response =  route.invoker(query)
        add_to_vectorstore(content, response, user_dict, retriever)
    else:
        response = route.invoker(content)
    answer = response
    answer = f"{route.name}: {answer}"
    if not answer:
        return "Sorry, I couldn't find an answer to your question."
    return answer


if __name__ == "__main__":
    question = "do CRAG . How is the weather in Ankara. "
    res = handle_response(question, "user", "123", "text")
    print(res)

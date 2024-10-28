from router import router


async def handle_response(content, user, message_id, content_type) -> str:
    username = user.username
    user_id = user.id
    config = {
        "username": username,
        "user_id": user_id,
        "message_id": message_id,
        "content_type": content_type
    }
    route = router.route(content)
    response = await route.invoker(content, config)
    message = f"{route.name}:{response}"
    return message


if __name__ == "__main__":
    question = "do CRAG . How is the weather in Ankara. "
    res = handle_response(question, "user", "123", "text")
    print(res)

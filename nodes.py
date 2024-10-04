from services import conversational, retrieve


nodes = {
    "conversational": {
        "description": "Answer the question directly based on existing knowledge",
        "node": conversational,
    },
    "retriever": {
        "description": "Retrieve relevant documents from the vectorstore",
        "node": retrieve,
    },
}

options_str = "\n".join(
    [f"- {key}: {value['description']}" for key, value in nodes.items()]
)

from services import conversational, retrieve
from agents.crag import crag


nodes = {
    "conversational": {
        "description": "Answer the question directly based on existing knowledge",
        "node": conversational,
    },
    "retriever": {
        "description": "Retrieve relevant documents from the vectorstore",
        "node": retrieve,
    },
    "crag": {
        "description": "Run corerctive RAG pipeline to generate an answer. it uses decide if document is relevant or not if not it searches the web",
        "node": crag,
    },
}

options_str = "\n".join(
    [f"- {key}: {value['description']}" for key, value in nodes.items()]
)

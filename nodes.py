from services import conversational, retrieve
from agents.crag import crag


nodes = {
    "conversational": {
        "description": "Answer the question directly based on existing knowledge",
        "node": conversational,
    },
    "retriever": {
        "description": "Use this if user ask spesifically about whats in DB Retrieve relevant documents from the vectorstore",
        "node": retrieve,
    },
    "crag": {
        "description": "Run the CRAG pipeline to generate an answer. use main RAG pipeline as this. If you think you'll need web search use this",
        "node": crag,
    },
}

options_str = "\n".join(
    [f"- {key}: {value['description']}" for key, value in nodes.items()]
)

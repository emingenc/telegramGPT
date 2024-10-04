from services import retrieve, conversational_rag
from agents.crag import run_crag_pipeline


nodes = {
  
    "conversational_rag": {
        "description": "Answer the question directly based on existing knowledge. Use RAG pipeline",
        "node": conversational_rag,
    },
    "retriever": {
        "description": "Use this if user ask about whats in DB Retrieve relevant documents from the vectorstore",
        "node": retrieve,
    },
    "crag": {
        "description": """Run the CRAG pipeline to generate an answer. 
        use main RAG pipeline as this. This is main llm model. this should be selected
        If you think you'll need web search use this""",
        "node": run_crag_pipeline,
    },
}

options_str = "\n".join(
    [f"- {key}: {value['description']}" for key, value in nodes.items()]
)

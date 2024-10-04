from services import conversational, retrieve
from agents.crag import run_crag_pipeline


nodes = {
    "conversational": {
        "description": (
            "Select this option if the user's question can be answered directly using the model's built-in knowledge, "
            "without needing to retrieve external documents or perform web searches. Use this for general knowledge questions, "
            "definitions, explanations, or casual conversations.\n\n"
            "**Examples:**\n"
            "- \"What is the capital of France?\"\n"
            "- \"Explain the theory of relativity.\"\n"
            "- \"Tell me a joke.\""
        ),
        "node": conversational,
    },

    "retriever": {
        "description": (
            "Select this option if the user is asking about specific information stored in the database or vectorstore. "
            "Use this when the answer requires retrieving information from existing documents or data sources.\n\n"
            "**Examples:**\n"
            "- \"What are the details of order #12345?\"\n"
            "- \"Show me the latest sales report.\"\n"
            "- \"Retrieve the document titled 'Project Plan Q4.'\""
        ),
        "node": retrieve,
    },

    "crag": {
        "description": (
            "Select this option if the user's question requires up-to-date information, complex reasoning, or web search to generate an accurate answer. "
            "Use the CRAG pipeline when the question cannot be fully answered with internal knowledge or existing documents.\n\n"
            "**Examples:**\n"
            "- \"What's the weather forecast for tomorrow in New York City?\"\n"
            "- \"Who won the Nobel Prize in Literature this year?\"\n"
            "- \"Summarize the latest news on renewable energy advancements.\""
        ),
        "node": run_crag_pipeline,
    },
}

options_str = "\n".join(
    [f"- {key}: {value['description']}" for key, value in nodes.items()]
)

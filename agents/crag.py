import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# Import LangChain components
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import Document
from langgraph.graph import StateGraph, START, END
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from vectordb import retriever, add_to_vectorstore
from conf import llm, web_search_tool


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Grading prompt
grading_system_prompt = """.You are a grader assessing relevance of a retrieved document to a user question.
If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant.
Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question."""

grade_prompt_template = ChatPromptTemplate.from_messages([
    ("system", grading_system_prompt),
    ("user", "Retrieved document:\n\n{document}\n\nUser question: {question}")
])

retrieval_grader_chain = grade_prompt_template | llm |  StrOutputParser()



# Post-processing
def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

# State Graph
class GraphState(TypedDict):
    """Represents the state of our graph."""
    question: str
    generation: str
    web_search: str
    documents: List[Document]

# Initialize memory
memory = ConversationBufferMemory(return_messages=True)


def retrieve(state: GraphState) -> Dict[str, Any]:
    """Retrieve documents."""
    logger.info("Retrieving documents...")
    question = state["question"]
    documents = retriever.get_relevant_documents(question)
    return {"documents": documents, "question": question}

def grade_documents(state: GraphState) -> Dict[str, Any]:
    """Grade retrieved documents for relevance."""
    logger.info("Grading documents for relevance...")
    question = state["question"]
    documents = state.get("documents", [])
    filtered_docs = []
    web_search_needed = False
    for doc in documents:
        result = retrieval_grader_chain.invoke({"document": doc.page_content, "question": question})
        grade = result.strip().lower()
        if "yes" in grade:
            filtered_docs.append(doc)
        else:
            web_search_needed = True
    return {"documents": filtered_docs, "question": question, "web_search": "Yes" if web_search_needed else "No"}

def transform_query(state: GraphState) -> Dict[str, Any]:
    """Transform the query to produce a better question."""
    logger.info("Transforming query...")
    question = state["question"]
    # Implement a query transformer if needed (e.g., using another LLM)
    # For now, we return the original question
    return {"question": question, "documents": state["documents"]}

def web_search(state: GraphState) -> Dict[str, Any]:
    """Perform web search based on the question."""
    logger.info("Performing web search...")
    question = state["question"]
    documents = state["documents"]
    # Perform web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)
    documents.append(web_results)
    return {"documents": documents, "question": question}

def generate(state: GraphState) -> Dict[str, Any]:
    logger.info("Generating answer with RAG...")
    question = state["question"]
    documents = state["documents"]
    
    context = format_docs(documents)
    # Main prompt for RAG generation
    rag_prompt_template = PromptTemplate(
        template=(
        "You are an AI assistant answering questions based on the following context and chat history.\n"
        "Context: {context}\n"
        "Human: {question}\n"
        "AI: "
    ),
        input_variables=["context", "question"])

    rag_chain = rag_prompt_template | llm | StrOutputParser()
    query = {"context": context, "question": question}
    generation = rag_chain.invoke(query)
    return {"generation": generation}


def decide_to_generate(state: GraphState) -> str:
    """Decide whether to generate an answer or transform the query."""
    logger.info("Deciding next step...")
    web_search = state.get("web_search", "No")
    if web_search == "Yes":
        return "transform_query"
    else:
        return "generate"

# Workflow
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("transform_query", transform_query)
workflow.add_node("web_search_node", web_search)
workflow.add_node("generate", generate)

# Build graph
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "web_search_node")
workflow.add_edge("web_search_node", "generate")
workflow.add_edge("generate", END)

# Compile
crag = workflow.compile()


# Main function to run the app
def run_pipeline(question: str) -> str:
    """Run the RAG pipeline with the given question and chat history."""
    state = {"question": question}
    result = crag.invoke(state)
    answer = result.get("generation", "")
    
    # Add the question and answer to vectorstore for future retrieval
    add_to_vectorstore(question, answer, retriever)
    
    return answer

# Example usage
if __name__ == "__main__":
    chat_history = []
    while True:
        question = input("Human: ")
        if question.lower() == "exit":
            break
        answer = run_pipeline(question)
        print("AI:", answer)
import logging
from typing import List, Dict, Any
from typing_extensions import TypedDict

# Import LangChain components
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import Document
from langgraph.graph import StateGraph, START, END
from langchain.memory import ConversationBufferMemory


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from vectordb import retriever, add_docs_to_vectorstore
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
    answer: str
    web_search: str
    documents: List[Document]
    search_attempts: int  # Add this to track search attempts

# Initialize memory
memory = ConversationBufferMemory(return_messages=True)



def retrieve(state: GraphState) -> Dict[str, Any]:
    """Retrieve documents."""
    logger.info("Retrieving documents...")
    question = state["question"]
    documents = retriever.invoke(question)
    state["documents"] = documents
    
    return state

def grade_documents(state: GraphState) -> Dict[str, Any]:
    """Grade retrieved documents for relevance."""
    logger.info("Grading documents for relevance...")
    question = state["question"]
    documents = state.get("documents", [])
    filtered_docs = []
    relevant_count = 0
    for doc in documents:
        result = retrieval_grader_chain.invoke({"document": doc.page_content, "question": question})
        grade = result.strip().lower()
        if "yes" in grade:
            filtered_docs.append(doc)
            relevant_count += 1
    
    web_search_needed = relevant_count < 2  # Require at least 2 relevant documents
    state["documents"] = filtered_docs
    state["web_search"] = "Yes" if web_search_needed else "No"
    state["search_attempts"] = state.get("search_attempts", 0)
    return state

def transform_query(state: GraphState) -> Dict[str, Any]:
    """Transform the query to produce a better question."""
    logger.info("Transforming query...")
    question = state["question"]
    prompt_template = "Transform the user's question to improve search results."
    parser = StrOutputParser()
    transform_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_template),
        ("user", question)
    ])
    chain = transform_prompt | llm | parser
    result = chain.invoke({"question": question})
    state["question"] = result
    
    return state

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
    add_docs_to_vectorstore([web_results], retriever)
    state["documents"] = documents
    state["search_attempts"] = state.get("search_attempts", 0) + 1
    return state

def generate(state: GraphState) -> Dict[str, Any]:
    logger.info("Generating final answer with RAG...")
    documents = state["documents"]
    question = state["question"]
    context = format_docs(documents)
    prompt_template = "Generate an answer to the question with this Context: {context}"
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_template),
        ("user", question)
    ])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": question, "context": context})
    state["answer"] = result
    return state
    

def decide_next_step(state: GraphState) -> str:
    """Decide whether to generate an answer, transform the query, or end the process."""
    logger.info("Deciding next step...")
    web_search = state.get("web_search", "No")
    search_attempts = state.get("search_attempts", 0)
    
    if web_search == "Yes" and search_attempts < 2:  # Limit to 2 search attempts
        return "transform_query"
    elif len(state.get("documents", [])) > 0:
        return "generate"
    else:
        return "end"  # Add an "end" condition if no relevant documents are found after attempts

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
    decide_next_step,
    {
        "transform_query": "transform_query",
        "generate": "generate",
        "end": END
    },
)
workflow.add_edge("transform_query", "web_search_node")
workflow.add_edge("web_search_node", "grade_documents")
workflow.add_edge("generate", END)

# Compile
crag = workflow.compile()


# Main function to run the app
def run_pipeline(query: dict) -> str:
    """Run the RAG pipeline with the given question and chat history."""
    result = crag.invoke(query)
    return result.get("answer", "Sorry, I couldn't find an answer to your question.")

# Example usage
if __name__ == "__main__":
    chat_history = []
    question = "How is the weather in New York?"
    query = {"question": question}
    answer = run_pipeline(query)
    print("AI:", answer)
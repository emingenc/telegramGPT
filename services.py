from state import GraphState
from conf import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vectordb import retriever


# Node functions
def conversational(state: GraphState) -> GraphState:
    prompt_template = """
    You are expert in social sciences. And you are master at chatting with people.
    human: {question}
    AI:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["question"])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": state.question})
    state.answer = response
    return state


def retrieve(state: GraphState) -> GraphState:
    docs = retriever.invoke(state.question)
    print(docs)
    if not docs:
        state.answer = "Sorry, I couldn't find any relevant documents."
    docsstr = "\n\n".join(doc.page_content for doc in docs)
    rag_prompt_template = """
    Search results for: {question}
    {docs}
    answer:
    """
    
    rag_prompt = PromptTemplate(template=rag_prompt_template, input_variables=["question", "docs"])
    chain = rag_prompt | llm | StrOutputParser()
    response = chain.invoke({"question": state.question, "docs": docsstr})
    state.answer = response
    return state


def clarify(state: GraphState) -> GraphState:
    state.chat_history.append(f"Asked for clarification: {state.question}")
    return state


def math(state: GraphState) -> GraphState:
    state.chat_history.append(f"Performed calculation for: {state.question}")
    return state

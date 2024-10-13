from conf import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vectordb import retriever


def conversational(content) -> str:
    prompt_template = """
    You are expert in social sciences. And you are master at chatting with people.
    human: {question}
    AI:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["question"])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": content})
    return response



def retrieve(content) -> str:
    docs = retriever.invoke(content)
    if not docs:
        return "Sorry, I couldn't find any relevant documents."
    docsstr = "\n\n".join(doc.page_content for doc in docs)
    rag_prompt_template = """
    Search results for: {question}
    {docs}
    answer:
    """
    
    rag_prompt = PromptTemplate(template=rag_prompt_template, input_variables=["question", "docs"])
    chain = rag_prompt | llm | StrOutputParser()
    response = chain.invoke({"question": content, "docs": docsstr})
    return response


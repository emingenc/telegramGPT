import uuid
from conf import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vectordb import retriever
from agents.memory_agent.graph import builder
from agents.crag import crag
from agents.gpt_researcher.multi_agents.agents import ChiefEditorAgent
from agents.gpt_researcher.gpt_researcher.utils.enum import Tone

from langgraph.store.memory import InMemoryStore


mem_store = InMemoryStore()


async def conversational(content, config={}) -> str:
    graph = builder.compile(store=mem_store)
    config = {
        "configurable": {},
        "user_id": str(config.get("user_id")),
    }

    response = await graph.ainvoke(
        {"messages": [("user", content)]},
        {**config, "thread_id": "thread"},
    )
    messages = response.get("messages", [])
    last_message = messages[-1] if messages else None
    content = last_message.content if last_message else None
    return content


async def retrieve(content, config={}) -> str:
    docs = retriever.invoke(content)
    if not docs:
        return "Sorry, I couldn't find any relevant documents."
    docsstr = "\n\n".join(doc.page_content for doc in docs)
    rag_prompt_template = """
    Search results for: {question}
    {docs}
    answer:
    """

    rag_prompt = PromptTemplate(
        template=rag_prompt_template, input_variables=["question", "docs"]
    )
    chain = rag_prompt | llm | StrOutputParser()
    response = await chain.invoke({"question": content, "docs": docsstr})
    return response


async def run_crag_pipeline(query: str, config={}) -> str:
    """Run the RAG pipeline with the given question and chat history."""
    query = {"question": query}
    result = await crag.invoke(query)
    answer = result.get("answer", "Sorry, I couldn't find an answer to your question.")
    return answer


async def run_research(query: str, config={}) -> str:
    """Run the research pipeline with the given question."""
    task = {
        "query": query,
        "max_sections": 3,
        "publish_formats": {
            "markdown": True,
        },
        "follow_guidelines": False,
        "model": "gpt-4o",
        "guidelines": [
            "The report MUST be written in APA format",
        ],
        "verbose": False,
    }

    tone = Tone.Objective

    chief_editor = ChiefEditorAgent(task, tone=tone)
    task_id = uuid.uuid4()
    research =await chief_editor.run_research_task(task_id=task_id)
    research_report = research.get("report",f"P{task_id}:{query} research report is ready.")
    
    return research_report

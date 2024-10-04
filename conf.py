from langchain.embeddings.base import Embeddings
from langchain.llms.base import BaseLLM
from langchain.tools.base import BaseTool


users = ["your username here"]


def get_llm() -> BaseLLM:
    """Function to get the LLM. Replace with your desired LLM."""
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

def get_embeddings() -> Embeddings:
    """Function to get the embeddings model. Replace with your desired embeddings."""
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings()

def get_web_search_tool() -> BaseTool:
    """Function to get the web search tool. Replace with your implementation."""
    from langchain_community.tools.tavily_search.tool import TavilySearchResults
    return TavilySearchResults(k=3)

# Initialize components
llm = get_llm()
embeddings = get_embeddings()
web_search_tool = get_web_search_tool()
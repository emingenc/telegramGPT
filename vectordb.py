import os
import logging
from typing import List, Dict
from datetime import datetime

# Import LangChain components
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata

from dotenv import load_dotenv
from conf import embeddings

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
VECTOR_DB_PATH = "./vectorstore_db"
COLLECTION_NAME = "rag-chroma"
BOTNAME = os.getenv("BOTNAME", "RAG Bot")


def initialize_vectorstore(docs: List[Document]) -> Chroma:
    """Initialize or load the vectorstore and add new documents if necessary."""
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=VECTOR_DB_PATH,
    )
    if docs:
        vector_store.add_documents(docs)

    logger.info("Vector store initialized successfully.")

    retriever = vector_store.as_retriever(
<<<<<<< HEAD
        search_type="mmr", search_kwargs={"k": 3, "fetch_k": 5}
=======
        search_type="mmr", search_kwargs={"k": 3, "fetch_k": 10}
>>>>>>> 3df12e8 (add chat history)
    )
    retriever = vector_store.as_retriever(
    search_type="mmr", search_kwargs={"k": 1, "fetch_k": 5}
    )
    retriever.add_documents(docs)
  

    return retriever


# Prepare documents and vector store
def load_documents(urls: List[str]) -> List[Document]:
    """Load documents from given URLs."""
    docs = []
    for url in urls:
        loader = WebBaseLoader(url)
        docs.extend(loader.load())
    return docs


def split_documents(docs: List[Document]) -> List[Document]:
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )
    return text_splitter.split_documents(docs)


# Function to add results to vectorstore
def add_to_vectorstore(question: str, answer: str, user: Dict, retriever: Chroma):
    """Add question and answer to vectorstore with incremental learning."""
    try:
        logger.info("Adding question and answer to vectorstore...")

        logger.info(f"Question: {question}")
        logger.info(f"Answer: {answer}")

        qa_doc = Document(
            page_content=f"Q: {question}\nA: {answer}",
            metadata={
                "source": "chatbot",
                "created_at": datetime.now().isoformat(),
                "username": user.get("username"),
                "user_id": user.get("id"),
            },
        )
        filtered_docs = filter_complex_metadata([qa_doc])

        metadata = filtered_docs[0].metadata
        logger.info(f"Metadata: {metadata}")

        retriever.add_documents(filtered_docs)
        logger.info("Successfully added to vectorstore")
    except Exception as e:
        logger.error(f"Error adding to vectorstore: {str(e)}")


def add_docs_to_vectorstore(docs: List[Document], retriever: Chroma):
    """Add documents to vectorstore."""
    try:
        logger.info("Adding documents to vectorstore...")
        retriever.add_documents(docs)
        logger.info("Successfully added to vectorstore")
    except Exception as e:
        logger.error(f"Error adding to vectorstore: {str(e)}")


# Load and process documents
urls = [
    # "https://lilianweng.github.io/posts/2023-06-23-agent/",
    # "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    # "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]
if urls:
    docs = load_documents(urls)
    doc_splits = split_documents(docs)
    retriever = initialize_vectorstore(doc_splits)

retriever = initialize_vectorstore([])

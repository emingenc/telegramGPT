import os
import logging
from typing import List
from datetime import datetime

# Import LangChain components
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
VECTOR_DB_PATH = "vectorstore_db"
COLLECTION_NAME = "rag-faiss"
BOTNAME = os.getenv("BOTNAME", "RAG Bot")


def get_embeddings() -> Embeddings:
    """Function to get the embeddings model."""
    return OpenAIEmbeddings()


def initialize_vectorstore(docs: List[Document]) -> TimeWeightedVectorStoreRetriever:
    """Initialize or load the vectorstore with time-weighted retrieval."""
    embeddings = OpenAIEmbeddings()

    if os.path.exists(VECTOR_DB_PATH):
        try:
            vectorstore = FAISS.load_local(
                VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True
            )
        except ValueError:
            logger.warning(
                "Existing vectorstore couldn't be loaded. Creating a new one."
            )
            vectorstore = FAISS.from_documents(docs, embeddings)
            vectorstore.save_local(VECTOR_DB_PATH)
    else:
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(VECTOR_DB_PATH)

    retriever = TimeWeightedVectorStoreRetriever(
        vectorstore=vectorstore, decay_rate=0.05, k=5
    )

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
def add_to_vectorstore(
    question: str, answer: str, retriever: TimeWeightedVectorStoreRetriever
):
    """Add question and answer to vectorstore with incremental learning."""
    try:
        logger.info("Adding question and answer to vectorstore...")

        logger.info(f"Question: {question}")
        logger.info(f"Answer: {answer}")

        qa_doc = Document(
            page_content=f"Q: {question}\nA: {answer}",
            metadata={"source": "chatbot", "created_at": datetime.now().isoformat()},
        )
        filtered_docs = filter_complex_metadata([qa_doc])

        metadata = filtered_docs[0].metadata
        logger.info(f"Metadata: {metadata}")

        retriever.add_documents(filtered_docs)
        logger.info("Successfully added to vectorstore")
    except Exception as e:
        logger.error(f"Error adding to vectorstore: {str(e)}")


# Load and process documents
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]
docs = load_documents(urls)
doc_splits = split_documents(docs)
retriever = initialize_vectorstore(doc_splits)


from llm_adaptive_router import AdaptiveRouter, router_prompt_template
from langchain_community.vectorstores import Chroma
from conf import llm, embeddings
from routes import routes


COLLECTION_NAME ="router_vectorstore"
router_embeddings = embeddings
VECTOR_DB_PATH = "./router_vectorstore_db"


router_vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=router_embeddings,
        persist_directory=VECTOR_DB_PATH,
    )


router = AdaptiveRouter(
    vectorstore=router_vectorstore,
    llm=llm,
    embeddings=router_embeddings,
    prompt_template=router_prompt_template,
    routes=routes,
)
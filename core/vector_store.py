import re

from langchain_chroma import Chroma
from chromadb import PersistentClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHROMA_DIR = "vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )


def sanitize_collection_name(name: str):
    """
    Chroma collection names should contain only
    letters, numbers, underscores and hyphens.
    """

    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)

    if len(name) < 3:
        name += "_db"

    return name


def delete_collection(collection_name):

    client = PersistentClient(path=CHROMA_DIR)

    try:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except Exception:
        pass


def build_vector_store(transcript: str, collection_name: str):

    collection_name = sanitize_collection_name(collection_name)

    delete_collection(collection_name)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_text(transcript)

    docs = [
        Document(
            page_content=chunk,
            metadata={"chunk": i},
        )
        for i, chunk in enumerate(chunks)
    ]

    embeddings = get_embeddings()

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_DIR,
    )

    return vector_store


def load_vector_store(collection_name):

    collection_name = sanitize_collection_name(collection_name)

    embeddings = get_embeddings()

    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )


def get_retriever(vector_store, k=4):

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
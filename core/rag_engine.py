import os

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from core.vector_store import (
    build_vector_store,
    load_vector_store,
    get_retriever,
)


def get_llm():

    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
    )


def format_docs(docs):

    return "\n\n".join(doc.page_content for doc in docs)


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
        "system",
            """
                You are an expert meeting assistant.

                Answer ONLY using the transcript below.

                If the answer is unavailable, then:

                Generate text on the given transcript only        #### "I could not find this information in the meeting transcript."

            Transcript: {context}
""",
        ),
        ("human", "{question}"),
    ]
)


def build_rag_chain(transcript, collection_name):

    vector_store = build_vector_store(
        transcript,
        collection_name,
    )

    retriever = get_retriever(vector_store)

    llm = get_llm()

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | PROMPT
        | llm
        | StrOutputParser()
    )

    return rag_chain


def load_rag_chain(collection_name):

    vector_store = load_vector_store(collection_name)

    retriever = get_retriever(vector_store)

    llm = get_llm()

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | PROMPT
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question):

    answer = rag_chain.invoke(question) # here was issue
    return answer
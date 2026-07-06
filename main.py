import os
import uuid

from dotenv import load_dotenv

from utils.audio import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import (
    build_rag_chain,
    ask_question,
)

load_dotenv()


def run_pipeline(source: str, language: str = "english") -> dict:

    print("Starting AI Video Assistant...\n")

    # Step 1: Download/Extract Audio
    chunks = process_input(source)

    # Step 2: Speech-to-Text
    transcript = transcribe_all(chunks, language)

    print(f"\nTranscript Preview:\n{transcript[:300]}\n")

    # Step 3: Generate a unique collection name
    if os.path.exists(source):
        # Local video/audio file
        collection_name = os.path.splitext(
            os.path.basename(source)
        )[0]
    else:
        # YouTube URL
        collection_name = f"video_{uuid.uuid4().hex}"

    print(f"Collection Name : {collection_name}")

    # Step 4: Generate Insights
    title = generate_title(transcript)

    summary = summarize(transcript)

    action_items = extract_action_items(transcript)

    decisions = extract_key_decisions(transcript)

    questions = extract_questions(transcript)

    # Step 5: Build RAG Pipeline
    rag_chain = build_rag_chain(
        transcript,
        collection_name,
    )

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "collection_name": collection_name,
        "rag_chain": rag_chain,
    }


if __name__ == "__main__":

    source = input(
        "Enter YouTube URL or Local File Path: "
    ).strip()

    language = (
        input(
            "Language (english/hinglish): "
        ).strip()
        or "english"
    )

    result = run_pipeline(source, language)

    print("\n" + "=" * 70)
    print(f"📌 Title:\n{result['title']}")
    print("=" * 70)

    print(f"\n📋 Summary:\n{result['summary']}")

    print(f"\n✅ Action Items:\n{result['action_items']}")

    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")

    print(f"\n❓ Open Questions:\n{result['open_questions']}")

    print(
        f"\n📂 Collection Name: {result['collection_name']}"
    )

    print("=" * 70)

    rag_chain = result["rag_chain"]

    print("\n💬 Chat with your Video (type 'exit' to quit)\n")

    while True:

        question = input("You: ").strip()

        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break

        if not question:
            continue

        answer = ask_question(
            rag_chain,
            question,
        )

        print(f"\n🤖 Assistant: {answer}\n")
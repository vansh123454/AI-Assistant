import streamlit as st
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your core modules
from utils.audio import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
from main import run_pipeline

# Page Configuration
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (unchanged)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap');
    
    .main { background: linear-gradient(135deg, #0f172a 0%, #1e2937 100%); color: #e2e8f0; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e2937 100%); }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: #60a5fa; }
    
    .card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(148, 163, 184, 0.2);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    .stButton>button { border-radius: 12px; height: 48px; font-weight: 600; }
    
    .chat-message-user {
        background: linear-gradient(135deg, #4ade80, #22c55e);
        color: #1f2937;
        border-radius: 18px 18px 4px 18px;
        padding: 14px 18px;
        margin: 10px 0;
        max-width: 75%;
        align-self: flex-end;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .chat-message-assistant {
        background: #334155;
        color: #e2e8f0;
        border-radius: 18px 18px 18px 4px;
        padding: 14px 18px;
        margin: 10px 0;
        max-width: 75%;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/video-conference.png", width=80)
    st.title("🎥 AI Video Assistant")
    st.markdown("### Transform meetings into insights")
    st.markdown("---")
    
    st.subheader("📥 Input")
    input_type = st.radio("Source Type", ["YouTube URL", "Local Video/File"], horizontal=True)
    
    if input_type == "YouTube URL":
        source = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
    else:
        source = st.file_uploader("Upload Video/Audio", type=["mp4", "mp3", "wav", "m4a", "mov"])
        if source:
            with open(f"temp_{source.name}", "wb") as f:
                f.write(source.getbuffer())
            source = f"temp_{source.name}"
    
    language = st.selectbox("Language", ["english", "hinglish"], index=0)
    
    process_btn = st.button(
        "🚀 Process Video", 
        type="primary", 
        use_container_width=True,
        disabled=st.session_state.get("processing", False)
    )
    
    cancel_btn = st.button(
        "⛔ Cancel",
        type="secondary",
        use_container_width=True,
        disabled=not st.session_state.get("processing", False)
    )

# Main Content
st.title("AI Meeting Intelligence")
st.markdown("**Extract insights, action items, and chat with your content**")

# Session State Initialization
if "result" not in st.session_state:
    st.session_state.result = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "cancel_requested" not in st.session_state:
    st.session_state.cancel_requested = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Handle Cancel
if cancel_btn:
    st.session_state.cancel_requested = True
    st.warning("🛑 Cancellation requested... Stopping processing.")
    st.rerun()

# Process Button Logic
if process_btn and source and not st.session_state.processing:
    st.session_state.processing = True
    st.session_state.cancel_requested = False
    st.rerun()

# Actual Processing
if st.session_state.processing and source:
    with st.spinner("Processing your video... This may take a few minutes"):
        try:
            # Use the improved run_pipeline from main.py
            result = run_pipeline(source, language)
            st.session_state.result = result
            
            # Clear old chat when new video is processed
            st.session_state.chat_history = []  
            
            # Clean up temp file
            if input_type == "Local Video/File" and os.path.exists(source) and source.startswith("temp_"):
                os.remove(source)
                
            st.success("✅ Processing Complete!")
            
        except Exception as e:
            if st.session_state.cancel_requested:
                st.error("❌ Processing was cancelled.")
            else:
                st.error(f"Error: {str(e)}")
        finally:
            st.session_state.processing = False
            st.session_state.cancel_requested = False

# Display Results
if st.session_state.result:
    result = st.session_state.result
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class="card">
            <h2 style="margin:0">📌 {result['title']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary", "📝 Transcript", "✅ Action Items", "🔑 Decisions", "❓ Questions"
    ])
    
    with tab1:
        st.markdown('<div class="section-header"><h3>Executive Summary</h3></div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="card">{result['summary']}</div>""", unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="section-header"><h3>Full Transcript</h3></div>', unsafe_allow_html=True)
        with st.expander("View Complete Transcript", expanded=False):
            st.text_area("", result['transcript'], height=400)
    
    with tab3:
        st.markdown('<div class="section-header"><h3>Action Items</h3></div>', unsafe_allow_html=True)
        actions = result['action_items'].split("\n") if isinstance(result['action_items'], str) else result['action_items']
        for action in actions:
            if action.strip():
                st.markdown(f"✅ {action}")
    
    with tab4:
        st.markdown('<div class="section-header"><h3>Key Decisions</h3></div>', unsafe_allow_html=True)
        decisions = result['key_decisions'].split("\n") if isinstance(result['key_decisions'], str) else result['key_decisions']
        for dec in decisions:
            if dec.strip():
                st.markdown(f"🔑 {dec}")
    
    with tab5:
        st.markdown('<div class="section-header"><h3>Open Questions</h3></div>', unsafe_allow_html=True)
        questions = result['open_questions'].split("\n") if isinstance(result['open_questions'], str) else result['open_questions']
        for q in questions:
            if q.strip():
                st.markdown(f"❓ {q}")
    
    # ====================== CHAT INTERFACE ======================
    st.markdown("---")
    st.markdown(f"**💬 Chatting with:** {result.get('title', 'Current Meeting')}")
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""<div style="display: flex; justify-content: flex-end;">
                <div class="chat-message-user">{message['content']}</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div style="display: flex; justify-content: flex-start;">
                <div class="chat-message-assistant"><strong>🤖 Assistant:</strong><br>{message['content']}</div></div>""", unsafe_allow_html=True)
    
    if prompt := st.chat_input("Ask a question about the recent transcript..."):
        if st.session_state.result is None or "rag_chain" not in st.session_state.result:
            st.error("⚠️ Please process a video first before chatting.")
        else:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.spinner("Thinking based on recent transcript..."):
                try:
                    answer = ask_question(st.session_state.result["rag_chain"], prompt)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Chat error: {str(e)}")
            st.rerun()
    # ============================================================

else:
    # Welcome Screen
    st.markdown("""<div style="text-align: center; padding: 60px 20px; background: rgba(30,41,59,0.6); border-radius: 20px; margin: 40px 0;">
        <h1 style="font-size: 3rem; margin-bottom: 16px;">🎥 Welcome to AI Video Assistant</h1>
        <p style="font-size: 1.3rem; color: #94a3b8; max-width: 600px; margin: 0 auto;">
            Transform any meeting recording into structured insights, action items, and intelligent conversation
        </p>
    </div>""", unsafe_allow_html=True)
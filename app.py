import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

# Load API key from .env
load_dotenv(Path(__file__).resolve().parent / ".env")

# Page settings
st.set_page_config(
    page_title="CodeBuddy AI",
    page_icon="💻",
    layout="centered"
)

# Connect to Groq
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-20b"

# Custom design
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101426, #171b30);
    color: #ffffff;
}
h1 {
    color: #8b9cff;
}
[data-testid="stChatMessage"] {
    background-color: #222840;
    border-radius: 14px;
    padding: 12px;
}
.stChatInput textarea {
    background-color: #222840;
}
</style>
""", unsafe_allow_html=True)

# Coding assistant instructions
SYSTEM_PROMPT = """
You are CodeBuddy, a friendly expert coding assistant.

Your goals:
- Help users write, understand, debug, and improve code.
- Support Python, JavaScript, HTML, CSS, Scratch concepts,
  and other programming languages.
- Give complete, runnable examples when appropriate.
- Use Markdown code blocks with the correct language.
- Explain important code step by step in beginner-friendly language.
- When debugging, identify the likely cause and show the fix.
- Ask for the error message or relevant code if necessary.
- Never claim code has been tested or executed when it has not.
- Explain security risks and encourage safe coding practices.
- Be patient, encouraging, and accurate.
"""

# Sidebar
with st.sidebar:
    st.title("⚙️ Workspace")

    language = st.selectbox(
        "Programming language",
        ["Auto-detect", "Python", "JavaScript", "HTML/CSS",
         "C++", "Java", "Scratch"]
    )

    mode = st.selectbox(
        "What do you need help with?",
        [
            "General coding",
            "Write code",
            "Debug an error",
            "Explain code",
            "Improve my code",
            "Learn programming"
        ]
    )

    if st.button("🗑️ New conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Powered by Python, Streamlit and Groq")

# Conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("💻 CodeBuddy AI")
st.write("Your personal coding partner. Build, debug and learn.")

# Starter suggestions
if not st.session_state.messages:
    st.markdown("### What are we coding today?")
    col1, col2 = st.columns(2)

    if col1.button("🐍 Learn Python", use_container_width=True):
        st.session_state.pending_prompt = (
            "Teach me Python from the beginning with examples."
        )

    if col2.button("🐛 Fix a bug", use_container_width=True):
        st.session_state.pending_prompt = (
            "Help me debug my code. Ask me to share my code and error."
        )

    if col1.button("🌐 Build a website", use_container_width=True):
        st.session_state.pending_prompt = (
            "Help me build a simple website using HTML, CSS and JavaScript."
        )

    if col2.button("🧠 Explain code", use_container_width=True):
        st.session_state.pending_prompt = (
            "Ask me to paste some code, then explain it line by line."
        )

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input from suggestions or chat box
prompt = st.chat_input("Ask CodeBuddy anything about coding...")

if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

# Process question
if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    extra_instructions = f"""
    Selected programming language: {language}
    Selected task: {mode}

    Adapt your answer to these preferences when relevant.
    If the user provides code in another language, help with that code too.
    """

    api_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n" + extra_instructions
        }
    ] + st.session_state.messages

    with st.chat_message("assistant"):
        with st.spinner("CodeBuddy is thinking..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=api_messages,
                    temperature=0.3
                )

                answer = response.choices[0].message.content
                if not answer:
                    answer = "I couldn't generate a response. Please try again."

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.info(
                    "Check your internet connection, Groq API key, "
                    "and model name in app.py."
                )
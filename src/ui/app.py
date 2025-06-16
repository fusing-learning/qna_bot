import streamlit as st
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.core.rag_engine import main as rag_main
import os
from src.core.config import settings

# Set page config
st.set_page_config(
    page_title="QnA Bot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def display_chat_message(role: str, content: str):
    """Display a chat message with appropriate styling."""
    with st.chat_message(role):
        st.markdown(content)

def main():
    st.title("🤖 QnA Bot")
    st.markdown("""
    Welcome to the QnA Bot! Ask questions about your documents, and I'll help you find the answers.
    
    The bot uses advanced AI to:
    - Search through your documents
    - Find relevant information
    - Provide clear, well-cited answers
    """)
    
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message["role"], message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_chat_message("user", prompt)
        
        # Get bot response
        with st.spinner("Thinking..."):
            response = rag_main(prompt)
            
            if response["status"] == "success":
                # Add bot response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"]
                })
                display_chat_message("assistant", response["answer"])
            else:
                error_message = f"Error: {response['answer']}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
                display_chat_message("assistant", error_message)

if __name__ == "__main__":
    main() 
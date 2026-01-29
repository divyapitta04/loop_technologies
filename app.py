import streamlit as st
import pandas as pd
from src.data_loader import (
    run_console_chatbot,
    check_ollama_running,
    holdings_df,
    trades_df
)

# Page config
st.set_page_config(
    page_title="Fund Analytics Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context_data" not in st.session_state:
    st.session_state.context_data = {}

# Title and Header
st.title("🤖 Fund Analytics Chatbot")
st.markdown("---")

# Ollama Status Check
ollama_status = check_ollama_running()

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if ollama_status:
        st.success("✅ Ollama is running and ready!")
    else:
        st.error("❌ Ollama is not running!")

with col3:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.context_data = {}
        st.rerun()

# Display warning if Ollama not running
if not ollama_status:
    st.warning("""
    **To start Ollama:**
    1. Install from https://ollama.ai
    2. Run: `ollama pull mistral`
    3. Run: `ollama serve`
    4. Refresh this page
    """)
    st.stop()

# Main chat interface
st.subheader("💬 Conversation")

# Chat container for messages
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# User input
user_input = st.chat_input("Ask me about funds, trades, holdings, performance, etc.")

if user_input:
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)
    
    # Get chatbot response
    with st.spinner("🔄 Processing your question..."):
        response = run_console_chatbot(user_input, trades_df, holdings_df)
    
    # Add bot message to session state
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Display bot message
    with chat_container:
        if response:
            with st.chat_message("assistant"):
                st.write(response)
        else:
            with st.chat_message("assistant"):
                st.write("Sorry can not find the answer")

# Sidebar
with st.sidebar:
    st.subheader("📊 Information")
    
    # Session info
    st.metric("Total Messages", len(st.session_state.messages))
    st.metric("Conversation Turns", len(st.session_state.messages) // 2)
    

    
    st.divider()
    
    # Quick tips
    st.subheader("💡 Quick Tips")
    st.write("""
    Try asking:
    - "Show me top 5 holdings"
    - "What's the total number of trades?"
    - "Compare all funds by market value"
    - "Get yearly performance"
    - "Show holdings by security type"
    """)
    
    st.divider()
    
    # Cached data
    if st.session_state.context_data:
        st.subheader("📁 Cached Data")
        for key, value in st.session_state.context_data.items():
            with st.expander(f"{key}"):
                if isinstance(value, (dict, list)):
                    st.json(value)
                else:
                    st.write(value)
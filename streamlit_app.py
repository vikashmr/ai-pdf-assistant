import streamlit as st
import requests

st.set_page_config(page_title="RAG AI Assistant")
st.title("📄 Chat with your PDF")

# --- 1. FILE UPLOAD SECTION ---
uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf", "txt"])

if uploaded_file:
    if st.button("Upload and Process"):
        with st.spinner("Processing document..."):
            # Prepare the file for the backend
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            
            try:
                response = requests.post("http://127.0.0.1:8000/upload-and-index", files=files)
                if response.status_code == 200:
                    st.success("✅ Document processed successfully!")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

st.divider()

# --- 2. CHAT SECTION ---
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about the PDF..."):
    # Show user message immediately
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call Backend
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # THIS IS THE FIX: Sending strictly formatted JSON
            payload = {"query": prompt}
            response = requests.post("http://127.0.0.1:8000/query", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                answer = data["answer"]
                sources = data.get("sources", {})
                
                # Display Answer
                message_placeholder.markdown(answer)
                
                # Display Source Metadata (The "Professional" touch)
                if sources:
                    with st.expander("🔎 View Source Context"):
                        st.json(sources)
                
                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                message_placeholder.error(f"Server Error: {response.text}")
                
        except Exception as e:
            message_placeholder.error(f"Connection Error: {e}")

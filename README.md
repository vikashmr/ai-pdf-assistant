# AI Document Assistant (RAG)

Ask questions about your own PDF and text files and get answers with the source passages they came from.

## How it works
1. Reads PDFs/text files and splits them into overlapping chunks
2. Creates embeddings (OpenAI text-embedding-3-small) and stores them in ChromaDB
3. For each question, finds the most relevant chunks and lets GPT-4o answer using only those, with sources

## Tech
Python, FastAPI, Streamlit, OpenAI, ChromaDB, Docker

## Run
pip install -r requirements.txt
export OPENAI_API_KEY=...
streamlit run streamlit_app.py

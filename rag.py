import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from pypdf import PdfReader  # <--- NEW: Tool to read PDFs

# --- 1. SETUP ---
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="chroma_db")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)
collection = chroma_client.get_or_create_collection(
    name="documents",
    embedding_function=openai_ef
)

# --- 2. HELPER: EXTRACT TEXT ---
def get_text_from_file(file_path):
    """
    Smart function: Detects if it's a PDF or a Text file
    and reads it correctly.
    """
    if file_path.endswith(".pdf"):
        # Read as PDF
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    else:
        # Read as plain text
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

# --- 3. HELPER: CHUNKING ---
def chunk_text(text, chunk_size=1000, overlap=100):
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        if end < text_len:
            last_space = text.rfind(' ', start, end)
            if last_space != -1:
                end = last_space
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
        if start >= end: start = end
    return chunks

# --- 4. MAIN: SAVE TO DB ---
def create_embeddings_and_store(file_path, filename):
    # A. Get the text (Handles PDF or TXT now)
    try:
        text = get_text_from_file(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # B. Chunk it
    text_chunks = chunk_text(text)
    
    if not text_chunks:
        return False

    # C. Create Metadata
    ids = [f"{filename}_chunk_{i}" for i in range(len(text_chunks))]
    metadatas = [{"source": filename, "chunk_index": i} for i in range(len(text_chunks))]
    
    # D. Save to Chroma
    collection.add(documents=text_chunks, metadatas=metadatas, ids=ids)
    print(f"✅ Indexed {len(text_chunks)} chunks from {filename}")
    return True

# --- 5. SEARCH ---
def query_vector_db(query_text, n_results=3):
    return collection.query(query_texts=[query_text], n_results=n_results)

# --- 6. GENERATE ANSWER ---
def generate_answer(query, retrieved_results):
    if not retrieved_results['documents'][0]:
        return "I couldn't find any relevant information in the document."

    context_chunks = retrieved_results['documents'][0]
    context_text = "\n\n---\n\n".join(context_chunks)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Use the provided context to answer the question. If the answer is not in the context, say you don't know."},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
        ]
    )
    return response.choices[0].message.content

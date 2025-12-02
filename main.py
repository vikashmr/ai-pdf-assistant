from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import os
# We import the NEW functions from rag.py
from rag import create_embeddings_and_store, query_vector_db, generate_answer

app = FastAPI()

# Define what a query looks like
class QueryRequest(BaseModel):
    query: str

@app.post("/upload-and-index")
async def upload_and_index(file: UploadFile = File(...)):
    # 1. Save the file locally
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Run the new Chunking & Embedding function
    success = create_embeddings_and_store(file_path, file.filename)
    
    if success:
        return {"message": f"Successfully processed and chunked {file.filename}"}
    else:
        raise HTTPException(status_code=400, detail="Failed to process file")

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    # 1. Search the Vector DB
    results = query_vector_db(request.query, n_results=3)
    
    # 2. Generate Answer
    answer = generate_answer(request.query, results)
    
    return {
        "answer": answer,
        "sources": results['metadatas'][0] 
    }   

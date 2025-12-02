from rag import chunk_text

def test_chunking_logic():
    # 1. Create a fake long text (2500 characters)
    long_text = "AI is the future. " * 150
    
    # 2. Run your chunking function
    chunks = chunk_text(long_text, chunk_size=1000, overlap=100)
    
    # 3. Assertions (The "Test")
    assert len(chunks) > 1, "Text should be split into multiple chunks"
    assert len(chunks[0]) <= 1000, "Chunk size should not exceed limit"
    print("✅ Logic Test Passed: Chunking works correctly.")

if __name__ == "__main__":
    test_chunking_logic()

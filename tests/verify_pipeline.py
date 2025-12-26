import os
from pipeline.text_cleaner import clean_text
from pipeline.chunker import chunk_text
from pipeline.embedder import get_embedding
from pipeline.rag_engine import generate_answer
from config import BASE_DIR, DOCS_DIR
import fitz

def create_dummy_pdf():
    pdf_path = os.path.join(DOCS_DIR, "test_doc.pdf")
    doc = fitz.open()
    page = doc.new_page()
    text = "Hacettepe Universitesi Yapay Zeka Muhendisligi bolumu 2019 yilinda kurulmustur. Bu bolum Turkiye'de ilktir."
    page.insert_text((50, 50), text)
    doc.save(pdf_path)
    print(f"Created dummy PDF at {pdf_path}")
    return pdf_path

def run_verification():
    print("--- Starting Verification ---")
    
    # 1. Ensure Directory
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

    # 2. Create Dummy PDF
    pdf_path = create_dummy_pdf()

    # 3. Test Loading (Using imported logic concept, but let's just use the main flow via imports)
    from pipeline.pdf_loader import load_pdf
    raw_text = load_pdf(pdf_path)
    print(f"1. PDF Loaded based on length: {len(raw_text) > 10}")

    # 4. Cleaning
    clean = clean_text(raw_text)
    print(f"2. Text Cleaned: {clean}")

    # 5. Chunking
    chunks = chunk_text(clean)
    print(f"3. Chunks Generated: {len(chunks)}")
    
    # 6. Embedding & Storage (Integration Test)
    # We will assume main.py logic works if individual components work.
    # Testing embedding connection:
    emb = get_embedding("test")
    if emb and len(emb) > 0:
        print("4. Embedding API Connected & Working")
    else:
        print("4. Embedding API FAILED")
        return

    # 7. RAG Generation Test
    # This might require the data to be in DB. Let's add it first.
    from pipeline.vector_store import add_documents
    import uuid
    
    doc_data = [{
        "id": str(uuid.uuid4()),
        "text": chunk,
        "embedding": get_embedding(chunk),
        "source": "test_doc.pdf",
        "metadata": "{}"
    } for chunk in chunks]
    
    add_documents(doc_data)
    print("5. Vectors Stored")
    
    # query
    answer = generate_answer("Hacettepe YZ bolumu ne zaman kuruldu?")
    print(f"6. RAG Answer:\n{answer}")

if __name__ == "__main__":
    run_verification()

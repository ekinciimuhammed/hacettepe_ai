import os
from pipeline.pdf_loader import load_pdf
from pipeline.text_cleaner import clean_text
from pipeline.chunker import chunk_text
from config import DOCS_DIR

def debug_pdf():
    # Target a specific file that likely has "Madde" structure
    filename = "2025_mayıs__önlisans lisans yurtdışından öğrenci alım yönerge (1).pdf"
    file_path = os.path.join(DOCS_DIR, filename)
    
    if not os.path.exists(file_path):
        print(f"File not found: {filename}")
        # Fallback to the one we saw in logs if this specific name is tricky with unicode
        filename = "7.5.13948.pdf" 
        file_path = os.path.join(DOCS_DIR, filename)
        print(f"Falling back to: {filename}")

    print(f"--- Debugging {filename} ---")
    
    # 1. Load
    raw_text = load_pdf(file_path)
    print(f"\n[RAW TEXT START (First 500 chars)]:\n{raw_text[:500]}\n[RAW TEXT END]")
    
    # 2. Clean
    cleaned = clean_text(raw_text)
    print(f"\n[CLEANED TEXT START (First 500 chars)]:\n{cleaned[:500]}\n[CLEANED TEXT END]")
    
    # 3. Chunk
    chunks = chunk_text(cleaned)
    print(f"\n[CHUNKS GENERATED]: {len(chunks)}")
    
    for i in range(min(3, len(chunks))):
        print(f"\n--- Chunk {i+1} ---\n{chunks[i][:300]}...\n----------------")

if __name__ == "__main__":
    debug_pdf()

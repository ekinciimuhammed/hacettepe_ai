import os
import time
import uuid
import json
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import DOCS_DIR, ENABLE_HYBRID_RAG
from pipeline.pdf_loader import load_pdf
from pipeline.text_cleaner import clean_text
from pipeline.chunker import chunk_text
from pipeline.embedder import get_embedding
from pipeline.vector_store import add_documents, create_table_if_not_exists, is_file_indexed
from pipeline.rag_engine import generate_answer

# Hybrid RAG için entity extractor
if ENABLE_HYBRID_RAG:
    from pipeline.entity_extractor import extract_entities

def process_file(file_path):
    print(f"Processing file: {file_path}")
    
    filename = os.path.basename(file_path)
    if is_file_indexed(filename):
        print(f"Skipping {filename} (Already indexed)")
        return

    # 1. Load
    raw_text = load_pdf(file_path)
    if not raw_text:
        print(f"Skipping {file_path} (Empty or unreadable)")
        return

    # 2. Clean
    cleaned_text = clean_text(raw_text)
    
    # 3. Chunk
    chunks = chunk_text(cleaned_text)
    print(f"Generated {len(chunks)} chunks from {os.path.basename(file_path)}")
    
    # 4. Embed & Prepare for DB
    documents = []
    for chunk in chunks:
        emb = get_embedding(chunk)
        if emb:
            # Hybrid RAG: Entity extraction
            if ENABLE_HYBRID_RAG:
                entities = extract_entities(chunk)
                metadata = json.dumps(entities, ensure_ascii=False)
            else:
                metadata = "{}"
            
            doc = {
                "id": str(uuid.uuid4()),
                "text": chunk,
                "embedding": emb,
                "source": os.path.basename(file_path),
                "metadata": metadata
            }
            documents.append(doc)
    
    # 5. Store
    if documents:
        add_documents(documents)
        print(f"Stored {len(documents)} vectors for {os.path.basename(file_path)}")
        if ENABLE_HYBRID_RAG:
            print(f"  ✨ Hybrid RAG: Entities extracted and stored")
    else:
        print(f"No valid embeddings generated for {file_path}")

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            print(f"New PDF detected: {event.src_path}")
            # Slight delay to ensure file write complete
            time.sleep(1)
            process_file(event.src_path)

def initial_scan():
    print("Performing initial scan of documents folder...")
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        
    for filename in os.listdir(DOCS_DIR):
        if filename.lower().endswith(".pdf"):
            process_file(os.path.join(DOCS_DIR, filename))
    print("Initial scan complete.")

def start_watcher():
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, path=DOCS_DIR, recursive=False)
    observer.start()
    print(f"Watching {DOCS_DIR} for new PDFs...")
    return observer

def chat_loop():
    print("\n--- Local RAG Assistant Ready ---")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            print("Thinking...")
            response = generate_answer(user_input)
            print(f"\nSystem:\n{response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure DB connection / basic setup
    create_table_if_not_exists()
    
    # 1. Initial Scan
    initial_scan()
    
    # 2. Start Watcher (in background thread concept, but Observer is threaded)
    observer = start_watcher()
    
    # 3. Chat Loop
    try:
        chat_loop()
    finally:
        observer.stop()
        observer.join()

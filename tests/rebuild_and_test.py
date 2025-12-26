import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import initial_scan
from pipeline.rag_engine import generate_answer
import time

def main():
    print("🔄 Starting Database Rebuild and Test...")
    
    # 1. Trigger Initial Scan (This will process the single file in belgeler/)
    print("\n--- Step 1: Indexing Document ---")
    start_time = time.time()
    initial_scan()
    print(f"Indexing completed in {time.time() - start_time:.2f} seconds.")
    
    # 2. Run Test Queries
    print("\n--- Step 2: Running Verification Queries ---")
    
    queries = [
        "Akademik başarı sıralaması nedir ve kimlere verilir?",
        "Hacettepe Üniversitesi'nde dereceye giren öğrencilere hangi belgeler verilir?",
        "Mezuniyet başarı sıralaması nasıl hesaplanır?"
    ]
    
    for q in queries:
        print(f"\n❓ Soru: {q}")
        print("-" * 50)
        answer = generate_answer(q)
        print(f"💡 Yanıt:\n{answer}")
        print("-" * 50)

if __name__ == "__main__":
    main()

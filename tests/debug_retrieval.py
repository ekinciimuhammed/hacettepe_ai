import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.rag_engine import retrieve_context

query = "Mezuniyet başarı sıralamasına girebilmek için mezuniyet GANO alt sınırı kaçtır?"
print(f"--- Debugging Query: {query} ---")

chunks = retrieve_context(query)

if not chunks:
    print("No chunks retrieved.")
else:
    for i, c in enumerate(chunks):
        print(f"\n[{i+1}] Source: {c['source']}")
        print(f"Score: {c.get('score', 'N/A')}")
        print("-" * 20)
        print(c['text'])
        print("-" * 20)

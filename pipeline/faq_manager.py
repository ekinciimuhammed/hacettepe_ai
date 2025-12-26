import json
import os
from typing import Optional, Dict

class FAQManager:
    def __init__(self, faq_path: str = "data/faq.json"):
        self.faq_path = faq_path
        self.faqs = []
        self.load_faqs()

    def load_faqs(self):
        """Loads FAQs from the JSON file."""
        if not os.path.exists(self.faq_path):
            print(f"⚠️ FAQ file not found at {self.faq_path}")
            return
            
        try:
            with open(self.faq_path, 'r', encoding='utf-8') as f:
                self.faqs = json.load(f)
        except Exception as e:
            print(f"❌ Error loading FAQs: {e}")

    def find_match(self, query: str, threshold: float = 0.8) -> Optional[Dict]:
        """
        Finds a matching FAQ for the given query.
        Uses simple normalized string containment for now (Can be upgraded to embedding search).
        """
        query_norm = query.lower().strip()
        
        # 1. Exact/Substring Match (High Confidence)
        for entry in self.faqs:
            for q in entry["questions"]:
                q_norm = q.lower().strip()
                if q_norm == query_norm or q_norm in query_norm:
                    return self._format_response(entry)
                    
        return None

    def _format_response(self, entry: Dict) -> Dict:
        """Formats the FAQ entry into the standard RAG response structure."""
        return {
            "answer": entry["answer"],
            "sources": [entry["source"]],
            "chunks": [{
                "text": entry.get("chunck_text", entry["answer"]),
                "source": entry["source"],
                "score": 1.0  # Max confidence
            }],
            "intent": "VERIFIED_FAQ"
        }

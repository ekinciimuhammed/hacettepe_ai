import requests
import json
from enum import Enum
from typing import Tuple, Optional
from config import OLLAMA_BASE_URL, LLM_MODEL

class Intent(Enum):
    GREETING = "GREETING"
    NON_ACADEMIC = "NON_ACADEMIC"
    ACADEMIC_READY = "ACADEMIC_READY"
    ACADEMIC_NEEDS_CLARIFICATION = "ACADEMIC_NEEDS_CLARIFICATION"

class IntentRouter:
    """
    Classifies user input using a lightweight LLM call to ensure semantic understanding.
    """
    
    def __init__(self):
        self.url = f"{OLLAMA_BASE_URL}/api/generate"
        self.model = LLM_MODEL # Using the main model for now, could be switched to a smaller one

    def route(self, query: str) -> Tuple[Intent, Optional[str]]:
        """
        Determines the intent of the query using LLM.
        """
        cleaned = query.strip()
        if not cleaned:
            return Intent.GREETING, "Bir soru yazmadınız. Size nasıl yardımcı olabilirim?"

        prompt = f"""
        You are an Intent Classifier for a University AI Assistant.
        Classify the User Query into EXACTLY ONE of these categories:
        
        1. GREETING: Common greetings, introductory words (e.g., "Selam", "Merhaba", "Nasılsın", "Günaydın").
        2. NON_ACADEMIC: Questions strictly UNRELATED to university, academic life, or administrative rules (e.g., "Fenerbahçe maçı kaç kaç?", "Hava durumu?", "Pizza tarifi", "Espri yap").
        3. ACADEMIC_NEEDS_CLARIFICATION: The query is about university/academic topics BUT is too vague or lacks context (e.g., just "sınav", "gpa", "büt", "yönetmelik", "ders").
        4. ACADEMIC_READY: A specific, clear question about university rules, regulations, lessons, or campus life (e.g., "ÇAP başvurusu ne zaman?", "Mezuniyet ortalaması kaç olmalı?", "Sınavdan kalınca ne olur?").

        User Query: "{cleaned}"

        Respond ONLY with a JSON object: {{"intent": "CATEGORY_NAME"}}
        Do not explain.
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.0}
        }

        try:
            response = requests.post(self.url, json=payload, timeout=10) # Fast timeout -> Increased to 10s for local LLM
            response.raise_for_status()
            result = response.json().get("response", "")
            data = json.loads(result)
            intent_str = data.get("intent", "ACADEMIC_READY")
            
            # Map string to Enum
            try:
                intent = Intent(intent_str)
            except ValueError:
                intent = Intent.ACADEMIC_READY # Fallback
            
            # Generate suggestions based on intent
            suggestion = self._get_suggestion(intent, cleaned)
            return intent, suggestion

        except Exception as e:
            print(f"Intent Classifier Error: {e}")
            # Fallback safe mode
            return Intent.ACADEMIC_READY, None

    def _get_suggestion(self, intent: Intent, query: str) -> Optional[str]:
        if intent == Intent.GREETING:
            return (
                "Merhaba! 👋 Ben Hacettepe Akademik Asistan.\n\n"
                "Üniversite yönetmelikleri, mezuniyet şartları, ÇAP/Yandal gibi "
                "konularda sorularınızı yanıtlamak için buradayım. Size nasıl yardımcı olabilirim?"
            )
        elif intent == Intent.NON_ACADEMIC:
            return (
                "Üzgünüm, ben sadece Hacettepe Üniversitesi akademik ve idari konularında "
                "yardımcı olmak üzere tasarlandım. Spor, hava durumu veya genel sohbet konularında "
                "bilgi sağlayamıyorum. Lütfen üniversite ile ilgili bir soru sorun."
            )
        elif intent == Intent.ACADEMIC_NEEDS_CLARIFICATION:
             return (
                 f"'{query}' konusu çok geniş. Size doğru bilgi verebilmem için lütfen sorunuzu "
                 "biraz daha detaylandırın.\n\n"
                 "Örnek: 'GPA şartı nedir?', 'Sınav tarihleri ne zaman?', 'Yaz okulu yönetmeliği' gibi."
             )
        return None

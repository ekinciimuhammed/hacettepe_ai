import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "belgeler")
LANCEDB_URI = os.path.join(BASE_DIR, "lancedb_data")

# Models
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "bge-m3:latest"
LLM_MODEL = "llama3.1:8b"  # User requested switch to installed model

# Chunking
# Dynamic chunking will try to respect "Madde" boundaries.
# CHUNK_SIZE here acts as a "safety limit" for very long articles.
# Document Processing
USE_DOCLING = True
DOCLING_OCR_CONFIDENCE = 0.8  # Threshold to reject bad OCR
CHUNK_SIZE = 1000 
CHUNK_OVERLAP = 200

# RAG
TOP_K = 6  # Artırıldı: Daha fazla chunk getir, entity re-ranking daha iyi çalışsın
MIN_SCORE_THRESHOLD = 0.35  # Geri getirildi: Kalite kontrolü için threshold
# Intent Gating
MIN_QUERY_LENGTH = 3 # Words

# Document Hierarchy (Re-ranking Weights)
# Multipliers to boost "Constitutional" docs over "Specific Directives"
DOCUMENT_PRIORITIES = {
    "EĞİTİM-ÖĞRETİM": 1.25,  # Ana Yönetmelik (Constitution) - Boost 25%
    "YÖNETMELİK": 1.10,      # Diğer Yönetmelikler (Laws) - Boost 10%
    "YÖNERGE": 1.0,          # Standart Yönergeler (Directives) - Baseline
    "SIRALAMASI": 0.85       # Başarı Sıralaması vb. (Specific/Confusing) - Slight Penalty
}

# Hybrid RAG (Entity-based enhancement)
ENABLE_HYBRID_RAG = True  # Hybrid RAG'i aktif et
VECTOR_WEIGHT = 0.6       # Azaltıldı: Entity matching'e daha fazla ağırlık ver
ENTITY_WEIGHT = 0.4       # Artırıldı: Spesifik sorgular için entity match önemli

# Cache Settings
ENABLE_CACHE = True       # Query-answer cache'i aktif et
CACHE_DIR = os.path.join(BASE_DIR, "cache")
CACHE_MAX_AGE_HOURS = 24  # Cache geçerlilik süresi (saat)

# Retry Settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# System Prompt
SYSTEM_PROMPT = """
Sen Hacettepe Üniversitesi öğrencileri için geliştirilmiş, yardımsever ve dürüst bir akademik asistansın.
Amacın: Öğrencilerin yönetmelik, mezuniyet, ders seçimi ve kampüs yaşamı hakkındaki sorularına, SADECE sana verilen belge parçalarına (Context) dayanarak cevap vermektir.

Kurallar:
1. SADECE verilen "CONTEXT" bilgisini kullan. Kendi dış bilgilerini kullanma.
2. Eğer verilen metinlerde sorunun cevabı KESİN OLARAK yoksa, uydurma. "Belgelerde bu bilgi yer almıyor" de.
3. "Şeref öğrencisi", "Sıralama", "ÇAP" gibi ÖZEL DURUMLARI, GENEL KURALLARDAN ayır. Örneğin, genel mezuniyet ortalaması ile dereceye girme ortalamasını karıştırma.
4. Çelişkili bilgiler görürsen, GENEL olanı (tüm öğrenciler için geçerli olanı) temel al ve özerl durumu istisna olarak belirt.
5. Cevabın kısa, net ve anlaşılır olsun. Resmi ama samimi bir dil kullan.
6. Asla var olmayan bir yönetmelik maddesi uydurma.

Eğer sorulan soru akademik veya üniversite ile ilgili değilse (örneğin futbol, yemek tarifi vb.), kibarca cevap veremeyeceğini belirt.
"""

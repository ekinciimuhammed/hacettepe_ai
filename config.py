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
CHUNK_SIZE = 4000  
CHUNK_OVERLAP = 200

# RAG
TOP_K = 6  # Artırıldı: Daha fazla chunk getir, entity re-ranking daha iyi çalışsın
MIN_SCORE_THRESHOLD = 0.35  # Geri getirildi: Kalite kontrolü için threshold

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
Sen **Hacettepe_Akademik_Asistan**'sın (Sürüm 1.0).
Görevin: Hacettepe Üniversitesi'ne ait resmî akademik belgeleri referans alarak bilgi vermek.

**KURALLAR:**
1. **Kaynak Sınırı:** Sadece sana verilen "CONTEXT" (bağlam) içindeki bilgileri kullan.
2. **Uydurma Yasak:** Belgelerde olmayan bir bilgi hakkında asla tahmin, yorum veya ekleme yapma.
3. **Öncelik:** Önce yüklenen belge bağlamını kullan.
4. **Yanıt Stili:** Kısa, öz, net, tarafsız, resmi ve akademik bir dil kullan. Kişisel yorum veya duygu katma.
5. **Kapsam Dışı:** Politik, dini, tıbbi, hukuki veya kişisel veri içeren sorulara "Bu konu Hacettepe Akademik Asistanı’nın kapsamı dışındadır." yanıtını ver.
6. **Eğer Bağlam Yoksa:** Soru akademik ise "Belge bulunmadığı için yanıt veremiyorum." de. Soru günlük sohbet (selam vb.) ise kısa bir yanıt ver.

Bunu sakın unutma: Sen sadece belgelerdeki gerçeği yansıtan bir asistansın.
"""

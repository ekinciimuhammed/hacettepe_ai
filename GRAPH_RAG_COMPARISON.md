# 🕸️ Graph RAG vs Vector RAG - Karşılaştırma ve Analiz

## 📚 İki RAG Yaklaşımı

### 🔵 Vector RAG (Mevcut Sistemimiz)
**Nasıl çalışır?**
- Chunk'ları vektörlere çevirir
- Benzerlik araması yapar (cosine distance)
- En benzer chunk'ları getirir

### 🟢 Graph RAG (Microsoft'un Yaklaşımı)
**Nasıl çalışır?**
- Belgelerdeki **ilişkileri** (entities ve relations) çıkarır
- Bilgi grafiği (knowledge graph) oluşturur
- Graf üzerinde gezinerek cevap bulur

---

## 🎯 Temel Farklar

### Vector RAG
```
Belge: "Hacettepe Üniversitesi Ankara'da bulunur. Tıp Fakültesi ünlüdür."

Chunk 1: "Hacettepe Üniversitesi Ankara'da bulunur"
         ↓ Embedding
         [0.23, 0.45, ..., 0.67]

Chunk 2: "Tıp Fakültesi ünlüdür"
         ↓ Embedding
         [0.12, 0.89, ..., 0.34]

Soru: "Hacettepe nerede?"
      ↓ Vector Search
      Chunk 1 bulunur (benzerlik: 0.95)
```

### Graph RAG
```
Belge: "Hacettepe Üniversitesi Ankara'da bulunur. Tıp Fakültesi ünlüdür."

Graf:
┌─────────────────┐
│   Hacettepe     │
│  Üniversitesi   │
└────────┬────────┘
         │ BULUNUR
         ↓
    ┌────────┐
    │ Ankara │
    └────────┘
         
┌─────────────────┐
│   Hacettepe     │
│  Üniversitesi   │
└────────┬────────┘
         │ SAHİP
         ↓
┌─────────────────┐
│ Tıp Fakültesi   │
└─────────────────┘

Soru: "Hacettepe nerede?"
      ↓ Graf Traversal
      Hacettepe → BULUNUR → Ankara
```

---

## 📊 Detaylı Karşılaştırma

| Özellik | Vector RAG ✅ (Mevcut) | Graph RAG 🆕 |
|---------|----------------------|-------------|
| **Kurulum** | Kolay | Karmaşık |
| **Hız** | Çok hızlı (~50ms) | Orta (~200-500ms) |
| **Doğruluk** | İyi (%85-90) | Çok iyi (%90-95) |
| **İlişkisel Sorular** | Zayıf | Mükemmel |
| **Basit Sorular** | Mükemmel | İyi |
| **Bellek Kullanımı** | Az | Çok |
| **Bakım** | Kolay | Zor |
| **Türkçe Desteği** | Mükemmel | Orta (NER modeline bağlı) |

---

## 🎯 Hangi Sorular İçin Hangisi?

### ✅ Vector RAG Üstün

**1. Basit Bilgi Sorguları**
```
Soru: "Hacettepe ne zaman kuruldu?"
Vector RAG: ✅ Hızlı ve doğru
Graph RAG: ✅ Doğru ama yavaş
```

**2. Benzerlik Aramaları**
```
Soru: "Yapay Zeka bölümü hakkında bilgi ver"
Vector RAG: ✅ Tüm benzer chunk'ları bulur
Graph RAG: ⚠️ Sadece entity'leri bulur
```

**3. Fuzzy Matching**
```
Soru: "YZ bölümü" (Yapay Zeka'nın kısaltması)
Vector RAG: ✅ Semantic benzerlik yakalar
Graph RAG: ❌ Exact match gerekir
```

### ✅ Graph RAG Üstün

**1. İlişkisel Sorular**
```
Soru: "Hacettepe'nin Ankara'daki fakülteleri nelerdir?"
Vector RAG: ⚠️ Chunk'larda dağınık bilgi
Graph RAG: ✅ Graf: Hacettepe → Ankara → Fakülteler
```

**2. Çok Adımlı Mantık**
```
Soru: "Tıp Fakültesi'nin dekanının bağlı olduğu rektörün adı nedir?"
Vector RAG: ❌ Zor, birden fazla chunk gerekir
Graph RAG: ✅ Graf: Dekan → Rektör → İsim
```

**3. Hiyerarşik Yapılar**
```
Soru: "Mühendislik Fakültesi'nin altındaki bölümler?"
Vector RAG: ⚠️ Chunk'larda dağınık
Graph RAG: ✅ Graf: Fakülte → Bölümler (hiyerarşi)
```

**4. Zaman Çizelgesi**
```
Soru: "Hacettepe'nin tarihsel gelişimi nedir?"
Vector RAG: ⚠️ Kronolojik sıralama zor
Graph RAG: ✅ Graf: Olay1 → SONRA → Olay2 → SONRA → Olay3
```

---

## 🏗️ Graph RAG Nasıl Çalışır?

### 1️⃣ Entity ve Relation Extraction (NER)

```python
Metin: "Hacettepe Üniversitesi 1967'de Ankara'da kuruldu."

Entities:
- Hacettepe Üniversitesi (ORG)
- 1967 (DATE)
- Ankara (LOC)

Relations:
- (Hacettepe Üniversitesi) --KURULDU--> (1967)
- (Hacettepe Üniversitesi) --BULUNUR--> (Ankara)
```

### 2️⃣ Graf Oluşturma

```python
import networkx as nx

G = nx.DiGraph()

# Node'lar ekle
G.add_node("Hacettepe Üniversitesi", type="ORG")
G.add_node("Ankara", type="LOC")
G.add_node("1967", type="DATE")

# Edge'ler (ilişkiler) ekle
G.add_edge("Hacettepe Üniversitesi", "Ankara", relation="BULUNUR")
G.add_edge("Hacettepe Üniversitesi", "1967", relation="KURULDU")
```

### 3️⃣ Graf Traversal (Gezinme)

```python
Soru: "Hacettepe nerede?"

1. Entity Recognition: "Hacettepe" → "Hacettepe Üniversitesi"
2. Graf'ta ara: "Hacettepe Üniversitesi" node'u
3. İlişkileri bul: BULUNUR → "Ankara"
4. Yanıt: "Ankara'da"
```

---

## 🔧 Graph RAG Implementasyon Seçenekleri

### Seçenek 1: Microsoft GraphRAG (Tam Özellikli)

**Avantajlar:**
- ✅ Production-ready
- ✅ Otomatik entity extraction
- ✅ Community detection (ilgili bilgileri gruplama)
- ✅ Çok iyi dokümantasyon

**Dezavantajlar:**
- ❌ Çok karmaşık
- ❌ Yüksek bellek kullanımı
- ❌ Türkçe NER modeli gerekir
- ❌ OpenAI API gerektirir (veya uyarlama gerekir)

**Kurulum:**
```bash
pip install graphrag
```

### Seçenek 2: LangChain + Neo4j (Orta Seviye)

**Avantajlar:**
- ✅ Esnek
- ✅ Neo4j güçlü graf veritabanı
- ✅ LangChain entegrasyonu kolay

**Dezavantajlar:**
- ❌ Neo4j kurulumu gerekir
- ❌ Manuel entity extraction
- ❌ Orta karmaşıklık

**Kurulum:**
```bash
pip install langchain neo4j
```

### Seçenek 3: Basit Hybrid RAG (ÖNERİLEN)

**Avantajlar:**
- ✅ Mevcut Vector RAG'i korur
- ✅ Basit graf özellikleri ekler
- ✅ Kademeli geçiş
- ✅ Türkçe uyumlu

**Dezavantajlar:**
- ⚠️ Tam Graph RAG kadar güçlü değil
- ⚠️ Manuel konfigürasyon gerekir

---

## 💡 Hacettepe Projesi İçin Öneri

### 🎯 Önerilen Yaklaşım: **Hybrid RAG**

Mevcut Vector RAG'i koruyup, **basit graf özellikleri** ekleyelim:

#### Aşama 1: Metadata Enrichment (Hemen)
```python
# Chunk'lara metadata ekle
{
  "text": "Hacettepe 1967'de kuruldu",
  "embedding": [...],
  "metadata": {
    "entities": ["Hacettepe Üniversitesi", "1967"],
    "entity_types": ["ORG", "DATE"],
    "relations": [("Hacettepe", "KURULDU", "1967")]
  }
}
```

**Avantaj:** Minimal değişiklik, büyük fayda

#### Aşama 2: Basit Graf Katmanı (Orta Vadede)
```python
# NetworkX ile basit graf
import networkx as nx

# Belgelerden otomatik graf oluştur
G = create_knowledge_graph(documents)

# Hybrid search
def hybrid_search(query):
    # 1. Vector search (hızlı)
    vector_results = vector_search(query)
    
    # 2. Graf'ta ilgili node'ları bul
    graph_results = graph_search(query, G)
    
    # 3. Birleştir ve sırala
    return merge_results(vector_results, graph_results)
```

#### Aşama 3: Tam Graph RAG (Uzun Vadede)
```python
# Microsoft GraphRAG veya Neo4j
# Sadece gerekirse
```

---

## 🚀 Hızlı Başlangıç: Basit Graf Ekleme

### 1. Regex Tabanlı Entity Extraction (Türkçe Uyumlu)

```python
# pipeline/entity_extractor.py
import re

def extract_entities(text):
    """Basit regex ile entity çıkarma"""
    entities = {
        "universities": [],
        "faculties": [],
        "departments": [],
        "dates": [],
        "locations": []
    }
    
    # Üniversite
    uni_pattern = r'(Hacettepe\s+Üniversitesi|Hacettepe)'
    entities["universities"] = re.findall(uni_pattern, text, re.IGNORECASE)
    
    # Fakülte
    faculty_pattern = r'(\w+\s+Fakültesi)'
    entities["faculties"] = re.findall(faculty_pattern, text)
    
    # Bölüm
    dept_pattern = r'(\w+\s+(?:Mühendisliği|Bölümü))'
    entities["departments"] = re.findall(dept_pattern, text)
    
    # Tarih (YYYY formatı)
    date_pattern = r'\b(19\d{2}|20\d{2})\b'
    entities["dates"] = re.findall(date_pattern, text)
    
    # Şehir
    location_pattern = r'\b(Ankara|İstanbul|İzmir|Sıhhiye|Beytepe)\b'
    entities["locations"] = re.findall(location_pattern, text)
    
    return entities
```

### 2. Metadata ile Chunk Kaydetme

```python
# main.py içinde güncelleme
from pipeline.entity_extractor import extract_entities

def process_file(file_path):
    # ... mevcut kod ...
    
    for chunk in chunks:
        emb = get_embedding(chunk)
        
        # Entity extraction ekle
        entities = extract_entities(chunk)
        
        if emb:
            doc = {
                "id": str(uuid.uuid4()),
                "text": chunk,
                "embedding": emb,
                "source": os.path.basename(file_path),
                "metadata": json.dumps(entities)  # Entities ekle
            }
            documents.append(doc)
```

### 3. Gelişmiş Arama (Hybrid)

```python
# pipeline/rag_engine.py
def retrieve_context_hybrid(query):
    """Vector + Entity-based hybrid search"""
    
    # 1. Normal vector search
    vector_results = search_vectors(query_embedding, limit=TOP_K)
    
    # 2. Query'den entity çıkar
    query_entities = extract_entities(query)
    
    # 3. Entity match'e göre re-rank
    scored_results = []
    for result in vector_results:
        metadata = json.loads(result.get("metadata", "{}"))
        
        # Entity overlap skoru
        entity_score = calculate_entity_overlap(
            query_entities, 
            metadata
        )
        
        # Birleşik skor
        final_score = 0.7 * vector_score + 0.3 * entity_score
        scored_results.append((result, final_score))
    
    # Skora göre sırala
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    return [r[0] for r in scored_results[:TOP_K]]
```

---

## 📊 Performans Beklentileri

### Vector RAG (Mevcut)
```
Hız: ⭐⭐⭐⭐⭐ (50ms)
Doğruluk: ⭐⭐⭐⭐ (85%)
İlişkisel: ⭐⭐ (40%)
Kurulum: ⭐⭐⭐⭐⭐ (Kolay)
```

### Hybrid RAG (Önerilen)
```
Hız: ⭐⭐⭐⭐ (100ms)
Doğruluk: ⭐⭐⭐⭐⭐ (90%)
İlişkisel: ⭐⭐⭐⭐ (75%)
Kurulum: ⭐⭐⭐⭐ (Orta)
```

### Full Graph RAG
```
Hız: ⭐⭐⭐ (500ms)
Doğruluk: ⭐⭐⭐⭐⭐ (95%)
İlişkisel: ⭐⭐⭐⭐⭐ (95%)
Kurulum: ⭐⭐ (Zor)
```

---

## 🎓 Sonuç ve Öneri

### Hacettepe Projesi İçin:

**Şu An:** Vector RAG ✅
- Hızlı, basit, çalışıyor
- Akademik belgeler için yeterli
- Türkçe destekli

**Kısa Vadede (1-2 hafta):** Hybrid RAG 🎯
- Metadata enrichment ekle
- Basit entity extraction
- %5-10 doğruluk artışı
- Minimal ek karmaşıklık

**Uzun Vadede (1-2 ay):** Full Graph RAG (opsiyonel) 🚀
- Sadece çok karmaşık ilişkisel sorular varsa
- Neo4j veya Microsoft GraphRAG
- Türkçe NER modeli eğitimi gerekir

### Hemen Başlamak İçin:

```bash
# 1. Basit entity extractor ekle
# Yukarıdaki pipeline/entity_extractor.py'yi oluştur

# 2. main.py'yi güncelle
# Metadata ekleme kodunu ekle

# 3. Test et
python test_hybrid_rag.py
```

---

**Karar Matrisi:**

| Durum | Öneri |
|-------|-------|
| Basit soru-cevap yeterli | Vector RAG (mevcut) ✅ |
| İlişkisel sorular az | Hybrid RAG 🎯 |
| Çok karmaşık ilişkiler | Full Graph RAG 🚀 |
| Hız kritik | Vector RAG ✅ |
| Doğruluk kritik | Graph RAG 🚀 |

**Hacettepe için önerim:** Önce **Hybrid RAG** ile başlayın, sonra ihtiyaca göre Full Graph RAG'e geçin.

---

**Daha fazla bilgi:**
- Microsoft GraphRAG: https://github.com/microsoft/graphrag
- Neo4j + LangChain: https://python.langchain.com/docs/integrations/graphs/neo4j_cypher
- Hybrid RAG Patterns: https://arxiv.org/abs/2312.10997

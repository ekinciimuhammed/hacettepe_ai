# 🎓 Hacettepe Akademik Asistan (RAG Sistemi)

**Hacettepe Üniversitesi** için geliştirilmiş, yerel olarak çalışan, **Retrieval-Augmented Generation (RAG)** tabanlı akademik soru-cevap asistanı.

## 📋 İçindekiler
- [Proje Hakkında](#-proje-hakkında)
- [Sistem Mimarisi](#-sistem-mimarisi)
- [Teknolojiler](#-teknolojiler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Proje Yapısı](#-proje-yapısı)
- [Çalışma Mantığı](#-çalışma-mantığı)
- [Veritabanı Yönetimi](#-veritabanı-yönetimi)
- [Konfigürasyon](#-konfigürasyon)

---

## 🎯 Proje Hakkında

Bu proje, Hacettepe Üniversitesi'ne ait akademik belgeleri (PDF formatında) işleyerek, kullanıcıların bu belgeler hakkında sorular sormasını ve doğru, kaynak tabanlı yanıtlar almasını sağlar.

### Temel Özellikler:
- ✅ **Otomatik PDF İzleme**: `belgeler/` klasörüne eklenen PDF'ler otomatik olarak işlenir
- ✅ **OCR Desteği**: Taranmış PDF'ler için Tesseract OCR entegrasyonu
- ✅ **Semantic Chunking**: Paragraf/cümle sınırlarını koruyan akıllı metin bölümleme
- ✅ **Enhanced Hybrid RAG**: Vector similarity + 10 entity tipi ile gelişmiş arama
- ✅ **Gelişmiş Entity Extraction**: Programlar, dersler, enstitüler, araştırma merkezleri
- ✅ **Query Caching**: Tekrar sorular için 300-500x hız artışı
- ✅ **Vektör Tabanlı Arama**: LanceDB ile hızlı ve etkili arama (Cosine distance)
- ✅ **Yerel LLM**: Ollama ile tamamen offline çalışma
- ✅ **Kaynak Gösterimi**: Her yanıtta kullanılan belgeler ve chunk'lar gösterilir

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────┐
│  PDF Belgeler   │
│   (belgeler/)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              PIPELINE (İşleme Hattı)                │
│                                                     │
│  1. PDF Loader    → PDF'den metin çıkarma          │
│  2. Text Cleaner  → Metin temizleme ve normalize   │
│  3. Chunker       → Madde bazlı bölümleme          │
│  4. Embedder      → Vektör embedding (bge-m3)      │
│  5. Vector Store  → LanceDB'ye kaydetme            │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   LanceDB       │
│ (Vektör DB)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              RAG ENGINE (Soru-Cevap)                │
│                                                     │
│  1. Soru → Embedding                               │
│  2. Vektör Arama (Top-K)                           │
│  3. Context Oluşturma                              │
│  4. LLM ile Yanıt Üretme (llama3.1:8b)            │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   Kullanıcı     │
│    Yanıtı       │
└─────────────────┘
```

---

## 🛠️ Teknolojiler

### Core Dependencies
- **Python 3.8+**
- **PyMuPDF (fitz)**: PDF okuma
- **pytesseract**: OCR (taranmış PDF'ler için)
- **LanceDB**: Vektör veritabanı
- **Ollama**: Yerel LLM ve embedding modelleri
- **watchdog**: Dosya sistemi izleme

### AI Modelleri (Ollama)
- **Embedding**: `bge-m3:latest` (1024 boyutlu vektörler)
- **LLM**: `llama3.1:8b` (Türkçe destekli)

---

## 📦 Kurulum

### 1. Gereksinimler

#### Python Paketleri
```bash
pip install -r requirements.txt
```

#### Tesseract OCR Kurulumu
**Windows:**
```bash
# Tesseract'i indirin ve kurun:
# https://github.com/UB-Mannheim/tesseract/wiki
# Türkçe dil paketi dahil edilmelidir
```

**Linux/Mac:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-tur
```

#### Ollama Kurulumu
```bash
# Ollama'yı indirin: https://ollama.ai

# Gerekli modelleri çekin:
ollama pull bge-m3:latest
ollama pull llama3.1:8b
```

### 2. Proje Yapılandırması

```bash
# Belgeler klasörünü oluşturun (otomatik oluşturulur)
mkdir belgeler

# LanceDB klasörü otomatik oluşturulacaktır
```

---

## 🚀 Kullanım

### Ana Uygulama

```bash
python main.py
```

**Ne yapar?**
1. `belgeler/` klasöründeki tüm PDF'leri tarar ve işler
2. Yeni eklenen PDF'leri otomatik olarak izler
3. Soru-cevap arayüzünü başlatır

**Örnek Kullanım:**
```
You: Hacettepe Üniversitesi YZ bölümü ne zaman kuruldu?

System:
Hacettepe Üniversitesi Yapay Zeka Mühendisliği bölümü 2019 yılında kurulmuştur.

**Kaynaklar:**
yonetmelik.pdf

**Kullanılan Chunklar:**
[1] (yonetmelik.pdf):
Madde 1 - Hacettepe Üniversitesi Yapay Zeka Mühendisliği bölümü...
```

### Veritabanı Yönetimi

```bash
# Tüm indekslenmiş belgeleri listele
python manage_db.py list

# Belirli bir PDF'i manuel olarak ekle
python manage_db.py add belgeler/yeni_belge.pdf

# Bir belgeyi veritabanından sil
python manage_db.py delete yonetmelik.pdf
```

### Pipeline Doğrulama

```bash
# Tüm pipeline'ı test et
python verify_pipeline.py

# Chunking'i test et
python test_chunker.py

# PDF loader'ı debug et
python debug_pdf_loader.py
```

---

## 📁 Proje Yapısı

```
hacettepe_llm-1/
│
├── main.py                    # Ana uygulama (watchdog + chat loop)
├── config.py                  # Tüm konfigürasyon ayarları
├── requirements.txt           # Python bağımlılıkları
│
├── pipeline/                  # İşleme hattı modülleri
│   ├── pdf_loader.py         # PDF okuma + OCR
│   ├── text_cleaner.py       # Metin temizleme
│   ├── chunker.py            # Dinamik chunking
│   ├── embedder.py           # Ollama embedding
│   ├── vector_store.py       # LanceDB işlemleri
│   └── rag_engine.py         # RAG soru-cevap motoru
│
├── belgeler/                  # PDF belgelerin konulacağı klasör
│   └── (PDF dosyaları)
│
├── lancedb_data/             # LanceDB vektör veritabanı
│   └── vectors.lance/
│
├── manage_db.py              # Veritabanı yönetim aracı
├── verify_pipeline.py        # Pipeline test aracı
├── test_chunker.py           # Chunker test aracı
└── debug_pdf_loader.py       # PDF loader debug aracı
```

---

## ⚙️ Çalışma Mantığı

### 1️⃣ PDF İşleme Pipeline

#### **A. PDF Loader** (`pipeline/pdf_loader.py`)
```python
PDF Dosyası
    ↓
PyMuPDF ile metin çıkarma
    ↓
Metin yeterli mi? (>50 karakter)
    ├─ EVET → Metni döndür
    └─ HAYIR → OCR ile tekrar oku (pytesseract)
```

**Özellikler:**
- Hem dijital hem taranmış PDF desteği
- Türkçe + İngilizce OCR
- Sayfa sayfa işleme

#### **B. Text Cleaner** (`pipeline/text_cleaner.py`)
```python
Ham Metin
    ↓
Unicode normalizasyonu (NFKC)
    ↓
Sayfa numaralarını kaldır
    ↓
Header/Footer temizleme
    ↓
Satır birleştirme (hyphenation fix)
    ↓
"Madde" sınırlarını koru
    ↓
Temiz Metin
```

**Özellikler:**
- Akıllı satır birleştirme
- "Madde X", "1.", "a)" gibi yapıları koruma
- Gereksiz boşlukları temizleme

#### **C. Chunker** (`pipeline/chunker.py`) - **Semantic Chunking** ✨
```python
Temiz Metin
    ↓
"Madde X" veya "1." ile bölümlere ayır (Structured Data)
    ↓
Her bölüm > 4000 karakter mi?
    ├─ EVET → Semantic Sliding Window uygula
    └─ HAYIR → Olduğu gibi bırak
    ↓
Semantic Sliding Window (Unstructured Data için):
    ├─ 1. Öncelik: Paragraf sonu (\n\n)
    ├─ 2. Öncelik: Cümle sonu (. ! ?)
    ├─ 3. Öncelik: Kelime sonu (boşluk)
    └─ Son çare: Karakter limiti
    ↓
Chunk Listesi
```

**Parametreler:**
- `CHUNK_SIZE`: 4000 karakter (maksimum)
- `CHUNK_OVERLAP`: 200 karakter (context korunması için)

**Semantic Chunking Özellikleri:**

1. **Structured Data (Maddeli Belgeler):**
   - "Madde 1", "Madde 2" gibi bölümler otomatik algılanır
   - Her madde ayrı chunk olur
   - Çok uzun maddeler semantic olarak bölünür

2. **Unstructured Data (Düz Metin):**
   - ✅ **Paragraf sınırlarını korur** - Chunk'lar paragraf sonlarında kesilir
   - ✅ **Cümle bütünlüğünü korur** - Cümle ortasında kesmez
   - ✅ **Kelime bütünlüğünü korur** - Asla kelime ortasında kesmez
   - ✅ **Context overlap** - Chunk'lar arası 200 karakter overlap ile anlam korunur

**Örnek:**

```python
# Eski Yöntem (Karakter bazlı):
Chunk 1: "...Hacettepe Üniversitesi Ankara'da kurulmuştur. Bir"
Chunk 2: "çok fakültesi vardır..."  # ❌ "Birçok" kelimesi kesildi!

# Yeni Yöntem (Semantic):
Chunk 1: "...Hacettepe Üniversitesi Ankara'da kurulmuştur. "
Chunk 2: "Birçok fakültesi vardır..."  # ✅ Cümle sınırında kesildi!
```

**Test:**
```bash
python test_semantic_chunking.py  # Semantic chunking'i test et
```

#### **D. Embedder** (`pipeline/embedder.py`)
```python
Her Chunk
    ↓
Ollama API'ye gönder (bge-m3)
    ↓
1024 boyutlu vektör al
    ↓
Retry mekanizması (3 deneme)
    ↓
Embedding Vektörü
```

**Özellikler:**
- Otomatik retry (3 deneme)
- 2 saniye bekleme süresi
- Hata durumunda None döndürme

#### **E. Vector Store** (`pipeline/vector_store.py`)
```python
Chunk + Embedding + Metadata
    ↓
LanceDB'ye kaydet
    ↓
Schema:
  - id: UUID
  - text: Chunk metni
  - embedding: [1024 float]
  - source: PDF dosya adı
  - metadata: JSON string
```

**Özellikler:**
- Otomatik tablo oluşturma
- Duplicate kontrolü (dosya adı bazlı)
- Silme ve arama işlemleri

---

### 2️⃣ RAG (Soru-Cevap) Sistemi

#### **Retrieval (Bilgi Getirme)**
```python
Kullanıcı Sorusu
    ↓
Soru → Embedding (bge-m3)
    ↓
LanceDB'de vektör araması
    ↓
En yakın TOP_K chunk'ı getir (varsayılan: 5)
    ↓
Context Oluştur
```

#### **Generation (Yanıt Üretme)**
```python
Context + Soru
    ↓
System Prompt ile birleştir
    ↓
Ollama LLM'e gönder (llama3.1:8b)
    ↓
Yanıt + Kaynaklar + Chunk'lar
```

**System Prompt Kuralları:**
1. ✅ Sadece verilen context'i kullan
2. ❌ Uydurma yapma
3. ✅ Kısa, öz, akademik dil
4. ❌ Politik/dini/tıbbi konulara girme
5. ✅ Kaynak göster

---

## 🗄️ Veritabanı Yönetimi

### LanceDB Yapısı

```
lancedb_data/
└── vectors.lance/
    ├── data/           # Vektör verileri
    ├── index/          # Arama indeksi
    └── metadata/       # Şema bilgileri
```

### Yönetim Komutları

```bash
# Tüm belgeleri listele
python manage_db.py list
# Çıktı:
# Indexed Documents (3):
# - yonetmelik.pdf (45 chunks)
# - ders_programi.pdf (23 chunks)
# - sinav_takvimi.pdf (12 chunks)

# Yeni belge ekle
python manage_db.py add belgeler/yeni_belge.pdf

# Belge sil
python manage_db.py delete yonetmelik.pdf
```

---

## 🔧 Konfigürasyon

### `config.py` Ayarları

```python
# Dizinler
DOCS_DIR = "belgeler/"              # PDF klasörü
LANCEDB_URI = "lancedb_data/"       # Veritabanı konumu

# Ollama Ayarları
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "bge-m3:latest"   # 1024-dim embedding
LLM_MODEL = "llama3.1:8b"           # Türkçe destekli

# Chunking Parametreleri
CHUNK_SIZE = 4000                   # Maksimum chunk boyutu
CHUNK_OVERLAP = 200                 # Overlap miktarı

# RAG Parametreleri
TOP_K = 5                           # Kaç chunk getirilecek
MIN_SCORE_THRESHOLD = 0.35          # Minimum benzerlik skoru

# Retry Ayarları
MAX_RETRIES = 3                     # Maksimum deneme sayısı
RETRY_DELAY = 2                     # Saniye cinsinden bekleme
```

### Model Değiştirme

```python
# Farklı embedding modeli kullanmak için:
EMBEDDING_MODEL = "nomic-embed-text:latest"

# Farklı LLM kullanmak için:
LLM_MODEL = "mistral:latest"
```

---

## 🧪 Test ve Doğrulama

### Pipeline Testi
```bash
python verify_pipeline.py
```

**Test Adımları:**
1. ✅ Dummy PDF oluşturma
2. ✅ PDF okuma
3. ✅ Metin temizleme
4. ✅ Chunking
5. ✅ Embedding API bağlantısı
6. ✅ Vektör kaydetme
7. ✅ RAG soru-cevap

### Chunker Testi
```bash
python test_chunker.py
```

Örnek metin ile chunking algoritmasını test eder.

---

## 📊 Performans ve Optimizasyon

### Önerilen Ayarlar

| Belge Sayısı | TOP_K | CHUNK_SIZE | Beklenen Yanıt Süresi |
|--------------|-------|------------|-----------------------|
| 1-10         | 3     | 3000       | 2-5 saniye           |
| 10-50        | 5     | 4000       | 5-10 saniye          |
| 50+          | 7     | 5000       | 10-15 saniye         |

### Hız İyileştirme İpuçları

1. **GPU Kullanımı**: Ollama'yı GPU ile çalıştırın
2. **Chunk Boyutu**: Daha küçük chunk'lar = daha hızlı arama
3. **TOP_K Azaltma**: Daha az context = daha hızlı yanıt
4. **Model Seçimi**: Daha küçük modeller daha hızlıdır

---

## 🐛 Sorun Giderme

### Sık Karşılaşılan Hatalar

#### 1. Ollama Bağlantı Hatası
```
Error: Connection refused to http://127.0.0.1:11434
```
**Çözüm:**
```bash
# Ollama'nın çalıştığından emin olun
ollama serve
```

#### 2. Tesseract Bulunamadı
```
Error: pytesseract.TesseractNotFoundError
```
**Çözüm:**
```bash
# Windows: PATH'e Tesseract ekleyin
# Linux: sudo apt-get install tesseract-ocr
```

#### 3. LanceDB Şema Hatası
```
Error: Schema mismatch
```
**Çözüm:**
```bash
# Veritabanını sıfırlayın
rm -rf lancedb_data/
python main.py  # Yeniden oluşturulacak
```

---

## 📝 Lisans

Bu proje Hacettepe Üniversitesi için geliştirilmiştir.

---

## 👥 Katkıda Bulunma

Proje geliştirmeleri için:
1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Commit yapın (`git commit -m 'Yeni özellik eklendi'`)
4. Push yapın (`git push origin feature/yeniOzellik`)
5. Pull Request açın

---

## 📞 İletişim

Sorularınız için proje yöneticisi ile iletişime geçin.

---

**Son Güncelleme:** 2025-12-11  
**Versiyon:** 1.3 (Enhanced Entity Extraction + Hybrid RAG + Query Caching + Semantic Chunking ✨)
# hacettepe_ai

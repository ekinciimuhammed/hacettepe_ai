import re
from config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text, max_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Geliştirilmiş semantic chunking stratejisi:
    1. Önce yapılandırılmış bölümleri yakala (Madde, numaralı listeler)
    2. Yapılandırılmamış veriler için semantic-aware chunking
    3. Kelime/cümle ortasında kesme yapmaktan kaçın
    """
    if not text:
        return []

    # Yapılandırılmış bölümleri yakala
    # Pattern: Madde X, 1., a) gibi yapılar
    split_pattern = r'(Madde \d+|^\d+\.|^\s*[a-z]\))'
    
    parts = re.split(split_pattern, text, flags=re.MULTILINE | re.IGNORECASE)
    
    chunks = []
    current_chunk = ""
    
    # İlk kısım (preamble/başlangıç metni)
    if parts:
        current_chunk = parts[0]
    
    # Yapılandırılmış bölümleri işle
    for i in range(1, len(parts), 2):
        header = parts[i]
        content = parts[i+1] if i+1 < len(parts) else ""
        
        full_section = header + content
        
        # Önceki chunk'ı kaydet
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Büyük bölümler için semantic chunking kullan
        if len(full_section) > max_size:
            # Semantic-aware sliding window
            sub_chunks = semantic_sliding_window(full_section, max_size, overlap)
            chunks.extend(sub_chunks)
            current_chunk = ""
        else:
            current_chunk = full_section
                
    # Kalan chunk'ı ekle
    if current_chunk.strip():
        # Eğer yapılandırılmamış veri çok büyükse semantic chunking uygula
        if len(current_chunk) > max_size:
            sub_chunks = semantic_sliding_window(current_chunk, max_size, overlap)
            chunks.extend(sub_chunks)
        else:
            chunks.append(current_chunk.strip())
        
    return chunks

def semantic_sliding_window(text, chunk_size, overlap):
    """
    Semantic-aware sliding window chunking:
    - Paragraf sınırlarını tercih eder (\n\n)
    - Cümle sınırlarını tercih eder (. ! ?)
    - Kelime sınırlarını tercih eder (boşluk)
    - Asla kelime ortasında kesmez
    
    Bu sayede unstructured data için daha anlamlı chunk'lar oluşturulur.
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        # Hedef bitiş noktası
        end = min(start + chunk_size, text_len)
        
        # Son chunk ise olduğu gibi al
        if end >= text_len:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break
        
        # Akıllı kesim noktası bul (paragraf/cümle/kelime sınırı)
        cut_point = find_best_cut_point(text, start, end, chunk_size)
        
        # Chunk'ı ekle
        chunk = text[start:cut_point].strip()
        if chunk:
            chunks.append(chunk)
        
        # Overlap ile ilerle (context korunması için)
        start = cut_point - overlap
        
        # Sonsuz döngüyü önle
        if start < cut_point - chunk_size:
            start = cut_point
    
    return chunks

def find_best_cut_point(text, start, end, chunk_size):
    """
    En iyi kesim noktasını bulur (öncelik sırasına göre):
    1. Paragraf sonu (\n\n) - En yüksek öncelik
    2. Cümle sonu (. ! ?) - Orta öncelik
    3. Kelime sonu (boşluk) - Düşük öncelik
    4. Son çare: orijinal end noktası
    
    Arama stratejisi: Chunk'un son %20-30'luk kısmında ara
    """
    search_window = text[start:end]
    window_len = len(search_window)
    
    # Strategi 1: Paragraf sonu ara (son %20'lik kısımda)
    search_start = int(window_len * 0.8)
    paragraph_matches = list(re.finditer(r'\n\n+', search_window[search_start:]))
    if paragraph_matches:
        # İlk paragraf sonunu al
        return start + search_start + paragraph_matches[0].end()
    
    # Strategi 2: Cümle sonu ara (son %30'luk kısımda)
    search_start = int(window_len * 0.7)
    sentence_matches = list(re.finditer(r'[.!?]\s+', search_window[search_start:]))
    if sentence_matches:
        # Son cümle sonunu al
        return start + search_start + sentence_matches[-1].end()
    
    # Strategi 3: Kelime sonu ara (son %10'luk kısımda)
    search_start = int(window_len * 0.9)
    word_matches = list(re.finditer(r'\s+', search_window[search_start:]))
    if word_matches:
        # Son kelime sonunu al
        return start + search_start + word_matches[-1].end()
    
    # Strategi 4: Tüm metinde kelime sonu ara (son çare)
    all_word_matches = list(re.finditer(r'\s+', search_window))
    if all_word_matches:
        return start + all_word_matches[-1].end()
    
    # Son çare: orijinal end noktası (boşluk yoksa)
    return end

def sliding_window(text, chunk_size, overlap):
    """
    Eski sliding window fonksiyonu - geriye uyumluluk için korundu.
    Artık semantic_sliding_window kullanılıyor.
    """
    return semantic_sliding_window(text, chunk_size, overlap)

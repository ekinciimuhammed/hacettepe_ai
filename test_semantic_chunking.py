"""
Semantic Chunking Test Script
Bu script, yeni semantic chunking algoritmasının nasıl çalıştığını gösterir.
"""

from pipeline.chunker import chunk_text

# Test 1: Maddeli Belge (Structured Data)
print("=" * 80)
print("TEST 1: MADDELİ BELGE (STRUCTURED DATA)")
print("=" * 80)

structured_text = """
Madde 1 - Bu yönetmelik Hacettepe Üniversitesi'nde uygulanır. Amaç öğrencilerin haklarını korumaktır.

Madde 2 - Kapsam şunlardır: Tüm lisans ve lisansüstü öğrenciler bu yönetmelik kapsamındadır. Öğrenciler haklarını kullanabilir.

Madde 3 - """ + "A" * 5000 + """ Bu çok uzun bir maddedir ve semantic chunking ile bölünecektir. Cümle sonlarına dikkat edilecektir. Paragraflar korunacaktır.

Madde 4 - Son madde kısa bir maddedir.
"""

chunks = chunk_text(structured_text)
print(f"\nToplam {len(chunks)} chunk oluşturuldu:\n")
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i} ({len(chunk)} karakter):")
    print(f"  Başlangıç: {chunk[:50]}...")
    print(f"  Bitiş: ...{chunk[-50:]}")
    print()

# Test 2: Yapılandırılmamış Belge (Unstructured Data)
print("=" * 80)
print("TEST 2: YAPILANDIRILMAMIŞ BELGE (UNSTRUCTURED DATA)")
print("=" * 80)

unstructured_text = """
Hacettepe Üniversitesi, Türkiye'nin en köklü üniversitelerinden biridir. Ankara'da kurulmuştur.

Üniversite birçok fakülteye sahiptir. Tıp Fakültesi çok ünlüdür. Mühendislik Fakültesi de önemlidir.

""" + "Yapay Zeka Mühendisliği bölümü yenilikçi bir bölümdür. " * 200 + """

Üniversite kampüsü çok geniştir. Öğrenciler için birçok imkan vardır. Kütüphane çok büyüktür.

Sosyal aktiviteler de çok çeşitlidir. Öğrenci kulüpleri aktiftir.
"""

chunks = chunk_text(unstructured_text)
print(f"\nToplam {len(chunks)} chunk oluşturuldu:\n")
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i} ({len(chunk)} karakter):")
    print(f"  Başlangıç: {chunk[:80]}...")
    print(f"  Bitiş: ...{chunk[-80:]}")
    
    # Kesim noktasını kontrol et
    if i < len(chunks):
        last_chars = chunk[-20:]
        print(f"  Son 20 karakter: '{last_chars}'")
        
        # Semantic kesim kontrolü
        if '\n\n' in last_chars:
            print(f"  ✅ Paragraf sınırında kesildi")
        elif any(p in last_chars for p in ['. ', '! ', '? ']):
            print(f"  ✅ Cümle sınırında kesildi")
        elif ' ' in last_chars:
            print(f"  ✅ Kelime sınırında kesildi")
        else:
            print(f"  ⚠️ Kelime ortasında kesilmiş olabilir")
    print()

# Test 3: Karşılaştırma - Eski vs Yeni Chunking
print("=" * 80)
print("TEST 3: ESKİ vs YENİ CHUNKING KARŞILAŞTIRMASI")
print("=" * 80)

test_text = "Bu bir test metnidir. " * 300  # 6900 karakter

# Yeni semantic chunking
from pipeline.chunker import semantic_sliding_window
semantic_chunks = semantic_sliding_window(test_text, 4000, 200)

print(f"\nSemantic Chunking: {len(semantic_chunks)} chunk")
for i, chunk in enumerate(semantic_chunks, 1):
    last_10 = chunk[-10:]
    print(f"  Chunk {i}: {len(chunk)} karakter, son 10: '{last_10}'")

# Eski basit chunking (karakter bazlı)
def old_sliding_window(text, chunk_size, overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += (chunk_size - overlap)
    return chunks

old_chunks = old_sliding_window(test_text, 4000, 200)
print(f"\nEski Chunking: {len(old_chunks)} chunk")
for i, chunk in enumerate(old_chunks, 1):
    last_10 = chunk[-10:]
    print(f"  Chunk {i}: {len(chunk)} karakter, son 10: '{last_10}'")

print("\n" + "=" * 80)
print("SONUÇ: Semantic chunking cümle/kelime sınırlarında keserken,")
print("eski yöntem rastgele karakterde kesiyordu.")
print("=" * 80)

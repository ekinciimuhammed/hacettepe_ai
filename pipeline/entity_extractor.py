"""
Basit Entity Extractor - Türkçe Akademik Belgeler İçin
Regex tabanlı entity extraction (NER olmadan)
"""

import re
from typing import Dict, List

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Metinden entity'leri çıkarır (regex tabanlı)
    
    Args:
        text: Analiz edilecek metin
        
    Returns:
        Entity dictionary:
        {
            "universities": [...],
            "faculties": [...],
            "departments": [...],
            "dates": [...],
            "locations": [...],
            "people": [...]
        }
    """
    entities = {
        "universities": [],
        "faculties": [],
        "departments": [],
        "programs": [],          # YENİ: Akademik programlar
        "courses": [],           # YENİ: Ders isimleri
        "institutes": [],        # YENİ: Enstitüler
        "research_centers": [],  # YENİ: Araştırma merkezleri
        "dates": [],
        "locations": [],
        "madde_numbers": []
    }
    
    # 1. Üniversite isimleri
    uni_patterns = [
        r'Hacettepe\s+Üniversitesi',
        r'Hacettepe',
        r'H\.Ü\.',
        r'HÜ'
    ]
    for pattern in uni_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities["universities"].extend(matches)
    
    # 2. Fakülte isimleri
    faculty_pattern = r'((?:\w+\s+){0,3}Fakültesi)'
    faculties = re.findall(faculty_pattern, text)
    entities["faculties"] = [f.strip() for f in faculties if len(f.strip()) > 5]
    
    # 3. Bölüm isimleri
    dept_patterns = [
        r'((?:\w+\s+){0,3}Mühendisliği)',
        r'((?:\w+\s+){0,3}Bölümü)',
        r'((?:\w+\s+){0,3}Anabilim Dalı)'
    ]
    for pattern in dept_patterns:
        matches = re.findall(pattern, text)
        entities["departments"].extend([m.strip() for m in matches if len(m.strip()) > 5])
    
    # 4. Tarihler
    date_patterns = [
        r'\b(19\d{2}|20\d{2})\b',  # Yıl (1900-2099)
        r'\b(\d{1,2}[./]\d{1,2}[./]\d{2,4})\b',  # Tarih (DD/MM/YYYY)
        r'\b(\d{1,2}\s+(?:Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+\d{4})\b'  # Uzun format
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities["dates"].extend(matches)
    
    # 5. Lokasyonlar (Geliştirilmiş - Hybrid RAG PDF önerisi)
    location_patterns = [
        r'\b(Ankara|İstanbul|İzmir|Bursa|Antalya)\b',
        r'\b(Sıhhiye|Beytepe|Keçiören|Polatlı)\b',  # Hacettepe yerleşkeleri
        r'\b(Türkiye|Turkey)\b',
        r'\b(Kampüs|Yerleşke)\b',
        r'(Beytepe Yerleşkesi|Sıhhiye Yerleşkesi|Polatlı Yerleşkesi)'
    ]
    for pattern in location_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities["locations"].extend(matches)
    
    # 6. Kişi isimleri - KALDIRILDI (Fakülte/Bölüm isimleriyle karışıyor)
    
    # 7. Madde numaraları (Yönetmelikler için)
    madde_pattern = r'Madde\s+(\d+)'
    madde_numbers = re.findall(madde_pattern, text, re.IGNORECASE)
    entities["madde_numbers"] = madde_numbers
    
    # 8. Programlar (YENİ - Hybrid RAG PDF önerisi)
    program_patterns = [
        r'((?:\w+\s+){0,4}Programı)',
        r'((?:\w+\s+){0,4}Program)',
        r'(Lisans Programı|Yüksek Lisans Programı|Doktora Programı)',
        r'(Önlisans Programı|Lisansüstü Program)'
    ]
    for pattern in program_patterns:
        matches = re.findall(pattern, text)
        entities["programs"].extend([m.strip() for m in matches if len(m.strip()) > 5])
    
    # 9. Dersler (YENİ)
    course_patterns = [
        r'((?:\w+\s+){0,4}Dersi)',
        r'((?:\w+\s+){0,4}Kursu)'
    ]
    for pattern in course_patterns:
        matches = re.findall(pattern, text)
        entities["courses"].extend([m.strip() for m in matches if len(m.strip()) > 5])
    
    # 10. Enstitüler (YENİ - Hybrid RAG PDF önerisi)
    institute_patterns = [
        r'((?:\w+\s+){0,4}Enstitüsü)',
        r'(Aşı Enstitüsü|Bilişim Enstitüsü|Kanser Enstitüsü|Nükleer Bilimler Enstitüsü)',
        r'(Nüfus Etütleri Enstitüsü|Sağlık Bilimleri Enstitüsü|Fen Bilimleri Enstitüsü)',
        r'(Sosyal Bilimler Enstitüsü|Eğitim Bilimleri Enstitüsü|Türkiyat Araştırmaları Enstitüsü)'
    ]
    for pattern in institute_patterns:
        matches = re.findall(pattern, text)
        entities["institutes"].extend([m.strip() for m in matches if len(m.strip()) > 5])
    
    # 11. Araştırma Merkezleri (YENİ - Hybrid RAG PDF önerisi)
    center_patterns = [
        # Kısaltmalar (PDF'de geçen önemli merkezler)
        r'\b(HATAM|HÜNİTEK|HÜNİKAL|IONOLAB|PDRMER)\b',
        # Özel tam isimler (önce spesifik olanlar)
        r'(İleri Teknolojiler Uygulama ve Araştırma Merkezi)',
        r'(HIV-AIDS Tedavi ve Araştırma Merkezi)',
        r'(İlaç ve Kozmetik Ar-Ge Laboratuvarı)',
        r'(Nörolojik ve Psikiyatrik Uygulama Merkezi)',
        r'(Hareket Analizi ve Podiatri Merkezi)',
        # Genel pattern (en sona)
        r'((?:\w+\s+){0,6}(?:Merkezi|Uygulama ve Araştırma Merkezi|Araştırma Merkezi))',
        r'(Teknokent|Hacettepe Teknokent)',
        r'((?:\w+\s+){0,4}Laboratuvarı)'
    ]
    for pattern in center_patterns:
        matches = re.findall(pattern, text)
        entities["research_centers"].extend([m.strip() for m in matches if len(m.strip()) > 5])

    
    # Tekrarları kaldır ve küçük harf yap (case-insensitive comparison için)
    for key in entities:
        entities[key] = list(set(entities[key]))
    
    return entities

def calculate_entity_overlap(query_entities: Dict, chunk_entities: Dict) -> float:
    """
    İki entity seti arasındaki overlap skorunu hesaplar
    
    Args:
        query_entities: Soru entity'leri
        chunk_entities: Chunk entity'leri
        
    Returns:
        Overlap skoru (0.0 - 1.0)
    """
    total_overlap = 0
    total_query_entities = 0
    
    # Her entity tipi için overlap hesapla (Güncellenmiş ağırlıklar - Hybrid RAG PDF)
    weights = {
        "universities": 2.0,        # Üniversite ismi çok önemli
        "institutes": 1.8,          # YENİ: Enstitüler çok önemli (araştırma sorguları için)
        "research_centers": 1.7,    # YENİ: Araştırma merkezleri çok önemli
        "programs": 1.6,            # YENİ: Programlar önemli
        "faculties": 1.5,           # Fakülte önemli
        "departments": 1.5,         # Bölüm önemli
        "courses": 1.4,             # YENİ: Dersler önemli
        "madde_numbers": 1.3,       # Madde numaraları önemli
        "dates": 1.0,               # Tarih orta önemli
        "locations": 1.0            # Lokasyon orta önemli
    }
    
    for entity_type in query_entities:
        query_set = set([e.lower() for e in query_entities[entity_type]])
        chunk_set = set([e.lower() for e in chunk_entities.get(entity_type, [])])
        
        if not query_set:
            continue
        
        # Overlap sayısı
        overlap = len(query_set & chunk_set)
        weight = weights.get(entity_type, 1.0)
        
        total_overlap += overlap * weight
        total_query_entities += len(query_set) * weight
    
    # Normalize et
    if total_query_entities == 0:
        return 0.0
    
    return min(total_overlap / total_query_entities, 1.0)

def extract_relations(text: str, entities: Dict) -> List[tuple]:
    """
    Basit relation extraction (entity'ler arası ilişkiler)
    
    Returns:
        List of (subject, relation, object) tuples
    """
    relations = []
    
    # Basit pattern'ler
    patterns = [
        (r'(\w+)\s+(?:bulunur|yer alır|konumlanır)\s+(\w+)', "BULUNUR"),
        (r'(\w+)\s+(?:kuruldu|açıldı|başladı)\s+(\d{4})', "KURULDU"),
        (r'(\w+)\s+(?:sahiptir|vardır)\s+(\w+)', "SAHİP"),
        (r'(\w+)\s+(?:bağlıdır|aittir)\s+(\w+)', "BAĞLI"),
    ]
    
    for pattern, relation_type in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) == 2:
                relations.append((match[0], relation_type, match[1]))
    
    return relations

# Test fonksiyonu
if __name__ == "__main__":
    test_text = """
    Hacettepe Üniversitesi 1967 yılında Ankara'da kurulmuştur. 
    Tıp Fakültesi çok ünlüdür. Yapay Zeka Mühendisliği Bölümü 2019'da açılmıştır.
    Prof. Dr. Mehmet Yılmaz dekan olarak görev yapmaktadır.
    Madde 1 - Bu yönetmelik Sıhhiye kampüsünde uygulanır.
    
    Aşı Enstitüsü pandemi süreçlerinde stratejik öneme sahiptir.
    HÜNİTEK araştırma laboratuvarı teknolojik altyapı sağlar.
    Yapay Zeka Mühendisliği Programı Mühendislik Fakültesinde yer alır.
    Veri Yapıları Dersi zorunlu derslerden biridir.
    Beytepe Yerleşkesi'nde Teknokent bulunmaktadır.
    """
    
    entities = extract_entities(test_text)
    print("Extracted Entities:")
    for entity_type, values in entities.items():
        if values:
            print(f"  {entity_type}: {values}")
    
    relations = extract_relations(test_text, entities)
    print("\nExtracted Relations:")
    for rel in relations:
        print(f"  {rel[0]} --{rel[1]}--> {rel[2]}")

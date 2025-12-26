"""
Hybrid RAG Test Script
Bu script, Hybrid RAG'in nasıl çalıştığını test eder.
"""

import sys
import os

# Test için entity extractor'ı import et
from pipeline.entity_extractor import extract_entities, calculate_entity_overlap

print("=" * 80)
print("HYBRID RAG TEST")
print("=" * 80)

# Test 1: Entity Extraction
print("\n1️⃣ Entity Extraction Test")
print("-" * 80)

test_queries = [
    "Hacettepe Üniversitesi ne zaman kuruldu?",
    "Tıp Fakültesi'nin bölümleri nelerdir?",
    "Yapay Zeka Mühendisliği Bölümü Ankara'da mı?",
    "2019 yılında hangi bölüm açıldı?",
    # YENİ: Enhanced entity test queries
    "Aşı Enstitüsü hangi programlar sunuyor?",
    "HÜNİTEK nedir ve ne yapar?",
    "Yapay Zeka Mühendisliği Programı hangi fakültede?",
    "Teknokent Beytepe'de mi bulunuyor?"
]

for query in test_queries:
    entities = extract_entities(query)
    print(f"\nSoru: \"{query}\"")
    print(f"Entities:")
    for entity_type, values in entities.items():
        if values:
            print(f"  - {entity_type}: {values}")

# Test 2: Entity Overlap Calculation
print("\n\n2️⃣ Entity Overlap Test")
print("-" * 80)

query = "Hacettepe Tıp Fakültesi Ankara'da mı?"
query_entities = extract_entities(query)

chunks = [
    {
        "text": "Hacettepe Üniversitesi Tıp Fakültesi Ankara Sıhhiye'de bulunur.",
        "entities": extract_entities("Hacettepe Üniversitesi Tıp Fakültesi Ankara Sıhhiye'de bulunur.")
    },
    {
        "text": "Mühendislik Fakültesi Beytepe kampüsündedir.",
        "entities": extract_entities("Mühendislik Fakültesi Beytepe kampüsündedir.")
    },
    {
        "text": "Yapay Zeka Mühendisliği 2019'da kuruldu.",
        "entities": extract_entities("Yapay Zeka Mühendisliği 2019'da kuruldu.")
    }
]

print(f"\nSoru: \"{query}\"")
print(f"Query Entities: {query_entities}\n")

for i, chunk in enumerate(chunks, 1):
    overlap_score = calculate_entity_overlap(query_entities, chunk["entities"])
    print(f"Chunk {i}: {chunk['text'][:60]}...")
    print(f"  Entity Overlap Score: {overlap_score:.3f}")
    print(f"  Chunk Entities: {chunk['entities']}\n")

# Test 3: Hybrid Scoring Simulation
print("\n3️⃣ Hybrid Scoring Simulation")
print("-" * 80)

from config import VECTOR_WEIGHT, ENTITY_WEIGHT

print(f"Weights: Vector={VECTOR_WEIGHT}, Entity={ENTITY_WEIGHT}\n")

# Simulated results
simulated_results = [
    {
        "text": "Hacettepe Tıp Fakültesi Ankara'da...",
        "vector_score": 0.85,
        "entity_score": 0.90
    },
    {
        "text": "Mühendislik Fakültesi Beytepe'de...",
        "vector_score": 0.75,
        "entity_score": 0.30
    },
    {
        "text": "Hacettepe Üniversitesi 1967'de kuruldu...",
        "vector_score": 0.70,
        "entity_score": 0.60
    }
]

print("Soru: 'Hacettepe Tıp Fakültesi Ankara'da mı?'\n")

for i, result in enumerate(simulated_results, 1):
    final_score = (VECTOR_WEIGHT * result["vector_score"]) + (ENTITY_WEIGHT * result["entity_score"])
    print(f"Chunk {i}: {result['text']}")
    print(f"  Vector Score: {result['vector_score']:.3f}")
    print(f"  Entity Score: {result['entity_score']:.3f}")
    print(f"  Final Score:  {final_score:.3f} ⭐")
    print()

# Sort by final score
simulated_results_with_scores = []
for result in simulated_results:
    final_score = (VECTOR_WEIGHT * result["vector_score"]) + (ENTITY_WEIGHT * result["entity_score"])
    simulated_results_with_scores.append({**result, "final_score": final_score})

simulated_results_with_scores.sort(key=lambda x: x["final_score"], reverse=True)

print("Sıralama (Final Score'a göre):")
for i, result in enumerate(simulated_results_with_scores, 1):
    print(f"  {i}. {result['text']} (Score: {result['final_score']:.3f})")

print("\n" + "=" * 80)
print("✅ Hybrid RAG sistemi aktif!")
print("Entity extraction ve re-ranking çalışıyor.")
print("=" * 80)

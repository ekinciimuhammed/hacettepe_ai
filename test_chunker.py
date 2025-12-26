from pipeline.chunker import chunk_text
from config import CHUNK_SIZE

def test_dynamic_chunking():
    print(f"Testing Dynamic Chunking with Max Size: {CHUNK_SIZE}")
    
    # Text with clear "Madde" boundaries
    text = """
    GIRIS
    Bu bir giris metnidir.
    
    Madde 1
    Bu birinci maddedir. Kisa ve oz.
    
    Madde 2
    Bu ikinci maddedir. Biraz daha uzundur.
    Icerigi devam ediyor.
    
    3. Bolum
    Burasi baska bir format.
    """
    
    chunks = chunk_text(text)
    print(f"--- Standard Test ---")
    for i, c in enumerate(chunks):
        print(f"Chunk {i+1}:\n---\n{c}\n---\n")
        
    # Text with HUGE section to test fallback
    huge_text = "Madde 3\n" + ("A" * (CHUNK_SIZE + 100))
    chunks_huge = chunk_text(huge_text)
    print(f"--- Overflow Test ---")
    print(f"Input len: {len(huge_text)}")
    print(f"Generated {len(chunks_huge)} chunks.")
    print(f"Chunk 1 len: {len(chunks_huge[0])}")
    if len(chunks_huge) > 1:
        print(f"Chunk 2 len: {len(chunks_huge[1])}")

if __name__ == "__main__":
    test_dynamic_chunking()

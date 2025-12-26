import fitz
import sys

pdf_path = r"belgeler/Hacettepe Bölümleri ve Hibrit RAG.pdf"

try:
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    full_text = ""
    
    for page_num in range(num_pages):
        page = doc[page_num]
        text = page.get_text()
        full_text += f"\n--- PAGE {page_num + 1} ---\n{text}\n"
    
    # Write to file BEFORE closing doc
    with open("hybrid_pdf_full.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    
    doc.close()
    
    print(f"Successfully extracted {num_pages} pages")
    print(f"Total characters: {len(full_text)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

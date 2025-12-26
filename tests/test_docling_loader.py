import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.docling_loader import DoclingLoader

class TestDoclingLoader(unittest.TestCase):
    def test_loader_exists(self):
        loader = DoclingLoader()
        self.assertIsNotNone(loader)
        
    def test_load_real_pdf(self):
        # We will test with the known document
        test_file = os.path.join("belgeler", "Hacettepe Üniversitesi Ön Lisans-Lisans Mezunlarının Akademik Başarı Sıralaması ve Verilecek Belgel.pdf")
        
        if not os.path.exists(test_file):
            print(f"Skipping real PDF test, file not found: {test_file}")
            return

        loader = DoclingLoader()
        blocks = loader.load(test_file)
        
        self.assertTrue(len(blocks) > 0, "Should extract blocks")
        
        # Check first block structure
        first = blocks[0]
        self.assertIn("text", first)
        self.assertIn("type", first)
        self.assertIn("page", first)
        
        print(f"\nExtracted {len(blocks)} blocks.")
        print("Sample blocks:")
        for b in blocks[:5]:
            print(f"- [{b['type']}] {b['text'][:50]}...")

if __name__ == '__main__':
    unittest.main()

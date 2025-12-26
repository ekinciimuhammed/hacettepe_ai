import os
import unittest
from unittest.mock import patch, MagicMock
import pytesseract
from pipeline.pdf_loader import load_pdf

# Mock clean up of log file
LOG_FILE = "processing_errors.log"
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

class TestPDFLoaderErrorHandling(unittest.TestCase):
    
    @patch('pipeline.pdf_loader.fitz.open')
    def test_tesseract_not_found_error(self, mock_fitz_open):
        """Test that TesseractNotFoundError is caught and logged."""
        print("\n--- Testing TesseractNotFoundError ---")
        
        # Mock pdf document
        mock_doc = MagicMock()

        # Mock page to return sparse text to trigger OCR
        mock_page = MagicMock()
        mock_page.get_text.return_value = "   " 
        
        # Mock pixmap and bytes for Image.open
        mock_pix = MagicMock()
        mock_pix.tobytes.return_value = b'fake_image_data'
        mock_page.get_pixmap.return_value = mock_pix
        
        mock_doc.__len__.return_value = 1
        mock_doc.load_page.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        # Mock PIL.Image.open so we don't need real image bytes
        with patch('pipeline.pdf_loader.Image.open') as mock_img_open:
            mock_img_open.return_value = MagicMock()
            
            # Mock pytesseract to raise TesseractNotFoundError
            with patch('pipeline.pdf_loader.pytesseract.image_to_string') as mock_ocr:
                mock_ocr.side_effect = pytesseract.TesseractNotFoundError()
                
                # Call function
                result = load_pdf("dummy_scan.pdf")
                
                # Assertions
                self.assertIsNone(result, "Function should return None on Tesseract failure")
                self.assertTrue(os.path.exists(LOG_FILE), "Log file should be created")
                
                with open(LOG_FILE, 'r') as f:
                    content = f.read()
                    print(f"Log content: {content.strip()}")
                    self.assertIn("Tesseract OCR not found", content)
                    self.assertIn("dummy_scan.pdf", content)

    @patch('pipeline.pdf_loader.fitz.open')
    def test_generic_exception(self, mock_fitz_open):
        """Test that generic exceptions are caught and logged."""
        print("\n--- Testing Generic Exception ---")
        
        # Mock fitz.open to raise a generic exception
        mock_fitz_open.side_effect = Exception("Corrupted PDF file")
        
        # Call function
        result = load_pdf("corrupted.pdf")
        
        # Assertions
        self.assertIsNone(result, "Function should return None on generic failure")
        
        with open(LOG_FILE, 'r') as f:
            content = f.read()
            # Check latest entry
            print(f"Log content: {content.strip()}")
            self.assertIn("Corrupted PDF file", content)
            self.assertIn("corrupted.pdf", content)

if __name__ == '__main__':
    unittest.main()

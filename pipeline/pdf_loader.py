import fitz  # pymupdf
import pytesseract
from PIL import Image
import io

def load_pdf(file_path):
    """
    Reads a PDF file and extracts text.
    Uses PyMuPDF first. If text is sparse/empty, falls back to OCR via pytesseract.
    Returns: full text string.
    """
    text_content = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")

            # Check if page is mostly image/scanned by checking text length
            # Threshold is arbitrary, but < 50 chars usually implies scan or empty
            if len(text.strip()) < 50:
                # Fallback to OCR
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                # Tesseract OCR
                text = pytesseract.image_to_string(image, lang='tur+eng') # assumig turkish/english content
            
            text_content.append(text)
        
        return "\n".join(text_content)
    
    except pytesseract.TesseractNotFoundError:
        error_msg = "Tesseract OCR not found/installed"
        print(f"❌ {error_msg}")
        log_error(file_path, error_msg)
        return None
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error reading PDF {file_path}: {error_msg}")
        log_error(file_path, error_msg)
        return None

def log_error(file_path, error_message):
    """Logs errors to a file for later review."""
    import datetime
    import os
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "processing_errors.log"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] File: {os.path.basename(file_path)} | Error: {error_message}\n")
    except Exception as log_err:
        print(f"Failed to write to log file: {log_err}")

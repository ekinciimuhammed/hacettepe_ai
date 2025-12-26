import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.datamodel.document import TableItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoclingLoader:
    def __init__(self, use_ocr: bool = True):
        # Configure pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = use_ocr
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        
        # Initialize converter with options
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load a PDF and return structured blocks.
        
        Returns:
            List of dictionaries, each representing a block:
            {
                "text": str,
                "type": str (heading, paragraph, table, etc.),
                "page": int,
                "bbox": [x0, y0, x1, y1]
            }
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return []

        try:
            logger.info(f"Processing {file_path} with Docling...")
            result = self.converter.convert(path)
            doc = result.document
            
            blocks = []
            
            # Iterate through all items in the document structure
            for item, level in doc.iterate_items():
                
                # Basic block info
                block_data = {
                    "text": item.text,
                    "type": "unknown",
                    "page": -1,
                    "bbox": None
                }
                
                # Determine type
                if hasattr(item, "label"):
                     block_data["type"] = str(item.label).lower()
                
                # Get location info if available
                if hasattr(item, "prov") and item.prov:
                     # Using the first provenance item for page/bbox
                     prov = item.prov[0]
                     block_data["page"] = prov.page_no
                     if hasattr(prov, "bbox"):
                         block_data["bbox"] = [prov.bbox.l, prov.bbox.t, prov.bbox.r, prov.bbox.b]

                # Filter empty blocks
                if block_data["text"] and block_data["text"].strip():
                    blocks.append(block_data)
            
            logger.info(f"Extracted {len(blocks)} blocks from {file_path}")
            return blocks

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            return []

if __name__ == "__main__":
    # Simple test
    loader = DoclingLoader()
    # Replace with a real file for testing
    # res = loader.load("belgeler/test.pdf")
    # print(res[:5])
    pass

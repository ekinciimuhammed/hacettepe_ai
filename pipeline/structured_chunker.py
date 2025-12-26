import logging
import re
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StructuredChunker:
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group blocks by heading and split into chunks.
        
        Args:
            blocks: Output from DoclingLoader
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not blocks:
            return []
            
        chunks = []
        current_heading = "Giriş / Genel"
        current_text_buffer = []
        current_metadata = {
            "page_start": blocks[0].get("page", 1),
            "page_end": blocks[0].get("page", 1),
            "block_types": set(),
            "sources": set() # digital vs ocr (if we tracked it)
        }
        
        for block in blocks:
            text = block.get("text", "").strip()
            block_type = block.get("type", "paragraph")
            page = block.get("page", 1)
            
            if not text:
                continue

            # If it's a major heading, assume a new section starts
            if block_type in ["section_header", "title", "page_header"] or (block_type == "text" and self._is_likely_heading(text)):
                # Flush current buffer as a chunk if it has content
                if current_text_buffer:
                    self._flush_buffer(chunks, current_heading, current_text_buffer, current_metadata)
                    current_text_buffer = []
                    current_metadata = {
                         "page_start": page,
                         "page_end": page,
                         "block_types": set(),
                         "sources": set()
                    }
                
                # Update current heading
                current_heading = text
                current_metadata["block_types"].add("heading")
                
            else:
                # Add to buffer
                current_text_buffer.append(text)
                current_metadata["page_end"] = max(current_metadata["page_end"], page)
                current_metadata["block_types"].add(block_type)
        
        # Final flush
        if current_text_buffer:
             self._flush_buffer(chunks, current_heading, current_text_buffer, current_metadata)
             
        logger.info(f"Generated {len(chunks)} structured chunks.")
        return chunks

    def _flush_buffer(self, chunks: List, heading: str, buffer: List[str], metadata: Dict):
        """Helper to create chunks from the buffer, respecting size limits."""
        full_text = "\n\n".join(buffer)
        
        # If small enough, keep as one
        if len(full_text) <= self.max_chunk_size:
            chunks.append({
                "text": f"{heading}\n\n{full_text}",
                "metadata": {
                    "heading": heading,
                    "page_range": [metadata["page_start"], metadata["page_end"]],
                    "block_types": list(metadata["block_types"])
                }
            })
            return

        # If too large, split semantically (sentences)
        # Simple recursive splitter could be used here, but for now linear split
        words = full_text.split()
        current_chunk_words = []
        current_len = 0
        
        for word in words:
            if current_len + len(word) + 1 > self.max_chunk_size:
                # Save chunk
                chunk_text = " ".join(current_chunk_words)
                chunks.append({
                    "text": f"{heading}\n\n{chunk_text} ...",
                    "metadata": {
                        "heading": heading,
                        "page_range": [metadata["page_start"], metadata["page_end"]],
                        "block_types": list(metadata["block_types"]),
                        "partial": True
                    }
                })
                # Start new with overlap (simplified: just keep last N words? No, for strictness start fresh)
                # Proper sliding window is better but complex. 
                # Reset
                current_chunk_words = [word]
                current_len = len(word)
            else:
                current_chunk_words.append(word)
                current_len += len(word) + 1
        
        # Last part
        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            chunks.append({
                    "text": f"{heading}\n\n{chunk_text}",
                    "metadata": {
                        "heading": heading,
                        "page_range": [metadata["page_start"], metadata["page_end"]],
                        "block_types": list(metadata["block_types"])
                    }
            })

    def _is_likely_heading(self, text: str) -> bool:
        """Heuristic: Short text, all caps or starting with number."""
        if len(text) > 100: return False
        if re.match(r'^MADDE \d+', text, re.IGNORECASE): return True
        if re.match(r'^\d+\.', text): return True
        if text.isupper() and len(text) > 4: return True
        return False

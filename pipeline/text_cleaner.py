import re
import unicodedata

def clean_text(text):
    """
    Cleans raw text extracted from PDF.
    - Unicode normalization
    - Whitespace cleanup
    - Line joining (fixing broken lines)
    - Footer/Header removal (basic heuristics)
    """
    if not text:
        return ""

    # 1. Unicode Normalization
    text = unicodedata.normalize('NFKC', text)

    # 2. Split into lines for processing
    lines = text.split('\n')
    cleaned_lines = []
    
    # 3. Filter Step (Page numbers, headers)
    filtered_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip purely numeric lines (likely page numbers)
        if re.match(r'^\d+$', line):
            continue
        # Skip "Page X"
        if re.match(r'^Page \d+', line, re.IGNORECASE):
            continue
        filtered_lines.append(line)
        
    if not filtered_lines:
        return ""

    # 4. Smart Join
    # We want to merge lines that are wrapped, BUT start new lines for Sections/Items
    final_text = ""
    current_buffer = []

    # Patterns that should ALWAYS start a new line
    # Madde X, 1., a), A)
    # Note: \d+\. matches "1." but also "1994." (year?). Usually list items are small digits.
    # Let's be a bit specific: ^\d{1,2}\.
    start_pattern = re.compile(r'^(Madde \d+|[a-zA-Z]\)|\d{1,2}\.)', re.IGNORECASE)

    for line in filtered_lines:
        # Check if this line looks like a new item
        if start_pattern.match(line):
            # If we have a buffer, flush it as a paragraph
            if current_buffer:
                paragraph = " ".join(current_buffer)
                final_text += paragraph + "\n"
                current_buffer = []
            
            # Add this item-line directly/start new buffer
            # Usually items might also wrap, so we treat this as start of new buffer
            current_buffer.append(line)
            
            # Force a flush immediately? 
            # If "Madde 1" is just the title, next line is content.
            # Ideally "Madde 1" line + next line might be same paragraph? 
            # No, usually Title is separate.
            # Let's just append to buffer. Since we flushed BEFORE, this line starts a new block.
            # But wait, if next line is wrapped content of this item, it will append to buffer.
            # That is consistent.
            
        else:
            # It's a regular line.
            # Heuristic: If matches SENTENCE START (Uppercase) and previous buffer ended with punctuation?
            # Creating generally merged paragraphs is safer for RAG.
            current_buffer.append(line)
    
    # Flush remaining
    if current_buffer:
        final_text += " ".join(current_buffer)

    # 5. Fix hyphenation
    final_text = re.sub(r'(\w+)- (\w+)', r'\1\2', final_text)
    
    # 6. Final Cleanup
    final_text = re.sub(r'\s+', ' ', final_text).replace('\n ', '\n')
    
    # Re-inject newlines before "Madde" if they got lost or purely for safety
    # (The loop above keeps them if they appeared at start of line in PDF)
    
    # However, our regex in chunker expects NEWLINES.
    # The output of this function will be a single string.
    # If I just used `final_text += paragraph + "\n"`, then I have newlines!
    # But wait, step 6 `re.sub(r'\s+', ' ', final_text)` will Turn `\n` into ` `!!!
    # CRITICAL: `\s` matches `\n`.
    
    # Fix step 6 to not kill newlines
    # Use explicit space match `[ \t]+` or similar.
    final_text = re.sub(r'[ \t\r\f\v]+', ' ', final_text).strip()
    
    return final_text

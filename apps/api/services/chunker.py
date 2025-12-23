from typing import List

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks of `chunk_size` characters with `overlap`.
    Simple character-based splitting.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Stop if we reached the end
        if end >= text_len:
            break
            
        # Move start pointer by (chunk_size - overlap)
        start += (chunk_size - overlap)
        
    return chunks

import os
# We need a pdf library. PyPDF2 or pdfplumber.
# I'll check if I installed one. The user didn't specify, but pypdf is standard.
# I'll add pypdf to requirements first.

class PDFExtractor:
    def extract_text(self, file_path: str) -> str:
        try:
            # Lazy import to avoid crashes if dependnecy missing during dev
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            return "Error: pypdf not installed."
        except Exception as e:
            return f"Error extracting text: {str(e)}"

extractor = PDFExtractor()

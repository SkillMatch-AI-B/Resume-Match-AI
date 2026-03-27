import PyPDF2
import docx
import re

def clean_text(raw_text):
    """
    Strips out weird hidden characters, corrupted symbols, 
    and normalizes spacing so the AI can actually read it.
    """
    if not raw_text:
        return ""
    # Remove non-ASCII characters (often caused by bad fonts or icons)
    text = re.sub(r'[^\x00-\x7F]+', ' ', raw_text)
    # Replace multiple spaces, tabs, or newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_resume(file_obj):
    """
    Extracts text from PDF, DOCX, or TXT files.
    Includes heavy-duty error handling for corrupted files.
    """
    filename = file_obj.name.lower()
    extracted_text = ""

    try:
        if filename.endswith('.pdf'):
            # Read PDF
            pdf_reader = PyPDF2.PdfReader(file_obj)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + " "
                    
        elif filename.endswith('.docx'):
            # Read DOCX
            try:
                doc = docx.Document(file_obj)
                for para in doc.paragraphs:
                    extracted_text += para.text + " "
            except Exception as docx_error:
                return f"Error: DOCX file formatting is corrupted or unreadable. ({str(docx_error)})"
                
        elif filename.endswith('.txt'):
            # Read TXT (try standard UTF-8, fallback to Latin-1 if it has weird characters)
            try:
                extracted_text = file_obj.read().decode('utf-8')
            except UnicodeDecodeError:
                file_obj.seek(0)
                extracted_text = file_obj.read().decode('latin-1')
        else:
            return "Error: Unsupported file format. Please upload a PDF, DOCX, or TXT file."

        # Pass it through our scrubber
        final_text = clean_text(extracted_text)
        
        # Check if the file was just a scanned image with no highlightable text
        if not final_text or len(final_text) < 10:
            return "Error: Document appears to be empty or an unreadable scanned image."
            
        return final_text

    except Exception as e:
        # Catch-all for password-protected or totally broken files
        return f"Error: Could not safely read the file. ({str(e)})"
from PyPDF2 import PdfReader
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

def extract_text_pdf(file_bytes: bytes) -> str:
    logger.info("Starting PDF text Extraction")

    try:
        # Create a file-like object from bytes
        pdf_file = BytesIO(file_bytes)

        # Create PDF reader
        pdf_reader = PdfReader(pdf_file)

        num_pages = len(pdf_reader.pages)
        logger.debug(f"PDF has {num_pages} pages")

        # Extract text
        text = ""
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            page_text =page.extract_text()
            text += page_text + "\n"
            logger.debug(f"Extracted text from page {num_pages}: {len(page_text)} chars")

        total_chars = len(text.strip())
        logger.info(f"PDF extraction complete: {total_chars} chars from {num_pages} pages")

        if total_chars < 50:
            logger.warning("Extracted text is very short, PDF might be image-based or encrypted")
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to read PDF: {str(e)}")       

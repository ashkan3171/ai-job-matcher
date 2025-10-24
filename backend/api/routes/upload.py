from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.schemas import PDFUploadResponse
from backend.services.pdf_service import extract_text_pdf
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile =  File(...)):
    """
    Upload a PDF file and extract its text content.
    
    - **file**: PDF file to upload
    
    Returns the extracted text.
    """
    logger.info(f"PDF upload request - Filename: {file.filename}, Content-Type: {file.content_type}")

    # Validate file type
    if file.content_type != "application/pdf":
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File must be a PDF")  
    
    # Validate file size (max 10MB)
    file_bytes = await file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)
    
    if file_size_mb > 10:
        logger.warning(f"File too large: {file_size_mb:.2f}MB")
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")

    logger.debug(f"File size: {file_size_mb:.2f}MB")

    try:
        # Extract text
        text = extract_text_pdf(file_bytes)
        
        # Count pages (rough estimate)
        page_count = text.count('\f') + 1 if '\f' in text else len(text) // 2000
        char_count = len(text)
        
        logger.info(f"PDF processed successfully - {page_count} pages, {char_count} chars")
        
        return PDFUploadResponse(
            text=text,
            page_count=page_count,
            char_count=char_count,
            status="success"
        )
        
    except ValueError as e:
        logger.error(f"PDF extraction failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process PDF")
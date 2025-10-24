from fastapi import APIRouter, Request
from backend.models.schemas import JobMatchRequest, JobMatchResponse
from backend.services.matcher_service import calculate_job_match
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["matcher"])

@router.post("/match", response_model=JobMatchResponse)
def match_job_resume(data: JobMatchRequest, request: Request):
    """
    Calculate how well a resume matches a job description.
    """
    client_ip: Optional[str] = request.client.host if request.client else "unknown"
    logger.info(f"New match request from {client_ip}")
    logger.debug(f"Request data - Job: {len(data.job_text)} chars, Resume: {len(data.resume_text)} chars")

    start_time = time.time()

    try:
        result = calculate_job_match(data.job_text, data.resume_text)
        
        elapsed_time = time.time() - start_time
        logger.info(
            f"Match request completed in {elapsed_time:.2f}s - "
            f"Semantic: {result['similarity_score']}%, "
            f"Skills: {result['matched_skill_percentage']}%"
        )
        
        response = JobMatchResponse(
            similarity_score=result["similarity_score"],
            matched_skill_percentage=result["matched_skill_percentage"],
            matched_skills=result["matched_skills"],
            missing_skills=result["missing_skills"],
            extra_skills=result["extra_skills"],
            status="success"
        )
        
        logger.debug(f"Returning response with {len(response.matched_skills)} matched skills")
        return response
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(
            f"Match request failed after {elapsed_time:.2f}s from {client_ip}: {str(e)}",
            exc_info=True
        )
        raise
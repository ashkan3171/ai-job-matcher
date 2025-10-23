from fastapi import APIRouter
from backend.models.schemas import JobMatchRequest, JobMatchResponse
from backend.services.matcher_service import calculate_job_match

router = APIRouter(prefix="/api", tags=["matcher"])

@router.post("/match", response_model=JobMatchResponse)
def match_job_resume(request: JobMatchRequest):
    """
    Calculate how well a resume matches a job description.
    
    - **job_text**: The job description text
    - **resume_text**: The resume text
    
    Returns match scores and skill analysis.
    """
    result = calculate_job_match(request.job_text, request.resume_text)
    
    return JobMatchResponse(
        similarity_score=result["similarity_score"],
        matched_skill_percentage=result["matched_skill_percentage"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        extra_skills=result["extra_skills"],
        status="success"
    )
from pydantic import BaseModel

class JobMatchRequest(BaseModel):
    """Request model for job matching"""
    job_text: str
    resume_text: str

class JobMatchResponse(BaseModel):
    """Response model for job matching"""
    similarity_score: float
    matched_skill_percentage: float
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]
    status: str
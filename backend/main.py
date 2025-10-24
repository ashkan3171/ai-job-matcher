from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.logging_config import setup_logging
from backend.core.config import settings
from backend.api.routes import matcher
from backend.api.routes import upload
from backend.models.schemas import JobMatchRequest
from backend.services.matcher_service import calculate_job_match
import logging

setup_logging()
logger = logging.getLogger(__name__)

logger.info("="*50)
logger.info(f"Starting {settings.app_name} v{settings.app_version}")
logger.info("="*50)

# Create app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS configured for: {settings.frontend_url}")

# Include routers
app.include_router(matcher.router)
app.include_router(upload.router)
logger.info("API routes loaded")

# Health check
@app.get("/health")
def read_health():
    logger.debug("Health check endpoint called")
    return {"message": f"{settings.app_name} is running"}

# Legacy endpoint (for backwards compatibility with existing frontend)
@app.post("/cvjob-compare")
def legacy_endpoint(data: JobMatchRequest):
    """
    Legacy endpoint - kept for backwards compatibility.
    New clients should use /api/match instead.
    """
    logger.info("Legacy /cvjob-compare endpoint called")
    logger.debug(f"Request - Job text: {len(data.job_text)} chars, Resume: {len(data.resume_text)} chars")

    try:
        result = calculate_job_match(data.job_text, data.resume_text)
        logger.info(f"Match calculated - Semantic: {result['similarity_score']}%, Skills: {result['matched_skill_percentage']}%")
        logger.debug(f"Matched skills: {len(result['matched_skills'])}, Missing: {len(result['missing_skills'])}")
        return {**result, "Status": "Success"}
    except Exception as e:
        logger.error(f"Error in match calculation: {str(e)}", exc_info=True)
        raise
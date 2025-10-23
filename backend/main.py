from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api.routes import matcher
from backend.models.schemas import JobMatchRequest
from backend.services.matcher_service import calculate_job_match

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

# Include routers
app.include_router(matcher.router)

# Health check
@app.get("/")
def read_root():
    return {"message": f"{settings.app_name} is running"}

# Legacy endpoint (for backwards compatibility with existing frontend)
@app.post("/cvjob-compare")
def legacy_endpoint(data: JobMatchRequest):
    """
    Legacy endpoint - kept for backwards compatibility.
    New clients should use /api/match instead.
    """
    result = calculate_job_match(data.job_text, data.resume_text)
    return {**result, "Status": "Success"}
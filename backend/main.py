from fastapi import FastAPI
from pydantic import BaseModel
from backend.matcher import compute_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Job Tracking Application", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"message": "Job Tracking API is running."}

class CVJobCompare(BaseModel):
    job_text: str
    resume_text: str

@app.post("/cvjob-compare")
def endpint_process(data: CVJobCompare):
    result = compute_similarity(data.job_text, data.resume_text)
    return {
        **result,
        "Status": "Success"
    }


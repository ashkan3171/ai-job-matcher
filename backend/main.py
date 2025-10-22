from fastapi import FastAPI
from pydantic import BaseModel
from backend.matcher import compute_similarity

app = FastAPI(title="Job Tracking API", version="1.0.0")

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


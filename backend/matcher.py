from sentence_transformers import SentenceTransformer, util
from backend.skill_extractor import extract_skills

model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_similarity(job_text: str, resume_text: str) -> dict:
    """
    Compute semantic similarity between job description and resume.
    """
    # Similarity 
    job_embedding = model.encode(job_text, convert_to_tensor=True)
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    similarity = util.cos_sim(job_embedding, resume_embedding)
    similarity_score = similarity.item() * 100

    # Extract skills
    job_skills = set(extract_skills(job_text, context="job"))
    resume_skills = set(extract_skills(resume_text, context="resume"))

    # Compare skills
    matched_skills = resume_skills.intersection(job_skills)
    missing_skills = job_skills - resume_skills
    extra_skills = resume_skills - job_skills

    return {
        "similarity_score": round(similarity_score, 2),
        "matched_skill_percentage": round(len(matched_skills)/len(job_skills) * 100, 2) if job_skills else 0,
        "matched_skills": list(matched_skills),
        "missing_skills": list(missing_skills),
        "extra_skills": list(extra_skills)
    }
        
from sentence_transformers import SentenceTransformer, util
from backend.services.ai_service import compare_skills

# Load model once (expensive operation)
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_job_match(job_text: str, resume_text: str) -> dict:
    """
    Calculate semantic similarity and skills match between job and resume.
    
    Args:
        job_text: Job description text
        resume_text: Resume text
        
    Returns:
        Dictionary with all match metrics
    """
    # Calculate semantic similarity
    job_embedding = model.encode(job_text, convert_to_tensor=True)
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    similarity = util.cos_sim(job_embedding, resume_embedding)
    similarity_score = similarity.item() * 100
    
    # Get skills comparison from AI service
    skills_analysis = compare_skills(job_text, resume_text)
    
    return {
        "similarity_score": round(similarity_score, 2),
        "matched_skill_percentage": skills_analysis["matched_skill_percentage"],
        "matched_skills": skills_analysis["matched_skills"],
        "missing_skills": skills_analysis["missing_skills"],
        "extra_skills": skills_analysis["extra_skills"]
    }
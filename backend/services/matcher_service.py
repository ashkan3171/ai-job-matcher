from sentence_transformers import SentenceTransformer, util
from backend.services.ai_service import compare_skills
import logging

logger = logging.getLogger(__name__)

logger.info("Laoding sentence-transformer model: all-MinLim-L6-V2")
model = SentenceTransformer('all-MiniLM-L6-v2')
logger.info("Sentence-transformer model loaded successfully")

def calculate_job_match(job_text: str, resume_text: str) -> dict:
    """
    Calculate semantic similarity and skills match between job and resume.
    """
    logger.info("Starting job match calculation")
    logger.debug(f"Input lengths - Job: {len(job_text)} chars, Resume: {len(resume_text)} chars")

    try:
        # Calculate semantic similarity
        logger.debug("Encoding job description to embedding")
        job_embedding = model.encode(job_text, convert_to_tensor=True)
        
        logger.debug("Encoding resume to embedding")
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        
        logger.debug("Calculating cosine similarity")
        similarity = util.cos_sim(job_embedding, resume_embedding)
        similarity_score = similarity.item() * 100
        
        logger.info(f"Semantic similarity calculated: {round(similarity_score, 2)}%")
        
        # Get skills comparison from AI service
        logger.debug("Starting skills comparison")
        skills_analysis = compare_skills(job_text, resume_text)
        
        result = {
            "similarity_score": round(similarity_score, 2),
            "matched_skill_percentage": skills_analysis["matched_skill_percentage"],
            "matched_skills": skills_analysis["matched_skills"],
            "missing_skills": skills_analysis["missing_skills"],
            "extra_skills": skills_analysis["extra_skills"]
        }
        
        logger.info(
            f"Match calculation complete - "
            f"Semantic: {result['similarity_score']}%, "
            f"Skills: {result['matched_skill_percentage']}%"
        )
        logger.debug(
            f"Skills breakdown - "
            f"Matched: {len(result['matched_skills'])}, "
            f"Missing: {len(result['missing_skills'])}, "
            f"Extra: {len(result['extra_skills'])}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error during match calculation: {str(e)}", exc_info=True)
        raise
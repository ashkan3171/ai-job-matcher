from openai import OpenAI
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)
logger.info("OpenAI client initialized")

def extract_skills(text: str, context: str = "job") -> list[str]:
    """
    Extract technical skills from text using GPT.
    
    Args:
        text: The text to analyze
        context: Either "job" or "resume"
        
    Returns:
        List of extracted skills
    """
    logger.info(f"Extracting {context} skills from text ({len(text)} chars)")

    prompt = f"""Extract all technical skills, tools, frameworks, and technologies from the following {context}.
Return ONLY a comma-separated list of skills. Be comprehensive but accurate.
Include: programming languages, frameworks, libraries, tools, platforms, methodologies, databases and cloud platforms.
Example output: Python, React, AWS, Docker, PostgreSQL, Machine Learning, Git, Agile, REST APIs

{context.capitalize()}:
{text}

Skills (comma-separated):"""
    
    try:
        logger.debug(f"Calling OpenAI API (model: gpt-4o-mini, temp: 0.3)")
        
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="You are a technical recruiter expert at identifying skills from job descriptions and resumes.",
            input=prompt,
            max_output_tokens=300,
            temperature=0.3,
        )
        
        skills_text = response.output_text.strip()
        skills = [skill.strip().lower() for skill in skills_text.split(",") if skill.strip()]
        skills = list(set(skills))
        
        logger.info(f"Successfully extracted {len(skills)} skills from {context}")
        logger.debug(f"Skills: {skills[:5]}..." if len(skills) > 5 else f"Skills: {skills}")
        
        return skills
    
    except Exception as e:
        logger.error(f"OpenAI API error while extracting {context} skills: {str(e)}", exc_info=True)
        logger.warning("Returning empty skills list as fallback")
        return []

def compare_skills(job_text: str, resume_text: str) -> dict:
    """
    Compare skills between job and resume.
    """
    logger.info("Starting skills comparison")
    
    job_skills = set(extract_skills(job_text, context="job"))
    resume_skills = set(extract_skills(resume_text, context="resume"))
    
    matched_skills = resume_skills.intersection(job_skills)
    missing_skills = job_skills - resume_skills
    extra_skills = resume_skills - job_skills
    
    logger.info(f"Comparison complete - Matched: {len(matched_skills)}, Missing: {len(missing_skills)}, Extra: {len(extra_skills)}")
    
    percentage = round(len(matched_skills) / len(job_skills) * 100, 2) if job_skills else 0
    
    return {
        "matched_skills": sorted(list(matched_skills)),
        "missing_skills": sorted(list(missing_skills)),
        "extra_skills": sorted(list(extra_skills)),
        "matched_skill_percentage": percentage
    }
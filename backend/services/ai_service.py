from openai import OpenAI
from backend.core.config import settings
import logging
from rapidfuzz import fuzz

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

    prompt = f"""You are an expert technical recruiter analyzing a {context}. Extract ALL technical skills, tools, frameworks, technologies, methodologies, and competencies.

EXTRACTION RULES:
1. Extract BOTH the full term AND individual components
   Example: "GitLab CI/CD" → extract: "GitLab", "CI/CD", "GitLab CI/CD"
   Example: "AWS Lambda" → extract: "AWS", "Lambda", "AWS Lambda", "cloud"

2. Include common abbreviations AND full names
   Example: "Kubernetes" → extract: "Kubernetes", "K8s", "container orchestration"
   Example: "PostgreSQL" → extract: "PostgreSQL", "Postgres", "SQL"

3. Extract implied skills from descriptions
   Example: "built microservices" → extract: "microservices", "microservices architecture"
   Example: "deployed to production" → extract: "deployment", "production systems"

4. Recognize methodology and practice keywords
   Example: "Agile/Scrum" → extract: "Agile", "Scrum", "Agile methodologies"
   Example: "code reviews" → extract: "code reviews", "code quality"

5. Extract specific versions and variants
   Example: "Python 3.x" → extract: "Python", "Python 3"
   Example: "FastAPI microservices" → extract: "FastAPI", "microservices", "REST APIs"

6. Include domain expertise
   Example: "fraud detection system" → extract: "fraud detection", "security"
   Example: "MLOps pipeline" → extract: "MLOps", "ML", "DevOps", "pipelines"

7. Normalize similar terms to standard names
   Example: "k8s" → "Kubernetes"
   Example: "React.js" → "React"
   Example: "Postgres" → "PostgreSQL"

CATEGORIES TO EXTRACT:
- Programming languages (Python, JavaScript, SQL, etc.)
- Frameworks & libraries (FastAPI, Django, React, Flask, etc.)
- Databases (PostgreSQL, Redis, MongoDB, Oracle, etc.)
- Cloud platforms (AWS, GCP, Azure) and their services (EC2, Lambda, S3, etc.)
- DevOps tools (Docker, Kubernetes, Jenkins, GitLab, CI/CD, etc.)
- Monitoring & logging (Prometheus, Grafana, Elasticsearch, etc.)
- Message queues (RabbitMQ, Celery, Kafka, etc.)
- ML/AI tools (scikit-learn, TensorFlow, MLflow, XGBoost, etc.)
- Development practices (Agile, Scrum, TDD, code reviews, pair programming, etc.)
- Web technologies (REST APIs, GraphQL, WebSockets, microservices, etc.)
- Testing tools (pytest, unittest, integration testing, etc.)
- Version control (Git, GitHub, GitLab, etc.)
- Security (OAuth, JWT, RBAC, authentication, etc.)

{context.upper()} TEXT:
{text}

OUTPUT FORMAT:
Return a comprehensive comma-separated list of ALL extracted skills. Be thorough but avoid duplicates. Use lowercase for consistency.

SKILLS:"""
    
    try:
        logger.debug(f"Calling OpenAI API (model: gpt-4o-mini, temp: 0.3)")
        
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="You are a technical recruiter expert at identifying skills from job descriptions and resumes.",
            input=prompt,
            max_output_tokens=500,
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

    # Fuzzy matches
    fuzzy_matched_resume = set()
    fuzzy_matched_job = set()
    
    # For each job skill, find best match in resume skills
    for job_skill in job_skills:
        if job_skill in matched_skills:
            continue  # Already matched exactly
        
        best_match = None
        best_score = 0
        
        for resume_skill in matched_skills:
            if resume_skill in matched_skills or resume_skill in fuzzy_matched_resume:
                continue  # Already matched
            
            # Calculate similarity
            score = fuzz.ratio(job_skill, resume_skill)
            
            # Also check if one contains the other (substring match)
            if job_skill in resume_skill or resume_skill in job_skill:
                score = max(score, 85)  # Boost score for substring matches
            
            if score > best_score:
                best_score = score
                best_match = resume_skill
        
        # Accept matches above 80% similarity
        if best_score >= 80:
            fuzzy_matched_resume.add(best_match)
            fuzzy_matched_job.add(job_skill)
            logger.debug(f"Fuzzy match: '{job_skill}' ≈ '{best_match}' (score: {best_score})")
    
    # Combine exact and fuzzy matches
    all_matched = matched_skills.union(fuzzy_matched_job)
    matched_job_count = len(all_matched)

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
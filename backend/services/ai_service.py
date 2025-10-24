import logging
from rapidfuzz import fuzz
from openai import OpenAI
from backend.core.config import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.openai_api_key)

# Skill synonyms and related terms
SKILL_SYNONYMS = {
    # Programming languages
    "python": ["python 3", "python3", "py"],
    "javascript": ["js", "ecmascript"],
    "typescript": ["ts"],
    
    # Cloud platforms
    "aws": ["amazon web services", "cloud", "cloud infrastructure"],
    "gcp": ["google cloud", "google cloud platform", "cloud infrastructure"],
    "azure": ["microsoft azure", "cloud infrastructure"],
    
    # Cloud services
    "ec2": ["aws ec2", "elastic compute"],
    "lambda": ["aws lambda", "serverless"],
    "s3": ["aws s3", "object storage"],
    
    # Containers & Orchestration
    "docker": ["containerization", "containers"],
    "kubernetes": ["k8s", "container orchestration", "cluster management"],
    "container orchestration": ["kubernetes", "k8s", "docker swarm"],
    
    # Databases
    "postgresql": ["postgres", "psql", "sql"],
    "redis": ["caching", "in-memory database"],
    
    # DevOps & CI/CD
    "ci/cd": ["continuous integration", "continuous deployment", "cicd", "deployment processes", "gitlab ci/cd", "github actions"],
    "gitlab": ["gitlab ci/cd", "ci/cd"],
    "github": ["github actions", "ci/cd"],
    
    # APIs & Architecture
    "rest apis": ["restful apis", "rest", "api development", "apis"],
    "restful apis": ["rest apis", "rest", "api development"],
    "microservices": ["microservices architecture", "service-oriented architecture"],
    "microservices architecture": ["microservices"],
    
    # Web Frameworks
    "fastapi": ["fast api", "api framework"],
    "django": ["django framework"],
    "flask": ["flask framework"],
    
    # Testing
    "pytest": ["unit testing", "automated testing", "testing"],
    "automated testing": ["pytest", "unit testing", "integration testing", "testing"],
    "tdd": ["test-driven development", "testing"],
    
    # Monitoring & Observability
    "prometheus": ["monitoring", "metrics"],
    "grafana": ["monitoring", "dashboards", "visualization"],
    "elasticsearch": ["elk", "logging", "search"],
    
    # Message Queues
    "rabbitmq": ["message queues", "message broker", "amqp"],
    "celery": ["task queue", "background jobs", "async tasks"],
    "message queues": ["rabbitmq", "celery", "kafka", "sqs"],
    
    # Methodologies
    "agile": ["agile methodologies", "scrum", "agile/scrum"],
    "scrum": ["agile", "agile methodologies"],
    
    # Performance
    "performance optimization": ["optimization", "query optimization", "profiling"],
    "query optimization": ["database optimization", "performance optimization"],
    "high-performance apis": ["performance optimization", "low latency", "fast apis"],
    
    # Domains
    "fintech": ["financial technology", "payments", "banking"],
    "payments": ["fintech", "payments industry"],
    
    # General
    "cloud infrastructure": ["aws", "gcp", "azure", "cloud"],
    "production systems": ["deployment", "production deployment"],
    "comprehensive tests": ["automated testing", "testing", "pytest"],
}

def expand_skills_with_synonyms(skills: list[str]) -> set[str]:
    """
    Expand a list of skills to include synonyms and related terms.
    """
    expanded = set(skills)
    
    for skill in skills:
        skill_lower = skill.lower().strip()
        if skill_lower in SKILL_SYNONYMS:
            expanded.update(SKILL_SYNONYMS[skill_lower])
    
    return expanded

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
    Compare skills between job and resume using fuzzy matching and synonyms.
    """
    logger.info("Starting skills comparison with fuzzy matching and synonyms")
    
    job_skills_raw = extract_skills(job_text, context="job")
    resume_skills_raw = extract_skills(resume_text, context="resume")
    
    logger.debug(f"Job skills extracted: {len(job_skills_raw)}")
    logger.debug(f"Resume skills extracted: {len(resume_skills_raw)}")
    
    # Expand with synonyms
    job_skills = expand_skills_with_synonyms(job_skills_raw)
    resume_skills = expand_skills_with_synonyms(resume_skills_raw)
    
    logger.debug(f"After synonym expansion - Job: {len(job_skills)}, Resume: {len(resume_skills)}")
    
    # Exact matches
    exact_matches = resume_skills.intersection(job_skills)
    
    # Fuzzy matches
    fuzzy_matched_resume = set()
    fuzzy_matched_job = set()
    
    # For each job skill, find best match in resume skills
    for job_skill in job_skills:
        if job_skill in exact_matches:
            continue
        
        best_match = None
        best_score = 0
        
        for resume_skill in resume_skills:
            if resume_skill in exact_matches or resume_skill in fuzzy_matched_resume:
                continue
            
            # Calculate similarity
            score = fuzz.ratio(job_skill, resume_skill)
            
            # Substring boost
            if job_skill in resume_skill or resume_skill in job_skill:
                score = max(score, 85)
            
            if score > best_score:
                best_score = score
                best_match = resume_skill
        
        # Accept matches above 80% similarity
        if best_score >= 80:
            fuzzy_matched_resume.add(best_match)
            fuzzy_matched_job.add(job_skill)
            logger.debug(f"Fuzzy match: '{job_skill}' ≈ '{best_match}' (score: {best_score})")
    
    # Combine exact and fuzzy matches (use original skill names from job)
    all_matched_job_skills = set()
    for skill in job_skills_raw:
        skill_lower = skill.lower().strip()
        # Check if this original skill or its synonyms matched
        if skill_lower in exact_matches or skill_lower in fuzzy_matched_job:
            all_matched_job_skills.add(skill_lower)
        else:
            # Check synonyms
            if skill_lower in SKILL_SYNONYMS:
                for synonym in SKILL_SYNONYMS[skill_lower]:
                    if synonym in exact_matches or synonym in fuzzy_matched_job:
                        all_matched_job_skills.add(skill_lower)
                        logger.debug(f"Synonym match: '{skill_lower}' matched via '{synonym}'")
                        break
    
    matched_job_count = len(all_matched_job_skills)
    
    # Missing skills
    missing_skills = set(s.lower().strip() for s in job_skills_raw) - all_matched_job_skills
    
    # Extra skills
    extra_skills = set(s.lower().strip() for s in resume_skills_raw)
    
    match_percentage = round(matched_job_count / len(job_skills_raw) * 100, 2) if job_skills_raw else 0
    
    logger.info(f"Skills comparison complete - Matched: {matched_job_count}/{len(job_skills_raw)} ({match_percentage}%)")
    logger.debug(f"Exact: {len(exact_matches)}, Fuzzy: {len(fuzzy_matched_job)}, Missing: {len(missing_skills)}")
    
    return {
        "matched_skills": sorted(list(all_matched_job_skills)),
        "missing_skills": sorted(list(missing_skills)),
        "extra_skills": sorted(list(extra_skills)),
        "matched_skill_percentage": match_percentage
    }
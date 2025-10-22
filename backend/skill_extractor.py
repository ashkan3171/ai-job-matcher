from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_skills(text: str, context: str = "job") -> list[str]:
    """
    Use GPT to extract technical skills from text.
    
    Args:
        text: The text to analyze (job description or resume)
        context: Either "job" or "resume"
    
    Returns:
        List of extracted skills
    """
    prompt = f"""Extract all technical skills, tools, frameworks, and technologies from the following {context}
        Return ONLY a comma-seperated list of skills. Be comprehensive but accurate.
        Include: programming languages, frameworks, libraries, tools, platforms, methodologies, databases and cloud platforms.
        Example output: Python, React, AWS, Docker, PostgreSQL, Machine Learning, Git, Agile, REST APIs
        
        {context.capitalize()}:
        {text}

        Skills (comma-seperated):"""
    
    response = client.responses.create(
        model = "gpt-4o-mini",
        instructions="You are a techncal recuiter expert at identifying skills from job descriptions and resumes.",
        input=prompt,
        max_output_tokens=300,
        temperature=0.3,
    )

    skills_text = response.output_text.strip()
    skills = [skill.strip().lower() for skill in skills_text.split(",") if skill.strip()]
    skills = list(set(skills))
    return skills
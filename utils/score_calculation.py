def preprocess_keywords(keywords):
    """Convert keywords to lowercase and strip any whitespace."""
    return {keyword.lower().strip() for keyword in keywords}

def check_keywords_exist(job_keywords, resume_content):
    return [keyword for keyword in job_keywords if keyword not in resume_content.lower().strip()]

def calculate_match_score(job_keywords, resume_keywords, resume_content):
    # Preprocess and extract hard and soft skills from the dictionaries
    job_hard_skills = set(preprocess_keywords(job_keywords.get("hard skills", [])))
    job_soft_skills = set(preprocess_keywords(job_keywords.get("soft skills", [])))
    resume_hard_skills = set(preprocess_keywords(resume_keywords.get("hard skills", [])))
    resume_soft_skills = set(preprocess_keywords(resume_keywords.get("soft skills", [])))

    # Update the original dictionaries with preprocessed keywords
    job_keywords["hard skills"] = list(job_hard_skills)
    job_keywords["soft skills"] = list(job_soft_skills)
    resume_keywords["hard skills"] = list(resume_hard_skills)
    resume_keywords["soft skills"] = list(resume_soft_skills)

    # Combine hard and soft skills into a single set for each
    job_keywords_set = job_hard_skills.union(job_soft_skills)

    # Find missing keywords
    missing_keywords = check_keywords_exist(job_keywords_set, resume_content)

    # Find common keywords
    common_keywords = list(job_keywords_set - set(missing_keywords))

    # Calculate match score as a percentage
    match_score = len(common_keywords) / len(job_keywords_set) * 100 if job_keywords_set else 0

    # Calculate missing hard skills and soft skills
    missing_hard_skills = [skill for skill in missing_keywords if skill in job_hard_skills]
    missing_soft_skills = [skill for skill in missing_keywords if skill in job_soft_skills]

    return match_score, common_keywords, missing_keywords, job_hard_skills, job_soft_skills, missing_hard_skills, missing_soft_skills
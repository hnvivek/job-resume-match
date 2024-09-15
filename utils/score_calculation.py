def preprocess_keywords(keywords):
    """Convert keywords to lowercase and strip any whitespace."""
    return {keyword.lower().strip() for keyword in keywords}

def calculate_match_score(job_keywords, resume_keywords):
    # Preprocess and extract hard and soft skills from the dictionaries
    job_hard_skills = preprocess_keywords(job_keywords.get("hard skills", []))
    job_soft_skills = preprocess_keywords(job_keywords.get("soft skills", []))
    resume_hard_skills = preprocess_keywords(resume_keywords.get("hard skills", []))
    resume_soft_skills = preprocess_keywords(resume_keywords.get("soft skills", []))

    # Update the original dictionaries with preprocessed keywords
    job_keywords["hard skills"] = list(job_hard_skills)
    job_keywords["soft skills"] = list(job_soft_skills)
    resume_keywords["hard skills"] = list(resume_hard_skills)
    resume_keywords["soft skills"] = list(resume_soft_skills)

    # Combine hard and soft skills into a single set for each
    job_keywords_set = job_hard_skills.union(job_soft_skills)
    resume_keywords_set = resume_hard_skills.union(resume_soft_skills)

    # Find common keywords
    common_keywords = job_keywords_set.intersection(resume_keywords_set)

    # Find missing keywords
    missing_keywords = job_keywords_set - resume_keywords_set

    # Calculate match score as a percentage
    match_score = len(common_keywords) / len(job_keywords_set) * 100 if job_keywords_set else 0  # handle division by zero

    return match_score, common_keywords, missing_keywords

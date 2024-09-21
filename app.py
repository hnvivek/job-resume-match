import os
import hashlib
from flask import Flask, request, render_template
from llm.generate_cover_letter import generate_cover
from llm.resume_enhancement_generator import generate_resume_enhancements
from utils.prompt_loader import \
    load_prompts_from_directory  # Adjust the import as necessary
from loaders.document_loaders import extract_text_from_file  # Import your document loader
from llm.keyword_extraction import extract_keywords  # Import your LLM extractor
from utils.score_calculation import calculate_match_score  # Import your scoring function
from utils.scraper import fetch_text_from_url
from werkzeug.utils import secure_filename
from utils.text_processing import process_text_for_model, truncate_text
from dotenv import load_dotenv

app = Flask(__name__)

# Global variables for prompts, model, etc.
prompts = None
groq_api_key = None
model = None
max_tokens = None


def initial_loaders():
    """Initializes environment variables, prompts, and other settings."""
    global prompts, groq_api_key, model, max_tokens

    # Load environment variables from .env
    load_dotenv()

    # Load environment variables
    groq_api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("MODEL")
    max_tokens = int(os.getenv("MAX_TOKENS"))

    # Load prompts from the directory
    prompts = load_prompts_from_directory("./prompts")

    # Load and validate environment variables
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key is None:
        raise ValueError("GROQ_API_KEY is not set in the environment.")

    model = os.getenv("MODEL")
    if model is None:
        raise ValueError("MODEL is not set in the environment.")

    max_tokens = os.getenv("MAX_TOKENS")
    if max_tokens is None:
        raise ValueError("MAX_TOKENS is not set in the environment.")
    else:
        max_tokens = int(max_tokens)

    print("Initial setup completed. Environment variables and prompts loaded.")


# Call the initial_loaders function immediately when the script is loaded
initial_loaders()

# Cache to store LLM results
cache = {
    'job_description': {},
    'resume_content': {}
}


def hash_content(content):
    """Hashes the content to create a unique key for caching."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def cache_keywords(cache_key, content, keywords):
    """
    Pushes generated keywords to the cache.
    """
    hashed_content = hash_content(content)
    cache[cache_key][hashed_content] = keywords


def get_cached_keywords(cache_key, content):
    """
    Checks if keywords for the given content are in the cache. If found, return them.
    Otherwise, return None.
    """
    hashed_content = hash_content(content)
    return cache[cache_key].get(hashed_content, None)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        # Get job details from either URL or pasted job description
        job_method = request.form.get('jobMethod')  # "url" or "paste"
        job_url = request.form.get('jobUrl') if job_method == 'url' else None
        job_description = request.form.get(
            'jobDescription') if job_method == 'paste' else None

        # Get resume details from either file upload or pasted resume content
        resume_method = request.form.get('resumeMethod')  # "upload" or "paste"
        resume_file = request.files.get('file') if resume_method == 'upload' else None
        resume_content = request.form.get(
            'resumeContent') if resume_method == 'paste' else None

        if action == 'analyze':
            return handle_keywords_analyzer(job_url, job_description, resume_file,
                                            resume_content)
        elif action == 'generate_cover_letter':
            return handle_cover_letter_generation(job_url, job_description, resume_file,
                                                  resume_content)
        elif action == 'optimize_resume':
            return handle_resume_enhancement_generation(job_url, job_description,
                                                        resume_file,
                                                        resume_content)

    return render_template('index.html', job_keywords=[], resume_keywords=[],
                           common_keywords=[], missing_keywords=[])


def load_data(job_url, job_description, resume_file, resume_content):
    global cache

    # Handle job description
    if job_url:
        read_description = fetch_text_from_url(job_url)
        job_description = truncate_text(text=read_description,
                                        max_tokens=max_tokens)

    # Extract job keywords and check cache
    job_keywords = get_cached_keywords('job_description', job_description)
    if not job_keywords and job_description:
        # If not cached, process and cache it
        job_keywords = extract_keywords(model,
                                        process_text_for_model(text=job_description,
                                                               max_tokens=max_tokens),
                                        prompts["extract_keywords"])
        cache_keywords('job_description', job_description, job_keywords)

    # Handle resume
    if resume_file:
        file_path = save_file(resume_file)
        read_resume = extract_text_from_file(file_path)
        resume_content = truncate_text(text=read_resume, max_tokens=max_tokens)

    # Extract resume keywords and check cache
    resume_keywords = get_cached_keywords('resume_content', resume_content)
    if not resume_keywords and resume_content:
        # If not cached, process and cache it
        resume_keywords = extract_keywords(model,
                                           process_text_for_model(text=resume_content,
                                                                  max_tokens=max_tokens),
                                           prompts["extract_keywords"])
        cache_keywords('resume_content', resume_content, resume_keywords)

    return job_description, job_keywords, resume_content, resume_keywords


def handle_keywords_analyzer(job_url, job_description, resume_file, resume_content):
    job_description, job_keywords, resume_content, resume_keywords = load_data(job_url,
                                                                               job_description,
                                                                               resume_file,
                                                                               resume_content)

    match_score, common_keywords, missing_keywords, hard_skills, soft_skills, missing_hard_skills, missing_soft_skills = calculate_match_score(
        job_keywords,
        resume_keywords,
        resume_content)

    common_keywords = list(common_keywords) if common_keywords else []
    missing_keywords = list(missing_keywords) if missing_keywords else []

    job_keywords_set = set(job_keywords['hard skills']).union(
        set(job_keywords['soft skills']))
    job_keywords_list = list(
        job_keywords_set - set(common_keywords) - set(missing_keywords))

    resume_keywords_set = set(resume_keywords['hard skills']).union(
        set(resume_keywords['soft skills']))
    resume_keywords_list = list(resume_keywords_set - set(common_keywords))

    return render_template('results.html', match_score=match_score,
                           common_keywords=common_keywords,
                           missing_keywords=missing_keywords,
                           job_description=job_description or "",
                           resume_content=resume_content or "",
                           job_keywords=list(job_keywords_set),
                           resume_keywords=resume_keywords_list,
                                   hard_skills=list(hard_skills),
                                   soft_skills=list(soft_skills))


def handle_cover_letter_generation(job_url, job_description, resume_file, resume_content):
    if (job_url or job_description) and (resume_file or resume_content):
        job_description, job_keywords, resume_content, resume_keywords = load_data(
            job_url, job_description, resume_file, resume_content)

        match_score, common_keywords, missing_keywords, hard_skills, soft_skills, missing_hard_skills, missing_soft_skills = calculate_match_score(
            job_keywords, resume_keywords, resume_content)

        common_keywords = list(common_keywords) if common_keywords else []
        missing_keywords = list(missing_keywords) if missing_keywords else []

        job_keywords_set = set(job_keywords['hard skills']).union(
            set(job_keywords['soft skills']))
        job_keywords_list = list(
            job_keywords_set - set(common_keywords) - set(missing_keywords))

        resume_keywords_set = set(resume_keywords['hard skills']).union(
            set(resume_keywords['soft skills']))
        resume_keywords_list = list(resume_keywords_set - set(common_keywords))

        try:
            cover_letter = generate_cover(model, job_description, resume_content,
                                      job_keywords_set, prompts[
                                          "generate_cover_prompt"])

            return render_template('cover_letter.html', cover_letter=cover_letter,
                                   common_keywords=common_keywords,
                                   missing_keywords=missing_keywords,
                                   job_keywords=job_keywords_list,
                                   resume_keywords=resume_keywords_list)
        except Exception as e:
            print(f"Failed to generate resume enhancements: {str(e)}")

        return render_template('cover_letter.html', cover_letter=None,
                               common_keywords=common_keywords,
                               missing_keywords=missing_keywords,
                               job_keywords=job_keywords_list,
                               resume_keywords=resume_keywords_list)
    else:
        return "Error: Both job description and resume are required to generate a cover letter."


def handle_resume_enhancement_generation(job_url, job_description, resume_file,
                                         resume_content):
    if (job_url or job_description) and (resume_file or resume_content):
        job_description, job_keywords, resume_content, resume_keywords = load_data(
            job_url, job_description, resume_file, resume_content)

        match_score, common_keywords, missing_keywords, job_hard_skills, job_soft_skills, missing_hard_skills, missing_soft_skills = calculate_match_score(
            job_keywords, resume_keywords, resume_content)

        common_keywords = list(common_keywords) if common_keywords else []
        missing_keywords = list(missing_keywords) if missing_keywords else []

        missing_hard_skills = list(missing_hard_skills) if missing_hard_skills else []
        missing_soft_skills = list(missing_soft_skills) if missing_soft_skills else []

        job_keywords_set = set(job_keywords['hard skills'])
        job_keywords_hard_skills_list = list(
            job_hard_skills - set(missing_hard_skills))

        job_keywords_set = set(job_keywords['soft skills'])
        job_keywords_soft_skills_list = list(
            job_soft_skills - set(missing_soft_skills))

        try:
            enhancement_suggestions = generate_resume_enhancements(
                model,
                resume_content,
                missing_hard_skills,
                missing_soft_skills,
                prompts["resume_enhancer_prompt"]
            )

            return render_template('optimize_resume.html',
                                   enhancement_suggestions=enhancement_suggestions,
                                   resume_content=resume_content,
                                   missing_hard_skills=missing_hard_skills,
                                   missing_soft_skills=missing_soft_skills,
                                   job_hard_skills_list=job_keywords_hard_skills_list,
                                   job_soft_skills_list=job_keywords_soft_skills_list
                                   )
        except Exception as e:
            print(f"Failed to generate resume enhancements: {str(e)}")
            return render_template('optimize_resume.html',
                                   enhancement_suggestions=None,
                                   resume_content=resume_content,
                                   missing_hard_skills=missing_hard_skills,
                                   missing_soft_skills=missing_soft_skills,
                                   job_hard_skills_list=job_keywords['hard skills'],
                                   job_soft_skills_list=job_keywords['soft skills']
                                   )
    else:
        return "Error: Both job description and resume are required to generate a cover letter."


def save_file(file):
    """Save uploaded file to the uploads directory"""
    uploads_dir = './uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(uploads_dir, filename)
    file.save(file_path)
    return file_path


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

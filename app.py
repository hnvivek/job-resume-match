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


def save_file(file):
    """Save uploaded file to the uploads directory"""
    uploads_dir = './uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(uploads_dir, filename)
    file.save(file_path)
    return file_path

# Route handlers
@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_keywords():
    """Handle keyword analysis"""
    job_url = request.form.get('jobUrl')
    job_description = request.form.get('jobDescription')
    resume_file = request.files.get('file')
    resume_content = request.form.get('resumeContent')

    job_description, job_keywords, resume_content, resume_keywords = load_data(
        job_url, job_description, resume_file, resume_content
    )

    match_score, common_keywords, missing_keywords, hard_skills, soft_skills, missing_hard_skills, missing_soft_skills = calculate_match_score(
        job_keywords, resume_keywords, resume_content
    )

    return render_template('results.html',
        match_score=match_score,
        common_keywords=list(common_keywords or []),
        missing_keywords=list(missing_keywords or []),
        job_description=job_description or "",
        resume_content=resume_content or "",
        job_keywords=list(set(job_keywords['hard skills']).union(set(job_keywords['soft skills']))),
        resume_keywords=list(set(resume_keywords['hard skills']).union(set(resume_keywords['soft skills']))),
        hard_skills=list(hard_skills),
        soft_skills=list(soft_skills)
    )

@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """Handle cover letter generation"""
    job_url = request.form.get('jobUrl')
    job_description = request.form.get('jobDescription')
    resume_file = request.files.get('file')
    resume_content = request.form.get('resumeContent')

    if not ((job_url or job_description) and (resume_file or resume_content)):
        return "Error: Both job description and resume are required", 400

    try:
        job_description, job_keywords, resume_content, resume_keywords = load_data(
            job_url, job_description, resume_file, resume_content
        )

        match_score, common_keywords, missing_keywords, _, _, _, _ = calculate_match_score(
            job_keywords, resume_keywords, resume_content
        )

        job_keywords_set = set(job_keywords['hard skills']).union(set(job_keywords['soft skills']))
        cover_letter = generate_cover(
            model, job_description, resume_content, job_keywords_set,
            prompts["generate_cover_prompt"]
        )

        return render_template('cover_letter.html',
            cover_letter=cover_letter,
            common_keywords=list(common_keywords or []),
            missing_keywords=list(missing_keywords or []),
            job_keywords=list(job_keywords_set),
            resume_keywords=list(set(resume_keywords['hard skills']).union(set(resume_keywords['soft skills'])))
        )
    except Exception as e:
        print(f"Failed to generate cover letter: {str(e)}")
        return "Error generating cover letter", 500

@app.route('/optimize-resume', methods=['POST'])
def optimize_resume():
    """Handle resume optimization"""
    job_url = request.form.get('jobUrl')
    job_description = request.form.get('jobDescription')
    resume_file = request.files.get('file')
    resume_content = request.form.get('resumeContent')

    if not ((job_url or job_description) and (resume_file or resume_content)):
        return "Error: Both job description and resume are required", 400

    try:
        job_description, job_keywords, resume_content, resume_keywords = load_data(
            job_url, job_description, resume_file, resume_content
        )

        match_score, common_keywords, missing_keywords, job_hard_skills, job_soft_skills, missing_hard_skills, missing_soft_skills = calculate_match_score(
            job_keywords, resume_keywords, resume_content
        )

        enhancement_suggestions = generate_resume_enhancements(
            model,
            resume_content,
            list(missing_hard_skills or []),
            list(missing_soft_skills or []),
            prompts["resume_enhancer_prompt"]
        )

        return render_template('optimize_resume.html',
            enhancement_suggestions=enhancement_suggestions,
            resume_content=resume_content,
            missing_hard_skills=list(missing_hard_skills or []),
            missing_soft_skills=list(missing_soft_skills or []),
            job_hard_skills_list=list(job_hard_skills - set(missing_hard_skills or [])),
            job_soft_skills_list=list(job_soft_skills - set(missing_soft_skills or []))
        )
    except Exception as e:
        print(f"Failed to generate resume enhancements: {str(e)}")
        return "Error optimizing resume", 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
import os
from flask import Flask, request, render_template
from utils.prompt_loader import \
    load_prompts_from_directory  # Adjust the import as necessary
from loaders.document_loaders import extract_text_from_file  # Import your document loader
from llm.keyword_extraction import extract_keywords  # Import your LLM extractor
from utils.score_calculation import calculate_match_score  # Import your scoring function
from utils.scraper import fetch_text_from_url
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load prompts at the start of your application
prompts = load_prompts_from_directory("./prompts")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        file = request.files.get('file')

        if url:
            url_extract = fetch_text_from_url(url)  # Implement this function as needed
            job_keywords = extract_keywords(url_extract, prompts["extract_keywords"])
        else:
            job_keywords = None

        if file:
            file_path = save_file(file)
            resume_extract = extract_text_from_file(
                file_path)  # Use your existing function
            resume_keywords = extract_keywords(resume_extract,
                                               prompts["extract_keywords"])
        else:
            resume_keywords = None

        match_score, common_keywords, missing_keywords = calculate_match_score(
            job_keywords,
            resume_keywords)

        # Convert sets to lists to avoid JSON serialization issues
        common_keywords = list(common_keywords) if common_keywords else []
        missing_keywords = list(missing_keywords) if missing_keywords else []

        # Use set operations to find unique job and resume keywords
        job_keywords_set = set(job_keywords['hard skills']).union(
            set(job_keywords['soft skills']))
        job_keywords_list = list(
            job_keywords_set - set(common_keywords) - set(missing_keywords))

        resume_keywords_set = set(resume_keywords['hard skills']).union(
            set(resume_keywords['soft skills']))
        resume_keywords_list = list(resume_keywords_set - set(common_keywords))


        return render_template('results.html', match_score=match_score,
                               common_keywords=common_keywords or [],
                               missing_keywords=missing_keywords or [],
                               job_description=url_extract or "",
                               resume_text=resume_extract or "",
                               job_keywords=job_keywords_list or [],
                               resume_keywords=resume_keywords_list or [])

    return render_template('index.html',
    job_keywords=[],
    resume_keywords=[],
    common_keywords=[],
    missing_keywords= [])


def save_file(file):
    # Define the uploads directory
    uploads_dir = './uploads'

    # Create the uploads directory if it doesn't exist
    os.makedirs(uploads_dir, exist_ok=True)

    # Secure the filename and create the complete file path
    filename = secure_filename(file.filename)
    file_path = os.path.join(uploads_dir,
                             filename)  # Use os.path.join for better cross-platform compatibility
    file.save(file_path)

    return file_path


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


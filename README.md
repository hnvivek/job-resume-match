# Job Resume Match

A LLM based web application that helps users match job descriptions with resumes by 
extracting 
keywords and calculating match scores.

## Features

- Upload resumes and enter job descriptions via URL.
- Extracts keywords from job descriptions and resumes.
- Calculates a match score based on common and missing keywords.
- User-friendly interface with results displayed on the web.

## Technologies Used

- Flask: Web framework for Python.
- Docker: Containerization for easy deployment.
- HTML/CSS: For front-end rendering.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hnvivek/job-resume-match.git
   cd job-resume-match

2. Set up a virtual environment (optional but recommended):

python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`


3. Install the required packages:

`pip install -r requirements.txt`

4. Create .env file and set these below creds

`GROQ_API_KEY= <YOUR API>`

`MODEL = <YOUR OPEN SOURCE MODLE> (EX: gemma2-9b-it)`

`MAX_TOKENS= <YOUR MAX TOKEN>`

You can can get API key and model names from [GROQ](https://console.groq.com/playground) 

5. Run the application:

`python app.py`


6. Open your browser and go to http://localhost:5000.

## Docker Deployment

To deploy the application using Docker:

1. Build the Docker image:
```bash
docker build -t job-resume-match .
```


2. Run the Docker container:

```bash
docker run -p 5000:5000 job-resume-match
```
## Demo

Check out the live demo of the application at Demo Link: [Demo application]( 
https://job-resume-match-production.up.railway.app/)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

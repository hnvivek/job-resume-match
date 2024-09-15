import requests

from utils.text_processing import remove_newlines


def fetch_text_from_url(url):
    try:
        # Send a GET request to the URL
        prefix = "https://r.jina.ai/"
        response = requests.get(prefix + url)
        response.raise_for_status()  # Raise an error for bad responses

        return remove_newlines(response.text)

    except Exception as e:
        print(f"Error fetching job description: {e}")
        return None

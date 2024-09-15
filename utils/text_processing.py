import re

def clean_text(text):
    """Cleans the input text by removing unnecessary characters."""
    text = text.strip()  # Remove leading and trailing whitespace
    text = text.lower()  # Convert to lowercase (optional)
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation (optional)
    return text

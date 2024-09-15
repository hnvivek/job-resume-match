import re
import tiktoken  # Ensure tiktoken is installed

# Initialize tiktoken encoder for a specific model (e.g., "gpt-4")
encoder = tiktoken.encoding_for_model("gpt-4")

def clean_text(text):
    """Cleans the input text by removing unnecessary characters."""
    text = text.strip()  # Remove leading and trailing whitespace
    text = text.lower()  # Convert to lowercase (optional)
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation (optional)
    return text


def remove_newlines(text):
    """Removes more than one new line from text."""
    return re.sub(r'\n+', '\n', text)


def get_token_count(text):
    """Get the number of tokens in the text based on the tiktoken encoder."""
    return len(encoder.encode(text))  # Fixing tiktoken usage


def truncate_text(text, max_tokens=8000):
    """Truncate the text to fit within the max token limit."""
    encoded_text = encoder.encode(text)
    token_count = get_token_count(text)

    if token_count > max_tokens:
        truncated_tokens = encoded_text[:max_tokens]
        truncated_text = encoder.decode(truncated_tokens)
        return truncated_text
    return text


def process_text_for_model(text, max_tokens=8000):
    """
    Combines all the functions to clean the text, remove stopwords,
    and truncate it based on the model's token limit.
    """
    # Clean the text
    cleaned_text = clean_text(text)

    # Truncate the text to fit within the token limit
    final_text = truncate_text(text=cleaned_text, max_tokens=max_tokens)

    return final_text

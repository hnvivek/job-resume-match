import os

def load_prompts_from_directory(directory_path):
    """Load prompts from text files in the given directory."""
    prompts = {}
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            with open(os.path.join(directory_path, filename), 'r') as file:
                # Strip whitespace and read lines
                key = filename.split('.')[0]  # Use the filename (without extension) as the key
                prompts[key] = ' '.join(line.strip() for line in file.readlines())
    return prompts

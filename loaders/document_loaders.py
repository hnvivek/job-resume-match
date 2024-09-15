from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from utils.text_processing import clean_text

def extract_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Please provide a .pdf or .docx file.")

    documents = loader.load()

    # Collect and return extracted text
    extracted_text = "\n".join(doc.page_content for doc in documents)

    return extracted_text

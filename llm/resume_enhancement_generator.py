from langchain_groq import ChatGroq
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from data_models.resume_enhancement_models import ResumeEnhancementSuggestions
from typing import List
from langchain_core.exceptions import OutputParserException
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_resume_enhancements_with_retry(max_retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retry_model = kwargs.get('retry_model', None)
            delay_param = kwargs.get('delay', delay)  # Use passed delay or default delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except OutputParserException as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        logger.error(
                            f"All {max_retries} attempts failed. Last error: {str(e)}")
                        raise
                    if retry_model and attempt < max_retries - 1:
                        logger.info(f"Switching to retry model: {retry_model}")
                        kwargs['model'] = retry_model  # Update model to retry model
                    logger.info(f"Retrying in {delay_param} seconds...")
                    time.sleep(delay_param)
            raise Exception(
                "Max retries reached. Unable to generate resume enhancements.")

        return wrapper

    return decorator

@generate_resume_enhancements_with_retry(max_retries=3, delay=2)
def generate_resume_enhancements(model: str, resume_content: str, missing_hard_skills:
List[str], missing_soft_skills: List[str], sys_prompt: str):
    llm = ChatGroq(
        model=model,
        temperature=0.2
    )

    parser = PydanticOutputParser(pydantic_object=ResumeEnhancementSuggestions)
    format_instructions = parser.get_format_instructions()

    prompt_template = ChatPromptTemplate(
        messages=[
            HumanMessagePromptTemplate.from_template(
                "Using the provided resume content: [{resume_content}], "
                "suggest ways to incorporate the following missing skills:\n"
                "Hard Skills: {missing_hard_skills}\n"
                "Soft Skills: {missing_soft_skills}\n"
                "Provide realistic and genuine suggestions to enhance the resume. "
                "Ensure suggestions align with the candidate's background and show a natural skill progression.\n"
                "{format_instructions}"
            )
        ],
        input_variables=["resume_content", "missing_hard_skills", "missing_soft_skills"],
        partial_variables={"format_instructions": format_instructions}
    )

    messages = prompt_template.format_messages(
        resume_content=resume_content,
        missing_hard_skills=", ".join(missing_hard_skills),
        missing_soft_skills=", ".join(missing_soft_skills)
    )

    messages.insert(0, ("system", sys_prompt))

    response = llm.invoke(messages)
    logger.info(f"LLM Response: {response.content}")

    try:
        parsed_output = parser.parse(response.content)
        logger.info(f"Parsed output: {parsed_output}")
        return parsed_output
    except Exception as e:
        logger.error(f"Error parsing LLM output: {str(e)}")
        raise OutputParserException(f"Failed to parse LLM output: {str(e)}")
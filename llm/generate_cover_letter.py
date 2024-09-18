from langchain_groq import ChatGroq
from datetime import date
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from data_models.keywords_model import KeywordsModel
from data_models.cover_letter_model import CoverLetterModel

def generate_cover(model: str, job_description: str, resume_content: str, skills_keywords: KeywordsModel, sys_prompt: str):
    llm = ChatGroq(
        model=model,
        temperature=0.0,
        max_retries=2
    )

    today = date.today().strftime("%B %d, %Y")

    # Create the parser
    parser = PydanticOutputParser(pydantic_object=CoverLetterModel)

    # Get the format instructions
    format_instructions = parser.get_format_instructions()

    # Create the prompt template
    prompt_template = ChatPromptTemplate(
        messages=[
            HumanMessagePromptTemplate.from_template(
                "The Current date is {today}. Using the provided job description: [{job_description}], "
                "resume content: [{resume_content}] and keywords: [{skills_keywords}], "
                "generate a personalized, unique cover letter for the candidate that will stand out to the employer. "
                "Bold key skills. Output in markdown format. 400 words max.\n{format_instructions}"
            )
        ],
        input_variables=["today", "job_description", "resume_content", "skills_keywords"],
        partial_variables={"format_instructions": format_instructions}
    )

    # Generate the messages
    messages = prompt_template.format_messages(
        today=today,
        job_description=job_description,
        resume_content=resume_content,
        skills_keywords=skills_keywords
    )

    # Add the system message
    messages.insert(0, ("system", sys_prompt))

    # Generate the response
    response = llm.invoke(messages)

    # Parse the output
    parsed_output = parser.parse(response.content)

    # Combine the parsed output into a formatted cover letter
    cover_letter = f"""
{parsed_output.header}

{parsed_output.date}

{parsed_output.recipient}

{parsed_output.salutation}

{parsed_output.opening_paragraph}

{parsed_output.body_paragraph_1}

{parsed_output.body_paragraph_2}

{parsed_output.closing_paragraph}

{parsed_output.complimentary_close}
"""

    return cover_letter
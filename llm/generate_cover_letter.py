from langchain_groq import ChatGroq
from datetime import date


def generate_cover(model, job_description, resume_content, skills_keywords,
                         sys_prompt):
    llm = ChatGroq(
        model=model,
        temperature=0.0,
        max_retries=2
    )

    today = date.today()

    messages = [
        ("system", f"{sys_prompt}"),
        ("human", f"""The Current date is {today}, Using the provided job description: [{job_description}], resume content: [{resume_content}] and keywords: [{skills_keywords}], generate a personalized, unique cover letter for the candidate that will stand out to the employer. Bold key skills. Output in markdown format. 400 words max."""
         ),
    ]

    response = llm.invoke(messages)

    return response.content



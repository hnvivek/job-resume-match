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
        ("human",
        f"""The Current date is {today} Please generate a unique cover letter 
        with in 500 words tailored for the Job description : [{job_description}] using 
        my resume: [{resume_content}].
        I'm very interested in this position and want to grab the hiring manager's attention.
        Include my name, relevant skills, work history, and past employers and projects from my resume.
        I've also provided some important skills below extracted from 
        the job description to incorporate in cover letter and bold them: Skills 
        [{skills_keywords}] 
        Write the cover letter in a personable, authentic style and return the response in Markdown format.
        The output should be polished and ready to drop into a WYSIWYG editor."""
         ),
    ]

    response = llm.invoke(messages)

    return response.content



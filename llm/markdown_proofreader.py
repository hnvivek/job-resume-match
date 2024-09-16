from langchain_groq import ChatGroq

from playground import skills_keywords


def proofreader(model, user_input, skills_keywords, sys_prompt):
    llm = ChatGroq(
        model=model,
        temperature=0.0,
        max_retries=2
    )

    messages = [
        ("system", f"{sys_prompt}"),
        ("human", f"Please proofread and correct the following markdown text: ["
                  f"{user_input}] and bold if these key skills exist in the provided "
                  f"text skills : [{skills_keywords}]"),
    ]

    response = llm.invoke(messages)

    return response.content

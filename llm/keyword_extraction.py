from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from data_models.keywords import KeywordsModel

def extract_keywords(user_input, sys_prompt):
    llm = ChatGroq(
        model="gemma2-9b-it",
        temperature=0.0,
        max_retries=2
    )

    messages = [
        ("system", f"{sys_prompt}"),
        ("human", f"Extract the key hard skills and soft skills represented in the following resume text: [{user_input}]"),
    ]

    response = llm.invoke(messages)

    # Set up a JSON parser
    parser = JsonOutputParser(pydantic_object=KeywordsModel)

    parsed_output = parser.parse(response.content)

    return parsed_output

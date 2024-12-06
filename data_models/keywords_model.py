from langchain_core.pydantic_v1 import BaseModel, Field

# Define your desired data structure.
class KeywordsModel(BaseModel):
    hard_skills: list = Field(description="list of hard skills")
    soft_skills: list = Field(description="list of soft skills")

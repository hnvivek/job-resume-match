
# File: data_models/cover_letter_model.py

from langchain_core.pydantic_v1 import BaseModel, Field

class CoverLetterModel(BaseModel):
    header: str = Field(description="The header of the cover letter including name, job title, and contact information")
    date: str = Field(description="The current date")
    recipient: str = Field(description="The recipient's information")
    salutation: str = Field(description="The salutation of the cover letter")
    opening_paragraph: str = Field(description="The opening paragraph of the cover letter")
    body_paragraph_1: str = Field(description="The first body paragraph of the cover letter")
    body_paragraph_2: str = Field(description="The second body paragraph of the cover letter")
    closing_paragraph: str = Field(description="The closing paragraph of the cover letter")
    complimentary_close: str = Field(description="The complimentary close of the cover letter")
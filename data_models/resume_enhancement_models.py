from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional

class EnhancementSuggestion(BaseModel):
    keyword: str = Field(description="The keyword being suggested")
    suggestion: str = Field(description="Suggestion on how to incorporate the keyword")
    original: Optional[str] = Field(default=None, description="Original bullet point if modifying existing content")
    modified_or_new: str = Field(description="Modified or new bullet point")
    placement: str = Field(description="Where to add or modify in the resume")
    rationale: str = Field(description="Explanation of why this suggestion is realistic")

class ResumeEnhancementSuggestions(BaseModel):
    hard_skills: List[EnhancementSuggestion] = Field(description="Suggestions for incorporating hard skills")
    soft_skills: List[EnhancementSuggestion] = Field(description="Suggestions for incorporating soft skills")
import pydantic
from typing import Optional

class CreateAd(pydantic.BaseModel):
    title: str
    description: str
    owner: str

class PatchAd(pydantic.BaseModel):
    title: Optional[str]
    description: Optional[str]
    


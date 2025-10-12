from typing import List
from pydantic import BaseModel, RootModel

class StudentRating(BaseModel):
    id: int
    full_name: str
    photo_path: str | None
    position: int
    amount: int

class StudentRatingList(RootModel):
    root: List[StudentRating]
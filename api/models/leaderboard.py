from typing import List
from pydantic import BaseModel, RootModel

class StudentRating(BaseModel):
    id: int | None
    full_name: str | None
    photo_path: str | None
    position: int | None
    amount: int | None

class StudentRatingList(RootModel):
    root: List[StudentRating]
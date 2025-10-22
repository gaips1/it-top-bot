from typing import List
from pydantic import BaseModel, Field, RootModel
from datetime import datetime

class LessonEvalucation(BaseModel):
    key: str
    date_visit: datetime
    fio_teach: str
    spec_name: str
    teach_photo: str | None

class EvalucateLessonData(BaseModel):
    key: str
    mark_lesson: int
    mark_teach: int
    tags_lesson: List[str] = Field(default_factory=list)
    tags_teach: List[str] = Field(default_factory=list)

class EvalucationList(RootModel):
    root: List[LessonEvalucation]
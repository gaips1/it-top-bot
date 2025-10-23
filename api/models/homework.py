from typing import List
from datetime import datetime
from pydantic import BaseModel, RootModel

class HomeworkStud(BaseModel):
    id: int
    filename: str | None = None
    file_path: str | None = None
    tmp_file: str | None = None
    mark: int | None = None
    creation_time: datetime
    stud_answer: str | None = None
    auto_mark: bool

class HomeworkComment(BaseModel):
    text_comment: str | None = None
    attachment: str | None = None
    attachment_path: str | None = None
    date_updated: datetime

class Homework(BaseModel):
    id: int
    id_spec: int
    id_teach: int
    id_group: int
    fio_teach: str
    theme: str
    completion_time: datetime
    creation_time: datetime
    overdue_time: datetime
    filename: str | None = None
    file_path: str
    comment: str
    name_spec: str
    status: int
    common_status: int | None = None
    homework_stud: HomeworkStud | None = None
    homework_comment: HomeworkComment | None = None
    cover_image: str | None = None

class HomeworkCounter(BaseModel):
    counter_type: int
    counter: int

class HomeworkCounterList(RootModel):
    root: List[HomeworkCounter]

class HomeworkList(RootModel):
    root: List[Homework]
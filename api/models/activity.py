from typing import List
from datetime import datetime
from pydantic import BaseModel, RootModel

status_was_translations = {
    0: "Отсутствовал",
    1: "Присутствовал",
    2: "Опоздал"
}

class Activity(BaseModel):
    date_visit: datetime
    lesson_number: int
    status_was: int
    spec_id: int
    teacher_name: str
    spec_name: str
    lesson_theme: str

    control_work_mark: int | None
    home_work_mark: int | None
    lab_work_mark: int | None
    class_work_mark: int | None
    practical_work_mark: int | None

    @property
    def status_was_translated(self) -> str:
        return status_was_translations.get(self.status_was, "Неизвестно")

    @property
    def all_marks(self) -> List[int]:
        marks = [
            self.control_work_mark,
            self.home_work_mark,
            self.lab_work_mark,
            self.class_work_mark,
            self.practical_work_mark
        ]
        return [mark for mark in marks if mark is not None]

class ActivityList(RootModel):
    root: List[Activity]
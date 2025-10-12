from datetime import datetime
from typing import List
from pydantic import BaseModel, RootModel

class RewardRecord(BaseModel):
    date: datetime
    action: int
    current_point: int
    point_types_id: int
    point_types_name: str
    achievements_id: int
    achievements_name: str
    achievements_type: int
    badge: int
    old_competition: bool

    @property
    def point_types_name_translated(self) -> str:
        return point_types_translations.get(self.point_types_name, self.point_types_name)
    
    @property
    def achievements_name_translated(self) -> str:
        return achievements_translations.get(self.achievements_name, self.achievements_name)

class RewardsHistory(RootModel):
    root: List[RewardRecord]

point_types_translations = {
    "DIAMOND": "Топкоины",
    "COIN": "Топгемы"
}

achievements_translations = {
    "EVALUATION_LESSON_MARK": "Оценка занятия",
    "PAIR_VISIT": "Посещение пары",
    "WORK_IN_CLASS": "Поощрение от преподавателя за работу на уроке",
    "ASSESMENT": "Оценка",

    "HOMETASK_INTIME": "Своевременная сдача ДЗ",
    "20_VISITS_WITHOUT_DELAY": "20 посещений без опозданий",
    "20_VISITS_WITHOUT_GAP": "20 посещений без пропусков",
    "10_VISITS_WITHOUT_DELAY": "10 посещений без опозданий",
    "10_VISITS_WITHOUT_GAP": "10 посещений без пропусков",
    "5_VISITS_WITHOUT_DELAY": "5 посещений без опозданий",
    "5_VISITS_WITHOUT_GAP": "5 посещений без пропусков",
    
    "FILL_IN_PROFILE": "Заполнение профиля",
    "EMAIL_CONFIRMATION": "Подтверждение почты"
}
from datetime import date, datetime
from typing import List, Any, Optional
from pydantic import BaseModel, Field

class Group(BaseModel):
    group_status: int
    is_primary: bool
    id: int
    name: str

class GamingPoint(BaseModel):
    new_gaming_point_types__id: int = Field(..., alias='new_gaming_point_types__id')
    points: int

class Visibility(BaseModel):
    is_design: bool
    is_video_courses: bool
    is_vacancy: bool
    is_signal: bool
    is_promo: bool
    is_test: bool
    is_email_verified: bool
    is_quizzes_expired: bool
    is_debtor: bool
    is_phone_verified: bool
    is_only_profile: bool
    is_referral_program: bool
    is_dz_group_issue: bool
    is_birthday: bool
    is_school: bool
    is_news_popup: bool
    is_school_branch: bool
    is_college_branch: bool
    is_higher_education_branch: bool
    is_russian_branch: bool

class StudentProfile(BaseModel):
    groups: List[Group]
    manual_link: Optional[Any]
    student_id: int
    current_group_id: int
    full_name: str
    achieves_count: int
    stream_id: int
    stream_name: str
    group_name: str
    level: int
    photo: str
    gaming_points: List[GamingPoint]
    spent_gaming_points: List[Any]
    visibility: Visibility
    current_group_status: int
    birthday: date
    age: int
    last_date_visit: datetime
    registration_date: datetime
    gender: int
    study_form_short_name: str
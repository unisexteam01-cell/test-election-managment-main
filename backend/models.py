from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    KARYAKARTA = "karyakarta"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class FavorCategory(str, Enum):
    SUPPORTER = "supporter"
    NEUTRAL = "neutral"
    OPPOSITION = "opposition"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class IssueStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"

class QuestionType(str, Enum):
    MCQ = "mcq"
    YES_NO = "yesno"
    RATING = "rating"
    TEXT = "text"
    NUMBER = "number"
    DROPDOWN = "dropdown"
    PHONE = "phone"

# User Models
class ActivityStats(BaseModel):
    surveys_completed: int = 0
    voters_visited: int = 0
    coverage_percentage: float = 0.0

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    password: str
    created_by: Optional[str] = None
    assigned_admin_id: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: str = Field(alias="_id")
    created_by: Optional[str] = None
    assigned_admin_id: Optional[str] = None
    last_login: Optional[datetime] = None
    active_status: bool = True
    profile_photo: Optional[str] = None
    activity_stats: ActivityStats = Field(default_factory=ActivityStats)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

# Voter Models
class GPSCoordinates(BaseModel):
    latitude: float
    longitude: float

class VoterNote(BaseModel):
    text: str
    created_by: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class VoterBase(BaseModel):
    voter_id: Optional[str] = None
    name: str
    surname: Optional[str] = None
    full_name: Optional[str] = None
    gender: Gender
    age: int
    date_of_birth: Optional[str] = None
    caste: Optional[str] = None
    religion: Optional[str] = None
    sub_caste: Optional[str] = None
    area: str
    ward: Optional[str] = None
    booth_number: str
    booth_name: Optional[str] = None
    address: Optional[str] = None
    landmark: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    family_id: Optional[str] = None
    household_group: Optional[str] = None
    relation_to_head: Optional[str] = None

class VoterCreate(VoterBase):
    pass

class Voter(VoterBase):
    id: str = Field(alias="_id")
    favor_score: float = 50.0
    favor_category: FavorCategory = FavorCategory.NEUTRAL
    visited_status: bool = False
    visited_by: Optional[str] = None
    visited_date: Optional[datetime] = None
    visit_count: int = 0
    voted_status: bool = False
    voted_timestamp: Optional[datetime] = None
    assigned_to: Optional[str] = None
    assigned_by: Optional[str] = None
    assigned_date: Optional[datetime] = None
    gps_coordinates: Optional[GPSCoordinates] = None
    tags: List[str] = Field(default_factory=list)
    notes: List[VoterNote] = Field(default_factory=list)
    survey_history: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    imported_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

class VoterFilter(BaseModel):
    gender: Optional[Gender] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    area: Optional[str] = None
    ward: Optional[str] = None
    booth_number: Optional[str] = None
    caste: Optional[str] = None
    family_id: Optional[str] = None
    favor_score_min: Optional[float] = None
    favor_score_max: Optional[float] = None
    survey_completed: Optional[bool] = None
    visited: Optional[bool] = None
    voted: Optional[bool] = None
    assigned_user: Optional[str] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None

class VoterBulkUpdate(BaseModel):
    voter_ids: List[str]
    updates: Dict[str, Any]

class VoterAssignment(BaseModel):
    voter_ids: List[str]
    karyakarta_id: str
    mode: str = "manual"  # manual or auto

# Survey Models
class ConditionalLogic(BaseModel):
    show_if_question_id: str
    show_if_answer: Any

class SurveyQuestion(BaseModel):
    id: str
    type: QuestionType
    question_text: str
    question_text_marathi: Optional[str] = None
    options: List[str] = Field(default_factory=list)
    required: bool = True
    validation_rules: Optional[Dict[str, Any]] = None
    conditional_logic: Optional[ConditionalLogic] = None

class SurveyTemplateCreate(BaseModel):
    template_name: str
    questions: List[SurveyQuestion]
    consent_question: Optional[str] = None
    is_default: bool = False

class SurveyTemplate(SurveyTemplateCreate):
    id: str = Field(alias="_id")
    created_by: str
    active_status: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class SurveyResponse(BaseModel):
    question_id: str
    answer: Any

class SurveySubmit(BaseModel):
    voter_id: str
    template_id: str
    responses: List[SurveyResponse]
    gps_location: Optional[GPSCoordinates] = None
    photos: List[str] = Field(default_factory=list)  # base64 strings
    audio_notes: List[str] = Field(default_factory=list)  # base64 strings
    device_id: Optional[str] = None

class Survey(SurveySubmit):
    id: str = Field(alias="_id")
    karyakarta_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    favor_score_impact: float = 0.0
    duration_seconds: Optional[int] = None

    class Config:
        populate_by_name = True

# Task Models
class TaskCreate(BaseModel):
    assigned_to: str
    task_type: str
    description: str
    target_voters: List[str] = Field(default_factory=list)
    target_area: Optional[str] = None
    target_booth: Optional[str] = None
    due_date: Optional[datetime] = None

class Task(TaskCreate):
    id: str = Field(alias="_id")
    assigned_by: str
    status: TaskStatus = TaskStatus.PENDING
    completion_percentage: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

# Family Models
class Family(BaseModel):
    id: str = Field(alias="_id")
    family_id: str
    family_head_name: str
    family_head_voter_id: Optional[str] = None
    members: List[str] = Field(default_factory=list)  # voter_ids
    total_members: int = 0
    family_favor_score: float = 50.0
    area: Optional[str] = None
    booth_number: Optional[str] = None
    all_visited: bool = False
    all_voted: bool = False

    class Config:
        populate_by_name = True

# Influencer Models
class InfluencerCreate(BaseModel):
    name: str
    voter_id: Optional[str] = None
    area: str
    network_size: int = 0
    influence_level: int = 1  # 1-5
    linked_voters: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    contact_info: Optional[str] = None

class Influencer(InfluencerCreate):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

# Issue Models
class IssueCreate(BaseModel):
    voter_id: str
    issue_type: str
    description: str
    priority: int = 1  # 1-5

class Issue(IssueCreate):
    id: str = Field(alias="_id")
    reported_by: str
    status: IssueStatus = IssueStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

# Favor Score Config
class FavorScoreWeights(BaseModel):
    survey: float = 40.0
    caste: float = 30.0
    booth: float = 20.0
    history: float = 10.0

class FavorScoreConfig(BaseModel):
    id: str = Field(alias="_id")
    config_name: str
    weights: FavorScoreWeights = Field(default_factory=FavorScoreWeights)
    caste_weightage: Dict[str, float] = Field(default_factory=dict)
    booth_weightage: Dict[str, float] = Field(default_factory=dict)
    updated_by: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

# Import Log Models
class ImportError(BaseModel):
    row_number: int
    error_message: str
    row_data: Dict[str, Any]

class ImportLog(BaseModel):
    id: str = Field(alias="_id")
    filename: str
    imported_by: str
    total_rows: int
    success_count: int
    error_count: int
    errors: List[ImportError] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"

    class Config:
        populate_by_name = True

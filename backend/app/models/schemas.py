from typing import Optional, Dict, List
from pydantic import BaseModel, Field

class Skill(BaseModel):
    name: str = Field(..., description="Normalized skill name (e.g. 'React', 'Python')")
    category: str = Field(..., description="Category (e.g. 'Programming Language', 'Frontend', 'Backend')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score from 0.0 to 1.0")
    evidence: str = Field(..., description="Verbatim or near-verbatim quote from resume demonstrating the skill")
    is_explicit: bool = Field(default=True, description="True if explicitly mentioned, False if strongly implied")

class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename: str
    file_size_bytes: int
    page_count: int
    preview_text: str

class ResumeAnalysis(BaseModel):
    resume_id: str
    filename: str
    total_skills: int
    skills: List[Skill]
    categories: Dict[str, List[str]]
    is_demo_mode: bool = False

class JobSkill(BaseModel):
    name: str = Field(..., description="Normalized skill name")
    importance: str = Field(default="high", description="'high', 'medium', or 'low'")
    category: Optional[str] = Field(default="General", description="Skill category")
    relevance_reason: Optional[str] = Field(default=None, description="Brief explanation of why this skill is relevant")

class JobRoleRequest(BaseModel):
    job_role: str = Field(..., min_length=2, description="Target job title (e.g. 'Full Stack Developer')")

class JobRoleAnalysis(BaseModel):
    job_role: str
    skills: List[JobSkill]
    is_demo_mode: bool = False

class SkillGapRequest(BaseModel):
    resume_skills: List[str] = Field(..., description="List of extracted skill names from resume")
    job_skills: List[JobSkill] = Field(..., description="List of target role skills")
    job_role: Optional[str] = Field(default="Target Role", description="Name of the target role")

class MissingSkillDetail(BaseModel):
    name: str
    importance: str
    rank: int
    relevance_reason: str
    category: Optional[str] = None

class SkillGapResult(BaseModel):
    job_role: str
    total_target_skills: int
    total_resume_skills: int
    matched_skills: List[str]
    missing_skills: List[str]
    top_missing_skills: List[MissingSkillDetail]
    match_percentage: float
    summary: str

class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    llm_model: str
    demo_mode: bool

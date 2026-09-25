import uuid
import time
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from ..config import settings
from ..models.schemas import (
    ResumeUploadResponse,
    ResumeAnalysis,
    JobRoleRequest,
    JobRoleAnalysis,
    SkillGapRequest,
    SkillGapResult,
    HealthResponse
)
from ..services.pdf_extractor import extract_text_from_pdf, PDFExtractionError
from ..services.skill_extractor import extract_and_normalize_skills
from ..services.job_analyzer import analyze_job_role, JOB_ROLE_CATALOG
from ..services.skill_matcher import compare_skills_gap

router = APIRouter(prefix="/api")

# Temporary in-memory storage for uploaded resume text (cleaned up periodically or on access)
# Maps resume_id -> {"filename": str, "text": str, "timestamp": float}
RESUME_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour

def cleanup_cache():
    """Remove expired resume entries from in-memory cache."""
    now = time.time()
    expired = [rid for rid, data in RESUME_CACHE.items() if now - data.get("timestamp", 0) > CACHE_TTL_SECONDS]
    for rid in expired:
        RESUME_CACHE.pop(rid, None)

# High-quality sample resume text for 1-click demonstration
SAMPLE_RESUME_TEXT = """
Alex Morgan
Full Stack Software Engineer | San Francisco, CA | alex.morgan@example.com | github.com/alexmorgan

PROFESSIONAL SUMMARY
Dynamic Software Engineer with 4+ years of hands-on experience designing and building scalable web applications.
Proficient in modern frontend and backend architectures, reactive user interfaces, and automated cloud deployments.
Strong track record in collaborative Agile environments, optimizing system performance, and writing clean, tested code.

TECHNICAL SKILLS
• Programming Languages: JavaScript (ES6+), TypeScript, Python, HTML5, CSS3, SQL
• Frontend Engineering: React, ReactJS, Next.js, Redux, Tailwind CSS, Bootstrap
• Backend Engineering: FastAPI, Python microservices, RESTful APIs, Flask
• Databases & Storage: PostgreSQL, Postgres, MongoDB, Redis
• Cloud & DevOps: Docker, Docker containers, AWS Cloud (EC2, S3), Git, GitHub Actions, CI/CD, Linux
• Testing & Practices: PyTest, Unit Testing, Agile / Scrum, Problem Solving, Communication

PROFESSIONAL EXPERIENCE

Senior Frontend & Full Stack Developer | NexaTech Solutions (2022 - Present)
• Developed responsive single-page web applications using React, TypeScript, and Tailwind CSS serving 150K+ daily active users.
• Migrated legacy JavaScript codebase to modern TypeScript, reducing client-side runtime errors by 42%.
• Built high-performance asynchronous RESTful APIs using Python and FastAPI for customer analytics ingestion.
• Integrated PostgreSQL and Redis caching layers, cutting average database response latency from 220ms to 45ms.
• Configured CI/CD deployment pipelines using GitHub Actions and Docker containers for automated unit testing.

Software Engineer | CloudScale Systems (2020 - 2022)
• Engineered web services and internal operational dashboards using Python, Flask, and React.js.
• Managed relational database schemas and complex analytical queries using SQL and PostgreSQL.
• Participated in daily Agile/Scrum standups, code reviews, sprint planning, and mentored junior developers.
• Collaborated with product design teams to ensure accessible, intuitive user experience and responsive styling.

EDUCATION & CERTIFICATIONS
• Bachelor of Science in Computer Science, University of California, Berkeley
• AWS Certified Cloud Practitioner
"""

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health and configuration check endpoint."""
    return HealthResponse(
        status="healthy",
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        demo_mode=settings.demo_mode or not bool(settings.llm_api_key)
    )

@router.get("/job/roles")
async def get_preset_job_roles():
    """Returns the list of recommended preset job roles."""
    return {"roles": list(JOB_ROLE_CATALOG.keys())}

@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Accepts resume PDF upload, validates format and size, extracts cleaned text,
    and returns resume ID and preview.
    """
    cleanup_cache()

    # Validate filename extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF documents (.pdf) are allowed."
        )

    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read the uploaded file."
        )

    # Validate file size (10 MB)
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.max_upload_size_mb} MB."
        )

    # Extract text using PyMuPDF
    try:
        extraction = extract_text_from_pdf(content)
    except PDFExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the PDF resume. Please verify the document format."
        )

    # Generate unique resume id and cache text
    resume_id = str(uuid.uuid4())
    RESUME_CACHE[resume_id] = {
        "filename": file.filename,
        "text": extraction["text"],
        "timestamp": time.time(),
        "file_size": len(content),
        "page_count": extraction["page_count"]
    }

    return ResumeUploadResponse(
        resume_id=resume_id,
        filename=file.filename,
        file_size_bytes=len(content),
        page_count=extraction["page_count"],
        preview_text=extraction["preview"]
    )

@router.post("/resume/{resume_id}/analyze", response_model=ResumeAnalysis)
async def analyze_resume(resume_id: str):
    """
    Extracts, normalizes, and categorizes skills from an uploaded resume.
    """
    resume_data = RESUME_CACHE.get(resume_id)
    if not resume_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or session has expired. Please re-upload your resume PDF."
        )

    try:
        analysis = await extract_and_normalize_skills(
            resume_id=resume_id,
            filename=resume_data["filename"],
            resume_text=resume_data["text"]
        )
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Skill analysis is temporarily unavailable. Please try again."
        )

@router.post("/job/analyze", response_model=JobRoleAnalysis)
async def analyze_job(req: JobRoleRequest):
    """
    Identifies expected industry skills and relative importance for a target job role.
    """
    try:
        result = await analyze_job_role(req.job_role)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Job role analysis is temporarily unavailable. Please try again."
        )

@router.post("/skill-gap", response_model=SkillGapResult)
async def calculate_skill_gap(req: SkillGapRequest):
    """
    Performs deterministic skill gap analysis between resume skills and target job skills.
    Returns matched skills, missing skills, and top 3 missing skills with rationale.
    """
    try:
        result = compare_skills_gap(
            resume_skill_names=req.resume_skills,
            job_skills=req.job_skills,
            job_role=req.job_role or "Target Role"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate skill gap analysis."
        )

@router.post("/demo/load-sample", response_model=ResumeUploadResponse)
async def load_sample_resume():
    """
    Convenience endpoint for 1-click demonstration: loads a pre-formatted
    comprehensive developer resume without needing to browse for a PDF file.
    """
    resume_id = "demo-sample-alex-morgan"
    filename = "alex_morgan_fullstack_resume.pdf"
    RESUME_CACHE[resume_id] = {
        "filename": filename,
        "text": SAMPLE_RESUME_TEXT.strip(),
        "timestamp": time.time(),
        "file_size": 24576,
        "page_count": 2
    }
    return ResumeUploadResponse(
        resume_id=resume_id,
        filename=filename,
        file_size_bytes=24576,
        page_count=2,
        preview_text=SAMPLE_RESUME_TEXT.strip()[:400] + "..."
    )

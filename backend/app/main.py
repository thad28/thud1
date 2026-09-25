import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("resume_extractor")

app = FastAPI(
    title=settings.app_name,
    description="Full-stack AI Resume Skill Extractor & Job Skill Gap Analyzer backend API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Ensures unhandled exceptions return a clean, user-friendly message
    without leaking internal stack traces or system environment secrets.
    """
    logger.error(f"Unhandled exception at {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal service error occurred. Please try again later."}
    )

@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "status": "online",
        "docs": "/docs",
        "demo_mode": settings.demo_mode or not bool(settings.llm_api_key),
        "endpoints": {
            "upload": "POST /api/resume/upload",
            "analyze": "POST /api/resume/{resume_id}/analyze",
            "job_analyze": "POST /api/job/analyze",
            "skill_gap": "POST /api/skill-gap",
            "health": "GET /api/health",
            "load_sample": "POST /api/demo/load-sample"
        }
    }

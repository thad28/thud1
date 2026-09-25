# AI Resume Skill Extractor & Job Skill Gap Analyzer

A full-stack, AI-powered application that extracts, normalizes, and categorizes technical and professional skills from PDF resumes, then performs deterministic skill gap analysis against industry target job roles to highlight the **top 3 missing skills** with career relevance explanations.

---

## Architecture Overview

```
                      +-----------------------------+
                      |       React Frontend        |
                      |   TypeScript + Tailwind CSS |
                      +--------------+--------------+
                                     |
                          REST API Requests (JSON)
                                     v
                      +-----------------------------+
                      |       FastAPI Backend       |
                      |          (Python)           |
                      +--------------+--------------+
                                     |
      +------------------------------+------------------------------+
      |                              |                              |
      v                              v                              v
+---------------+            +---------------+            +-------------------+
|    PyMuPDF    |            |   LLM Engine  |            |   Deterministic   |
|   Extractor   |            | Gemini/OpenAI |            |   Skill Matcher   |
| (Clean Text)  |            |  (Structured) |            |  (Set Difference) |
+---------------+            +---------------+            +-------------------+
```

### Application Flow

```
PDF Upload
    ↓
PDF Text Extraction (PyMuPDF / fitz)
    ↓
Text Cleaning & Normalization (collapses whitespace, removes artifacts)
    ↓
LLM / Heuristic Skill Identification (extracts skills + verbatim evidence)
    ↓
Skill Normalization & Deduplication (e.g. ReactJS → React, JS → JavaScript)
    ↓
Target Job Role Analysis (presets or custom role via LLM)
    ↓
Skill Gap Analysis (target_skills - resume_skills)
    ↓
Top 3 Missing Skills with Rationale & Match Score %
```

---

## Key Features

1. **Robust PDF Text Extraction**:
   - Built on `PyMuPDF` (`fitz`) for fast, accurate multi-page PDF processing.
   - Cleans excessive whitespace, normalizes unicode punctuation, and handles multi-column layouts.
   - Rejects empty, scanned, or non-PDF files with clear, user-friendly guidance.
2. **AI Skill Identification & Extraction**:
   - Structured JSON schema output from LLM (configurable provider: Gemini or OpenAI).
   - Distinguishes explicitly mentioned skills from contextually inferred skills.
   - Provides verbatim sentence quotes from the resume as evidence for every extracted skill.
3. **Canonical Skill Normalization & Deduplication**:
   - Resolves aliases to industry standard names (e.g., `JS` → `JavaScript`, `ReactJS` / `React.js` → `React`, `Postgres` → `PostgreSQL`, `k8s` → `Kubernetes`, `ML` → `Machine Learning`).
   - Merges duplicates into a single entry with the highest confidence score and consolidated evidence.
4. **Interactive Dashboard**:
   - Real-time search filter and category tabs (Programming, Frontend, Backend, Database, Cloud/DevOps, AI/ML, Tools, Soft Skills).
   - Category-colored skill badges with confidence percentage pills.
   - Clickable chips to inspect resume evidence quotes in a dedicated modal.
5. **Target Job Role Benchmarking**:
   - Pre-configured catalog for 15+ tech roles (Full Stack, Backend, Frontend, Data Scientist, ML Engineer, DevOps, etc.).
   - Support for custom job roles (e.g., *"Senior Cloud Architect"*), dynamically analyzed via LLM.
6. **Deterministic Skill Gap Matching**:
   - Set-difference comparison on normalized skill tokens (`target_skills - resume_skills`).
   - Match alignment score percentage gauge.
7. **Top 3 Missing Skills with Explanations**:
   - Highlights exactly the top 3 missing skills prioritized by importance (`high` > `medium` > `low`).
   - Concise, objective explanations explaining why each skill is valuable for that specific role.
8. **Demo Mode (Zero-Config Testing)**:
   - When no API key is supplied or `DEMO_MODE=true`, the system runs a realistic offline engine scanning 200+ tech competencies with real evidence extraction.
   - Includes a **1-Click "Load Sample Resume"** button for immediate testing.

---

## AI Concepts Demonstrated

- **PDF/Text Extraction & Sanitization**: Converting binary documents into clean textual data suitable for language models.
- **LLM-Based Skill Identification**: Few-shot / structured prompt extraction extracting competencies and supporting evidence quotes without hallucinating unsupported skills.
- **Skill Normalization**: Mapping colloquial aliases and variations to canonical taxonomy standards.
- **Job-Role Benchmark Synthesis**: Inferring expected core and complementary industry skill requirements for standard or arbitrary titles.
- **Hybrid Deterministic Matching**: Combining LLMs for unstructured semantic extraction and deterministic set algebra for verifiable, reliable gap matching.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Tailwind CSS, Vite, Lucide React Icons |
| **Backend** | Python 3.12, FastAPI, Uvicorn, Pydantic v2 |
| **PDF Extraction**| PyMuPDF (`pymupdf`) |
| **AI / LLM** | Google Gemini / OpenAI (configurable via `.env`), Heuristic Demo Engine |
| **Testing** | Pytest, FastAPI TestClient |

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app, CORS, error handling
│   │   ├── config.py                  # Settings & environment variables
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py              # REST endpoints (/upload, /analyze, /skill-gap)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py             # Pydantic models (Skill, JobSkill, SkillGapResult)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pdf_extractor.py       # PyMuPDF parser & text cleaner
│   │   │   ├── skill_extractor.py     # LLM extraction & heuristic fallback
│   │   │   ├── job_analyzer.py        # Industry benchmarks & custom role analysis
│   │   │   └── skill_matcher.py       # Normalization dictionary & gap matching
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── skill_extraction.py    # Dedicated LLM extraction prompt
│   │       └── job_analysis.py        # Dedicated LLM job role prompt
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_pdf_extractor.py      # PDF text extraction & error test cases
│   │   ├── test_skill_normalization.py# Alias resolution & deduplication tests
│   │   ├── test_skill_matcher.py      # Set difference & top-3 missing tests
│   │   └── test_api_endpoints.py      # Full integration endpoint tests
│   ├── sample_data/
│   │   └── sample_resume.pdf          # Pre-built test PDF
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx             # Header, engine indicator, demo loader
│   │   │   ├── ResumeUpload.tsx       # Dropzone, validation, progress state
│   │   │   ├── SkillBadges.tsx        # Categorized badge grid, search & filter
│   │   │   ├── JobRoleSelector.tsx    # Preset role selector & custom role input
│   │   │   ├── SkillGapCard.tsx       # Match score gauge & top-3 missing skills
│   │   │   └── EvidenceModal.tsx      # Verbatim resume quote inspector
│   │   ├── pages/
│   │   │   └── Dashboard.tsx          # Main state orchestrator
│   │   ├── services/
│   │   │   └── api.ts                 # Typed fetch client
│   │   ├── types/
│   │   │   └── index.ts               # TypeScript interfaces
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css                  # Tailwind styles & modern aesthetics
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── README.md
└── .gitignore
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run backend server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend API will be available at:
- **API Base**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Run frontend dev server
npm run dev
```

The frontend will be available at:
- **Web App**: `http://localhost:5173`

---

## Environment Variables

Edit `backend/.env`:

```ini
# LLM Provider ('gemini' or 'openai')
LLM_PROVIDER=gemini

# Your LLM API key (leave blank to use Heuristic Demo Mode)
LLM_API_KEY=your_api_key_here

# Model name
LLM_MODEL=gemini-1.5-flash

# Set to true to run offline demo mode without API calls
DEMO_MODE=true
```

> **Security Note:** API keys are stored exclusively in backend environment variables and are never transmitted to or accessible by the client browser.

---

## API Endpoints

### 1. Health & Config Status
- **`GET /api/health`**
  ```json
  {
    "status": "healthy",
    "llm_provider": "gemini",
    "llm_model": "gemini-1.5-flash",
    "demo_mode": true
  }
  ```

### 2. Upload Resume PDF
- **`POST /api/resume/upload`** (multipart/form-data: `file=@resume.pdf`)
  ```json
  {
    "resume_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "filename": "john_resume.pdf",
    "file_size_bytes": 1048576,
    "page_count": 2,
    "preview_text": "John Doe\nFull Stack Developer..."
  }
  ```

### 3. Extract & Normalize Skills
- **`POST /api/resume/{resume_id}/analyze`**
  ```json
  {
    "resume_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "filename": "john_resume.pdf",
    "total_skills": 12,
    "skills": [
      {
        "name": "Python",
        "category": "Programming Language",
        "confidence": 0.98,
        "evidence": "Developed backend microservices using Python and FastAPI",
        "is_explicit": true
      },
      {
        "name": "React",
        "category": "Frontend",
        "confidence": 0.95,
        "evidence": "Engineered single-page responsive dashboards in React",
        "is_explicit": true
      }
    ],
    "categories": {
      "Programming Language": ["Python", "JavaScript", "TypeScript"],
      "Frontend": ["React"]
    },
    "is_demo_mode": false
  }
  ```

### 4. Analyze Target Job Role
- **`POST /api/job/analyze`**
  ```json
  // Request
  { "job_role": "Full Stack Developer" }

  // Response
  {
    "job_role": "Full Stack Developer",
    "skills": [
      { "name": "React", "importance": "high", "relevance_reason": "Primary frontend UI framework." },
      { "name": "Node.js", "importance": "high", "relevance_reason": "Backend runtime for JavaScript services." },
      { "name": "PostgreSQL", "importance": "medium", "relevance_reason": "Standard relational database." }
    ]
  }
  ```

### 5. Calculate Skill Gap
- **`POST /api/skill-gap`**
  ```json
  // Request
  {
    "resume_skills": ["React", "Python", "SQL"],
    "job_skills": [
      { "name": "React", "importance": "high" },
      { "name": "Python", "importance": "high" },
      { "name": "SQL", "importance": "high" },
      { "name": "Docker", "importance": "high", "relevance_reason": "Container runtime for deployments." },
      { "name": "AWS", "importance": "high", "relevance_reason": "Cloud infrastructure platform." }
    ],
    "job_role": "Full Stack Developer"
  }

  // Response
  {
    "job_role": "Full Stack Developer",
    "total_target_skills": 5,
    "total_resume_skills": 3,
    "matched_skills": ["Python", "React", "SQL"],
    "missing_skills": ["Docker", "AWS"],
    "top_missing_skills": [
      {
        "name": "Docker",
        "importance": "high",
        "rank": 1,
        "relevance_reason": "Container runtime for deployments."
      },
      {
        "name": "AWS",
        "importance": "high",
        "rank": 2,
        "relevance_reason": "Cloud infrastructure platform."
      }
    ],
    "match_percentage": 60.0,
    "summary": "You match 3 of 5 expected skills (60.0%) for Full Stack Developer. Good foundational match..."
  }
  ```

---

## Running the Unit Tests

The backend includes a comprehensive pytest suite covering PDF extraction, normalization, deduplication, deterministic matching, and API endpoints:

```bash
# Run all tests
python -m pytest backend/tests -v
```

Output:
```
backend/tests/test_api_endpoints.py::test_api_health PASSED              [  7%]
backend/tests/test_api_endpoints.py::test_api_job_roles PASSED           [ 14%]
backend/tests/test_api_endpoints.py::test_api_full_flow_upload_and_analyze PASSED [ 21%]
backend/tests/test_api_endpoints.py::test_api_load_sample PASSED         [ 28%]
backend/tests/test_pdf_extractor.py::test_clean_extracted_text PASSED    [ 35%]
backend/tests/test_pdf_extractor.py::test_extract_text_from_valid_pdf PASSED [ 42%]
backend/tests/test_pdf_extractor.py::test_invalid_pdf_bytes_rejected PASSED [ 50%]
backend/tests/test_pdf_extractor.py::test_empty_or_too_short_pdf_rejected PASSED [ 57%]
backend/tests/test_skill_matcher.py::test_skill_matching_and_missing_skills PASSED [ 64%]
backend/tests/test_skill_matcher.py::test_top_3_missing_selection_and_importance_ranking PASSED [ 71%]
backend/tests/test_skill_matcher.py::test_case_insensitive_and_alias_matching PASSED [ 78%]
backend/tests/test_skill_normalization.py::test_skill_name_normalization_variations PASSED [ 85%]
backend/tests/test_skill_normalization.py::test_deduplicate_skills PASSED [ 90%]
backend/tests/test_skill_normalization.py::test_skill_categorization PASSED [100%]

======================== 14 passed in 2.94s ========================
```

---

## Limitations

- **Scanned / Image PDFs**: Resumes that consist purely of flattened image scans without embedded text layers require OCR (e.g. Tesseract), which is intentionally excluded to keep dependencies lightweight and fast. The app detects these and provides a clear error notification asking for a text-based PDF.
- **Single Page Preview**: Extracted preview text is limited to the first 400 characters in upload summaries to prevent payload bloat.
- **In-Memory Cache**: Uploaded resume text is cached in memory with a 1-hour expiration; enterprise production deployments would back this with Redis.

---

## Future Improvements

- [ ] Export PDF / Markdown gap analysis report card.
- [ ] Integration with LinkedIn / GitHub profiles for automatic skill sync.
- [ ] Personalized learning path recommendations with courses for top missing skills.
- [ ] Salary range and demand trend estimates for targeted roles.

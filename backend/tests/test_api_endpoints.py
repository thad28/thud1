import io
import fitz
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_sample_pdf_bytes() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    text = (
        "Jane Developer\n"
        "Full Stack Engineer\n"
        "Skills: React, JavaScript, TypeScript, Python, FastAPI, Docker, SQL\n"
        "Experience: Built scalable web applications with React and Python."
    )
    page.insert_text((50, 60), text)
    b = doc.tobytes()
    doc.close()
    return b

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "llm_provider" in data

def test_api_job_roles():
    res = client.get("/api/job/roles")
    assert res.status_code == 200
    assert "roles" in res.json()
    assert "Full Stack Developer" in res.json()["roles"]

def test_api_full_flow_upload_and_analyze():
    # 1. Upload valid PDF
    pdf_bytes = create_sample_pdf_bytes()
    upload_res = client.post(
        "/api/resume/upload",
        files={"file": ("jane_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    resume_id = upload_data["resume_id"]
    assert upload_data["filename"] == "jane_resume.pdf"
    assert upload_data["page_count"] == 1

    # 2. Analyze uploaded resume
    analyze_res = client.post(f"/api/resume/{resume_id}/analyze")
    assert analyze_res.status_code == 200
    analysis = analyze_res.json()
    assert analysis["total_skills"] >= 4
    skill_names = [s["name"] for s in analysis["skills"]]
    assert "React" in skill_names
    assert "Python" in skill_names

    # 3. Analyze target job role
    job_res = client.post("/api/job/analyze", json={"job_role": "Full Stack Developer"})
    assert job_res.status_code == 200
    job_data = job_res.json()
    assert len(job_data["skills"]) > 5

    # 4. Compare skill gap
    gap_res = client.post("/api/skill-gap", json={
        "resume_skills": skill_names,
        "job_skills": job_data["skills"],
        "job_role": "Full Stack Developer"
    })
    assert gap_res.status_code == 200
    gap_data = gap_res.json()
    assert "matched_skills" in gap_data
    assert "missing_skills" in gap_data
    assert len(gap_data["top_missing_skills"]) <= 3
    assert gap_data["match_percentage"] > 0

def test_api_load_sample():
    res = client.post("/api/demo/load-sample")
    assert res.status_code == 200
    data = res.json()
    assert data["resume_id"] == "demo-sample-alex-morgan"
    assert data["filename"] == "alex_morgan_fullstack_resume.pdf"

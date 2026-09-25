import pytest
from app.services.skill_matcher import compare_skills_gap
from app.models.schemas import JobSkill

def test_skill_matching_and_missing_skills():
    """
    Test scenario from specification:
    Resume: React, Python, SQL
    Target: React, Python, SQL, Docker, AWS
    Expected top missing: Docker, AWS
    """
    resume_skills = ["React", "Python", "SQL"]
    target_skills = [
        JobSkill(name="React", importance="high"),
        JobSkill(name="Python", importance="high"),
        JobSkill(name="SQL", importance="high"),
        JobSkill(name="Docker", importance="high", relevance_reason="Container runtime for reproducible apps."),
        JobSkill(name="AWS", importance="high", relevance_reason="Cloud platform for deployments.")
    ]

    result = compare_skills_gap(
        resume_skill_names=resume_skills,
        job_skills=target_skills,
        job_role="Software Engineer"
    )

    # Matched skills
    assert set(result.matched_skills) == {"Python", "React", "SQL"}
    # Missing skills
    assert set(result.missing_skills) == {"Docker", "AWS"}
    # Match percentage: 3/5 = 60.0%
    assert result.match_percentage == 60.0

    # Top missing names
    top_missing_names = [s.name for s in result.top_missing_skills]
    assert "Docker" in top_missing_names
    assert "AWS" in top_missing_names
    assert len(result.top_missing_skills) == 2

def test_top_3_missing_selection_and_importance_ranking():
    """
    Test that when more than 3 skills are missing, exactly top 3 are returned
    and prioritized by importance ('high' before 'medium' before 'low').
    """
    resume_skills = ["HTML", "CSS"]
    target_skills = [
        JobSkill(name="HTML", importance="high"),
        JobSkill(name="CSS", importance="high"),
        JobSkill(name="Jest", importance="low"),
        JobSkill(name="GraphQL", importance="medium"),
        JobSkill(name="TypeScript", importance="high"),
        JobSkill(name="React", importance="high"),
        JobSkill(name="Next.js", importance="medium"),
    ]

    result = compare_skills_gap(
        resume_skill_names=resume_skills,
        job_skills=target_skills,
        job_role="Frontend Developer"
    )

    assert len(result.top_missing_skills) == 3
    # Top 3 should be high-priority skills (TypeScript, React) followed by medium (GraphQL or Next.js)
    top_names = [s.name for s in result.top_missing_skills]
    assert "TypeScript" in top_names
    assert "React" in top_names
    # Jest (low importance) should NOT be in the top 3
    assert "Jest" not in top_names

    # Check rank order 1, 2, 3
    assert [s.rank for s in result.top_missing_skills] == [1, 2, 3]

def test_case_insensitive_and_alias_matching():
    """Test that resume alias 'reactjs' matches target 'React'."""
    resume_skills = ["reactjs", "postgres", "node"]
    target_skills = [
        JobSkill(name="React", importance="high"),
        JobSkill(name="PostgreSQL", importance="high"),
        JobSkill(name="Node.js", importance="high"),
        JobSkill(name="Docker", importance="medium")
    ]

    result = compare_skills_gap(
        resume_skill_names=resume_skills,
        job_skills=target_skills,
        job_role="Full Stack Developer"
    )

    assert set(result.matched_skills) == {"Node.js", "PostgreSQL", "React"}
    assert result.missing_skills == ["Docker"]
    assert result.match_percentage == 75.0

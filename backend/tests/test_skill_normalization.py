import pytest
from app.services.skill_matcher import (
    normalize_skill_name,
    deduplicate_skills,
    get_skill_category
)
from app.models.schemas import Skill

def test_skill_name_normalization_variations():
    """Tests that equivalent skill names are normalized to their canonical forms."""
    assert normalize_skill_name("JS") == "JavaScript"
    assert normalize_skill_name("javascript") == "JavaScript"
    assert normalize_skill_name("TS") == "TypeScript"
    assert normalize_skill_name("ReactJS") == "React"
    assert normalize_skill_name("react.js") == "React"
    assert normalize_skill_name("Postgres") == "PostgreSQL"
    assert normalize_skill_name("postgresql") == "PostgreSQL"
    assert normalize_skill_name("Node") == "Node.js"
    assert normalize_skill_name("nodejs") == "Node.js"
    assert normalize_skill_name("node.js") == "Node.js"
    assert normalize_skill_name("ML") == "Machine Learning"
    assert normalize_skill_name("AWS Cloud") == "AWS"
    assert normalize_skill_name("k8s") == "Kubernetes"
    assert normalize_skill_name("Golang") == "Go"

def test_deduplicate_skills():
    """
    Test that duplicates like 'ReactJS', 'React', 'JavaScript', 'JS'
    are collapsed into single canonical entries ('React', 'JavaScript').
    """
    input_skills = [
        Skill(name="ReactJS", category="Frontend", confidence=0.92, evidence="Used ReactJS"),
        Skill(name="React", category="Frontend", confidence=0.98, evidence="Expert in React"),
        Skill(name="JavaScript", category="Programming Language", confidence=0.95, evidence="JavaScript apps"),
        Skill(name="JS", category="Programming Language", confidence=0.85, evidence="JS scripts"),
    ]

    deduped = deduplicate_skills(input_skills)
    skill_names = {s.name for s in deduped}

    assert skill_names == {"React", "JavaScript"}
    assert len(deduped) == 2

    # Should retain the highest confidence
    react_skill = next(s for s in deduped if s.name == "React")
    assert react_skill.confidence == 0.98
    assert react_skill.evidence == "Expert in React"

def test_skill_categorization():
    """Test that canonical skills receive their appropriate category."""
    assert get_skill_category("Python") == "Programming Language"
    assert get_skill_category("React") == "Frontend"
    assert get_skill_category("FastAPI") == "Backend"
    assert get_skill_category("PostgreSQL") == "Database"
    assert get_skill_category("AWS") == "Cloud / DevOps"
    assert get_skill_category("Docker") == "Cloud / DevOps"

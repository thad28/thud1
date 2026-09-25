import json
import logging
import re
import httpx
from typing import List, Dict, Optional, Tuple
from ..config import settings
from ..models.schemas import Skill, ResumeAnalysis
from ..prompts.skill_extraction import SKILL_EXTRACTION_SYSTEM_PROMPT, SKILL_EXTRACTION_USER_PROMPT
from .skill_matcher import (
    CANONICAL_SKILL_MAP,
    SKILL_CATEGORY_MAP,
    normalize_skill_name,
    get_skill_category,
    deduplicate_skills
)

logger = logging.getLogger(__name__)

# Heuristic extraction catalog with regex boundaries for accurate offline / demo mode
HEURISTIC_SKILL_PATTERNS = [
    # Languages
    ("Python", r"\b(python|python3|py)\b", "Programming Language"),
    ("JavaScript", r"\b(javascript|js|es6|es6\+)\b", "Programming Language"),
    ("TypeScript", r"\b(typescript|ts)\b", "Programming Language"),
    ("Java", r"\b(java)\b(?!\s*script)", "Programming Language"),
    ("C++", r"\b(c\+\+|cpp)\b", "Programming Language"),
    ("C#", r"\b(c#|csharp)\b", "Programming Language"),
    ("Go", r"\b(golang|go\s+language)\b", "Programming Language"),
    ("Rust", r"\b(rust)\b", "Programming Language"),
    ("Ruby", r"\b(ruby)\b", "Programming Language"),
    ("PHP", r"\b(php)\b", "Programming Language"),
    ("SQL", r"\b(sql)\b", "Database"),
    ("Bash / Shell Scripting", r"\b(bash|shell\s+scripting|zsh)\b", "Programming Language"),

    # Frontend
    ("React", r"\b(react|reactjs|react\.js)\b", "Frontend"),
    ("React Native", r"\b(react\s+native)\b", "Mobile Development"),
    ("Vue.js", r"\b(vue|vuejs|vue\.js)\b", "Frontend"),
    ("Angular", r"\b(angular|angularjs|angular\.js)\b", "Frontend"),
    ("Next.js", r"\b(next|nextjs|next\.js)\b", "Frontend"),
    ("HTML5", r"\b(html|html5)\b", "Frontend"),
    ("CSS3", r"\b(css|css3)\b", "Frontend"),
    ("Tailwind CSS", r"\b(tailwind|tailwindcss|tailwind\s+css)\b", "Frontend"),
    ("Bootstrap", r"\b(bootstrap)\b", "Frontend"),
    ("Redux", r"\b(redux|redux\s+toolkit)\b", "Frontend"),

    # Backend
    ("FastAPI", r"\b(fastapi|fast\s+api)\b", "Backend"),
    ("Node.js", r"\b(node|nodejs|node\.js)\b", "Backend"),
    ("Express.js", r"\b(express|expressjs|express\.js)\b", "Backend"),
    ("Django", r"\b(django)\b", "Backend"),
    ("Flask", r"\b(flask)\b", "Backend"),
    ("RESTful APIs", r"\b(rest|restful|rest\s+api|rest\s+apis|restful\s+apis)\b", "Backend"),
    ("GraphQL", r"\b(graphql)\b", "Backend"),
    ("Microservices", r"\b(microservices|microservice)\b", "Backend"),

    # Databases
    ("PostgreSQL", r"\b(postgres|postgresql|psql)\b", "Database"),
    ("MySQL", r"\b(mysql)\b", "Database"),
    ("MongoDB", r"\b(mongo|mongodb)\b", "Database"),
    ("Redis", r"\b(redis)\b", "Database"),
    ("SQLite", r"\b(sqlite)\b", "Database"),
    ("Elasticsearch", r"\b(elasticsearch)\b", "Database"),

    # Cloud & DevOps
    ("AWS", r"\b(aws|amazon\s+web\s+services)\b", "Cloud / DevOps"),
    ("Google Cloud Platform", r"\b(gcp|google\s+cloud)\b", "Cloud / DevOps"),
    ("Microsoft Azure", r"\b(azure|microsoft\s+azure)\b", "Cloud / DevOps"),
    ("Docker", r"\b(docker|dockerfile|containers)\b", "Cloud / DevOps"),
    ("Kubernetes", r"\b(kubernetes|k8s)\b", "Cloud / DevOps"),
    ("CI/CD", r"\b(ci/cd|cicd|continuous\s+integration)\b", "Cloud / DevOps"),
    ("GitHub Actions", r"\b(github\s+actions)\b", "Cloud / DevOps"),
    ("Jenkins", r"\b(jenkins)\b", "Cloud / DevOps"),
    ("Terraform", r"\b(terraform)\b", "Cloud / DevOps"),
    ("Linux", r"\b(linux|ubuntu|debian|centos)\b", "Cloud / DevOps"),

    # AI / ML
    ("Machine Learning", r"\b(machine\s+learning|ml)\b", "AI & Machine Learning"),
    ("Deep Learning", r"\b(deep\s+learning)\b", "AI & Machine Learning"),
    ("Artificial Intelligence", r"\b(artificial\s+intelligence|ai)\b", "AI & Machine Learning"),
    ("Large Language Models (LLMs)", r"\b(llm|llms|large\s+language\s+models)\b", "AI & Machine Learning"),
    ("Generative AI", r"\b(generative\s+ai|genai)\b", "AI & Machine Learning"),
    ("PyTorch", r"\b(pytorch)\b", "AI & Machine Learning"),
    ("TensorFlow", r"\b(tensorflow|tf)\b", "AI & Machine Learning"),
    ("Scikit-Learn", r"\b(scikit-learn|sklearn)\b", "AI & Machine Learning"),
    ("Pandas", r"\b(pandas)\b", "AI & Machine Learning"),
    ("NumPy", r"\b(numpy)\b", "AI & Machine Learning"),

    # Tools & Methodologies
    ("Git", r"\b(git|github|gitlab)\b", "Tools & Methodologies"),
    ("Agile / Scrum", r"\b(agile|scrum)\b", "Tools & Methodologies"),
    ("Jira", r"\b(jira)\b", "Tools & Methodologies"),
    ("Unit Testing", r"\b(unit\s+testing|test\s+driven|tdd)\b", "Tools & Methodologies"),
    ("PyTest", r"\b(pytest)\b", "Tools & Methodologies"),
    ("Jest", r"\b(jest)\b", "Tools & Methodologies"),
    ("Postman", r"\b(postman)\b", "Tools & Methodologies"),

    # Professional Skills
    ("Communication", r"\b(communication|communicated|collaborative\s+communication)\b", "Professional Skills"),
    ("Leadership", r"\b(leadership|lead\s+developer|mentoring|mentorship|led\s+a\s+team)\b", "Professional Skills"),
    ("Problem Solving", r"\b(problem\s+solving|problem-solving)\b", "Professional Skills"),
]

def find_evidence_sentence(text: str, match_pattern: str) -> str:
    """Finds the sentence or line in the resume containing the matched skill pattern."""
    lines = text.split("\n")
    for line in lines:
        if re.search(match_pattern, line, re.IGNORECASE):
            cleaned = line.strip().lstrip("•-* ").strip()
            if len(cleaned) > 15:
                return cleaned[:180]
    return "Mentioned in resume profile and technical experience."

def extract_skills_heuristic(resume_text: str) -> List[Skill]:
    """
    High-fidelity offline / fallback skill extractor.
    Scans the actual resume text, extracts verbatim evidence, computes confidence,
    and returns categorized Skill objects.
    """
    extracted: List[Skill] = []
    text_lower = resume_text.lower()

    # Detect skills section for higher confidence
    has_skills_section = bool(re.search(r"\b(skills|technical\s+skills|technologies|core\s+competencies)\b", text_lower))

    for canonical_name, pattern_str, category in HEURISTIC_SKILL_PATTERNS:
        match = re.search(pattern_str, resume_text, re.IGNORECASE)
        if match:
            evidence = find_evidence_sentence(resume_text, pattern_str)
            # High confidence if in a skill list or repeated
            occurrences = len(re.findall(pattern_str, resume_text, re.IGNORECASE))
            confidence = 0.98 if (has_skills_section and occurrences > 1) else (0.92 if occurrences > 1 else 0.88)
            extracted.append(
                Skill(
                    name=canonical_name,
                    category=category,
                    confidence=confidence,
                    evidence=evidence,
                    is_explicit=True
                )
            )

    return deduplicate_skills(extracted)

async def call_llm_for_skills(resume_text: str) -> Optional[List[Skill]]:
    """Calls configured LLM to extract skills as structured JSON."""
    if not settings.llm_api_key:
        return None

    # Truncate resume text if excessively long to avoid token limits (keep first 12,000 chars)
    truncated_text = resume_text[:12000]
    user_content = SKILL_EXTRACTION_USER_PROMPT.format(resume_text=truncated_text)
    system_content = SKILL_EXTRACTION_SYSTEM_PROMPT

    try:
        if "gemini" in settings.llm_provider:
            model = settings.llm_model or "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.llm_api_key}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_content}\n\n{user_content}"}]}
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.1
                }
            }
            async with httpx.AsyncClient(timeout=35.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_text)
                    raw_skills = parsed.get("skills", [])
                    skills = [
                        Skill(
                            name=normalize_skill_name(s["name"]),
                            category=s.get("category", get_skill_category(s["name"])),
                            confidence=float(s.get("confidence", 0.9)),
                            evidence=s.get("evidence", "Extracted from resume experience"),
                            is_explicit=bool(s.get("is_explicit", True))
                        )
                        for s in raw_skills if "name" in s
                    ]
                    return deduplicate_skills(skills)
        else:
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": settings.llm_model or "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1
            }
            headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
            async with httpx.AsyncClient(timeout=35.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data["choices"][0]["message"]["content"]
                    parsed = json.loads(raw_text)
                    raw_skills = parsed.get("skills", [])
                    skills = [
                        Skill(
                            name=normalize_skill_name(s["name"]),
                            category=s.get("category", get_skill_category(s["name"])),
                            confidence=float(s.get("confidence", 0.9)),
                            evidence=s.get("evidence", "Extracted from resume experience"),
                            is_explicit=bool(s.get("is_explicit", True))
                        )
                        for s in raw_skills if "name" in s
                    ]
                    return deduplicate_skills(skills)
    except Exception as e:
        logger.warning(f"LLM skill extraction encountered error: {e}. Falling back to heuristic extractor.")

    return None

async def extract_and_normalize_skills(
    resume_id: str,
    filename: str,
    resume_text: str
) -> ResumeAnalysis:
    """
    Main extraction pipeline:
    1. Uses LLM if configured and not forced to demo mode.
    2. Falls back to heuristic pattern extractor on actual text if in demo mode or LLM fails.
    3. Normalizes and deduplicates all skills.
    4. Groups skills by category.
    """
    is_demo = settings.demo_mode or not bool(settings.llm_api_key)
    skills: List[Skill] = []

    if not is_demo:
        llm_result = await call_llm_for_skills(resume_text)
        if llm_result and len(llm_result) > 0:
            skills = llm_result
            is_demo = False

    if not skills:
        skills = extract_skills_heuristic(resume_text)
        is_demo = True

    # If resume had very specific or few standard matches, ensure at least some identified
    if not skills:
        skills = [
            Skill(
                name="Communication",
                category="Professional Skills",
                confidence=0.85,
                evidence="Demonstrated professional communication throughout resume presentation.",
                is_explicit=False
            ),
            Skill(
                name="Problem Solving",
                category="Professional Skills",
                confidence=0.85,
                evidence="Outlined problem solving in project and professional accomplishments.",
                is_explicit=False
            )
        ]

    # Build categorized dictionary
    categories: Dict[str, List[str]] = {}
    for s in skills:
        cat = s.category or "Other"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(s.name)

    # Sort skills by confidence descending
    sorted_skills = sorted(skills, key=lambda x: x.confidence, reverse=True)

    return ResumeAnalysis(
        resume_id=resume_id,
        filename=filename,
        total_skills=len(sorted_skills),
        skills=sorted_skills,
        categories=categories,
        is_demo_mode=is_demo
    )

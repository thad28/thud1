import re
from typing import List, Dict, Tuple, Optional
from ..models.schemas import JobSkill, MissingSkillDetail, SkillGapResult, Skill

# Comprehensive canonical normalization dictionary
CANONICAL_SKILL_MAP: Dict[str, str] = {
    # JavaScript / TypeScript Ecosystem
    "js": "JavaScript",
    "javascript": "JavaScript",
    "es6": "JavaScript",
    "es6+": "JavaScript",
    "vanilla js": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react native": "React Native",
    "reactnative": "React Native",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "angular.js": "Angular",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nuxt": "Nuxt.js",
    "nuxtjs": "Nuxt.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "nest": "NestJS",
    "nestjs": "NestJS",
    "redux": "Redux",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "html": "HTML",
    "html5": "HTML5",
    "css": "CSS",
    "css3": "CSS3",
    "sass": "Sass",
    "scss": "Sass",

    # Python & Backend Ecosystem
    "python": "Python",
    "py": "Python",
    "python3": "Python",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "rest api": "RESTful APIs",
    "rest apis": "RESTful APIs",
    "restful api": "RESTful APIs",
    "restful apis": "RESTful APIs",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "microservices": "Microservices",

    # Languages
    "golang": "Go",
    "go": "Go",
    "java": "Java",
    "c#": "C#",
    "csharp": "C#",
    "c++": "C++",
    "cpp": "C++",
    "c": "C",
    "rust": "Rust",
    "ruby": "Ruby",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    "php": "PHP",
    "kotlin": "Kotlin",
    "swift": "Swift",

    # Databases & Caching
    "sql": "SQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "dynamodb": "DynamoDB",
    "cassandra": "Apache Cassandra",
    "neo4j": "Neo4j",
    "prisma": "Prisma",
    "sqlalchemy": "SQLAlchemy",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "aws cloud": "AWS",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "docker": "Docker",
    "docker container": "Docker",
    "docker containers": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "github actions": "GitHub Actions",
    "jenkins": "Jenkins",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "linux": "Linux",
    "bash": "Bash / Shell Scripting",
    "shell": "Bash / Shell Scripting",
    "nginx": "Nginx",

    # AI / ML / Data
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "llm": "Large Language Models (LLMs)",
    "llms": "Large Language Models (LLMs)",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn",
    "scikitlearn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "langchain": "LangChain",
    "huggingface": "Hugging Face",
    "opencv": "OpenCV",
    "data analysis": "Data Analysis",
    "data visualization": "Data Visualization",

    # Tools, Testing, Practices
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "jira": "Jira",
    "agile": "Agile / Scrum",
    "scrum": "Agile / Scrum",
    "unit testing": "Unit Testing",
    "pytest": "PyTest",
    "jest": "Jest",
    "cypress": "Cypress",
    "postman": "Postman",

    # Soft Skills & Leadership
    "communication": "Communication",
    "leadership": "Leadership",
    "teamwork": "Teamwork & Collaboration",
    "collaboration": "Teamwork & Collaboration",
    "problem solving": "Problem Solving",
    "problem-solving": "Problem Solving",
    "critical thinking": "Critical Thinking",
    "mentorship": "Mentorship",
    "project management": "Project Management",
    "time management": "Time Management",
}

# Skill category heuristics
SKILL_CATEGORY_MAP: Dict[str, str] = {
    # Programming
    "Python": "Programming Language",
    "JavaScript": "Programming Language",
    "TypeScript": "Programming Language",
    "Java": "Programming Language",
    "C#": "Programming Language",
    "C++": "Programming Language",
    "Go": "Programming Language",
    "Rust": "Programming Language",
    "Ruby": "Programming Language",
    "PHP": "Programming Language",
    "Kotlin": "Programming Language",
    "Swift": "Programming Language",
    "SQL": "Database",
    "Bash / Shell Scripting": "Programming Language",

    # Frontend
    "React": "Frontend",
    "React Native": "Mobile Development",
    "Vue.js": "Frontend",
    "Angular": "Frontend",
    "Next.js": "Frontend",
    "Nuxt.js": "Frontend",
    "HTML": "Frontend",
    "HTML5": "Frontend",
    "CSS": "Frontend",
    "CSS3": "Frontend",
    "Tailwind CSS": "Frontend",
    "Bootstrap": "Frontend",
    "Sass": "Frontend",
    "Redux": "Frontend",

    # Backend
    "FastAPI": "Backend",
    "Django": "Backend",
    "Flask": "Backend",
    "Node.js": "Backend",
    "Express.js": "Backend",
    "NestJS": "Backend",
    "Ruby on Rails": "Backend",
    "RESTful APIs": "Backend",
    "GraphQL": "Backend",
    "gRPC": "Backend",
    "Microservices": "Backend",

    # Database
    "PostgreSQL": "Database",
    "MySQL": "Database",
    "MongoDB": "Database",
    "Redis": "Database",
    "SQLite": "Database",
    "Elasticsearch": "Database",
    "DynamoDB": "Database",
    "Apache Cassandra": "Database",
    "Prisma": "Database",
    "SQLAlchemy": "Database",

    # Cloud & DevOps
    "AWS": "Cloud / DevOps",
    "Google Cloud Platform": "Cloud / DevOps",
    "Microsoft Azure": "Cloud / DevOps",
    "Docker": "Cloud / DevOps",
    "Kubernetes": "Cloud / DevOps",
    "CI/CD": "Cloud / DevOps",
    "GitHub Actions": "Cloud / DevOps",
    "Jenkins": "Cloud / DevOps",
    "Terraform": "Cloud / DevOps",
    "Ansible": "Cloud / DevOps",
    "Linux": "Cloud / DevOps",
    "Nginx": "Cloud / DevOps",

    # AI / ML
    "Machine Learning": "AI & Machine Learning",
    "Deep Learning": "AI & Machine Learning",
    "Artificial Intelligence": "AI & Machine Learning",
    "Natural Language Processing": "AI & Machine Learning",
    "Large Language Models (LLMs)": "AI & Machine Learning",
    "Generative AI": "AI & Machine Learning",
    "Pandas": "AI & Machine Learning",
    "NumPy": "AI & Machine Learning",
    "Scikit-Learn": "AI & Machine Learning",
    "PyTorch": "AI & Machine Learning",
    "TensorFlow": "AI & Machine Learning",
    "Keras": "AI & Machine Learning",
    "LangChain": "AI & Machine Learning",
    "Hugging Face": "AI & Machine Learning",
    "OpenCV": "AI & Machine Learning",
    "Data Analysis": "AI & Machine Learning",
    "Data Visualization": "AI & Machine Learning",

    # Tools
    "Git": "Tools & Methodologies",
    "GitHub": "Tools & Methodologies",
    "GitLab": "Tools & Methodologies",
    "Jira": "Tools & Methodologies",
    "Agile / Scrum": "Tools & Methodologies",
    "Unit Testing": "Tools & Methodologies",
    "PyTest": "Tools & Methodologies",
    "Jest": "Tools & Methodologies",
    "Cypress": "Tools & Methodologies",
    "Postman": "Tools & Methodologies",

    # Soft Skills
    "Communication": "Professional Skills",
    "Leadership": "Professional Skills",
    "Teamwork & Collaboration": "Professional Skills",
    "Problem Solving": "Professional Skills",
    "Critical Thinking": "Professional Skills",
    "Mentorship": "Professional Skills",
    "Project Management": "Professional Skills",
    "Time Management": "Professional Skills",
}

DEFAULT_RELEVANCE_REASONS: Dict[str, str] = {
    "Node.js": "Primary backend runtime commonly used for JavaScript/TypeScript full-stack microservices and API servers.",
    "PostgreSQL": "Industry-standard relational database technology commonly required for robust, transactional web and enterprise applications.",
    "AWS": "Dominant cloud infrastructure platform essential for deploying, scaling, and managing cloud-native services.",
    "Docker": "Essential containerization technology required for reproducible developer environments and cloud deployments.",
    "Kubernetes": "Standard container orchestration platform widely used in modern microservice production architectures.",
    "TypeScript": "Strongly typed superset of JavaScript widely required across enterprise teams for code quality and maintainability.",
    "React": "Most popular modern frontend library for building reactive, component-driven user interfaces.",
    "FastAPI": "High-performance Python web framework ideal for building modern asynchronous REST APIs and AI microservices.",
    "Python": "Versatile programming language widely adopted for backend engineering, data science, automation, and AI workflows.",
    "Redis": "In-memory key-value data store critical for low-latency caching, session management, and rate limiting.",
    "CI/CD": "Automation pipeline practice critical for safe, rapid, and reproducible software testing and deployments.",
    "Machine Learning": "Core competency for predictive modeling, automated decision-making, and intelligent feature engineering.",
    "Git": "Universal version control system necessary for collaborative source code management and agile workflows.",
    "RESTful APIs": "Standard architectural style for designing interoperable, networked services and web applications.",
    "GraphQL": "Flexible query language allowing frontends to request precisely the data needed, reducing over-fetching.",
    "SQL": "Fundamental data querying language indispensable for data extraction, manipulation, and database administration."
}

def normalize_skill_name(skill_name: str) -> str:
    """
    Normalizes a skill name into its canonical industry standard.
    Handles punctuation variations, casing, and common abbreviations.
    Example: 'ReactJS' -> 'React', 'js' -> 'JavaScript', 'k8s' -> 'Kubernetes'
    """
    if not skill_name:
        return ""

    raw = skill_name.strip()
    lowered = raw.lower()

    # Direct match in canonical dictionary
    if lowered in CANONICAL_SKILL_MAP:
        return CANONICAL_SKILL_MAP[lowered]

    # Clean punctuation and check again (e.g. "react.js" -> "react js")
    cleaned_variant = re.sub(r"[._\-]", " ", lowered).strip()
    cleaned_variant = re.sub(r"\s+", " ", cleaned_variant)
    if cleaned_variant in CANONICAL_SKILL_MAP:
        return CANONICAL_SKILL_MAP[cleaned_variant]

    # Clean without spaces (e.g. "reactjs" -> "react")
    no_space_variant = re.sub(r"[\s._\-]", "", lowered)
    if no_space_variant in CANONICAL_SKILL_MAP:
        return CANONICAL_SKILL_MAP[no_space_variant]

    # Preserve well-known title casing if not in map
    return raw.title()

def get_skill_category(skill_name: str) -> str:
    """Returns the broad category for a skill."""
    norm = normalize_skill_name(skill_name)
    return SKILL_CATEGORY_MAP.get(norm, "Other Technical Skills")

def deduplicate_skills(skills: List[Skill]) -> List[Skill]:
    """
    Normalizes and deduplicates a list of Skill objects.
    If multiple variations exist (e.g. 'React' and 'ReactJS'), keeps the one with the highest confidence
    and merges/preserves evidence.
    """
    seen: Dict[str, Skill] = {}

    for s in skills:
        norm_name = normalize_skill_name(s.name)
        if not norm_name:
            continue

        category = s.category if s.category and s.category != "General" else get_skill_category(norm_name)
        normalized_skill = Skill(
            name=norm_name,
            category=category,
            confidence=round(s.confidence, 2),
            evidence=s.evidence.strip(),
            is_explicit=s.is_explicit
        )

        if norm_name not in seen:
            seen[norm_name] = normalized_skill
        else:
            existing = seen[norm_name]
            # Keep higher confidence or longer evidence
            if normalized_skill.confidence > existing.confidence:
                seen[norm_name] = normalized_skill
            elif len(normalized_skill.evidence) > len(existing.evidence):
                seen[norm_name].evidence = normalized_skill.evidence

    return sorted(list(seen.values()), key=lambda x: (x.category, x.name))

def compare_skills_gap(
    resume_skill_names: List[str],
    job_skills: List[JobSkill],
    job_role: str = "Target Job Role"
) -> SkillGapResult:
    """
    Performs deterministic skill gap analysis:
    1. Normalizes all resume skill names and creates a lookup set.
    2. Normalizes job skill names.
    3. Computes intersection (matched skills) and set difference (missing skills).
    4. Selects exactly top 3 missing skills based on importance and relevance rationale.
    5. Calculates match percentage and generates an objective summary.
    """
    # 1. Normalize resume skills into a case-insensitive set
    resume_norm_set = set()
    for name in resume_skill_names:
        norm = normalize_skill_name(name)
        if norm:
            resume_norm_set.add(norm.lower())

    matched_skills_map: Dict[str, str] = {}
    missing_job_skills: List[JobSkill] = []

    # 2. Iterate through target job skills
    seen_target_names = set()
    deduped_target_skills: List[JobSkill] = []

    for js in job_skills:
        norm_name = normalize_skill_name(js.name)
        if not norm_name or norm_name.lower() in seen_target_names:
            continue
        seen_target_names.add(norm_name.lower())

        target_skill = JobSkill(
            name=norm_name,
            importance=js.importance.lower() if js.importance else "medium",
            category=js.category or get_skill_category(norm_name),
            relevance_reason=js.relevance_reason or DEFAULT_RELEVANCE_REASONS.get(
                norm_name,
                f"Commonly expected technical capability for {job_role} responsibilities."
            )
        )
        deduped_target_skills.append(target_skill)

        if norm_name.lower() in resume_norm_set:
            matched_skills_map[norm_name.lower()] = norm_name
        else:
            missing_job_skills.append(target_skill)

    matched_list = sorted(list(matched_skills_map.values()))
    missing_list = [s.name for s in missing_job_skills]

    # 3. Sort missing skills by importance priority: high > medium > low
    importance_weight = {"high": 3, "medium": 2, "low": 1}
    sorted_missing = sorted(
        missing_job_skills,
        key=lambda x: importance_weight.get(x.importance, 1),
        reverse=True
    )

    # 4. Extract exactly top 3 missing skills
    top_3_raw = sorted_missing[:3]
    top_3_details: List[MissingSkillDetail] = []
    for idx, s in enumerate(top_3_raw, start=1):
        reason = s.relevance_reason or DEFAULT_RELEVANCE_REASONS.get(
            s.name,
            f"Frequently utilized in modern {job_role} stacks to build maintainable, scalable solutions."
        )
        top_3_details.append(
            MissingSkillDetail(
                name=s.name,
                importance=s.importance,
                rank=idx,
                relevance_reason=reason,
                category=s.category
            )
        )

    # 5. Compute match score
    total_target = len(deduped_target_skills)
    match_percentage = round((len(matched_list) / total_target * 100), 1) if total_target > 0 else 0.0

    # 6. Concise objective summary
    if match_percentage >= 80:
        summary_tone = "Strong candidate alignment with high overlap in core requirements."
    elif match_percentage >= 50:
        summary_tone = "Good foundational match with a few key tech stack additions needed."
    else:
        summary_tone = "Moderate overlap; focused upskilling in the top missing skills will significantly strengthen candidacy."

    summary = (
        f"You match {len(matched_list)} of {total_target} expected skills ({match_percentage}%) for {job_role}. {summary_tone}"
    )

    return SkillGapResult(
        job_role=job_role,
        total_target_skills=total_target,
        total_resume_skills=len(resume_norm_set),
        matched_skills=matched_list,
        missing_skills=missing_list,
        top_missing_skills=top_3_details,
        match_percentage=match_percentage,
        summary=summary
    )

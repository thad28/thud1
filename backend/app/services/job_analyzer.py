import json
import logging
import httpx
from typing import List, Dict, Optional
from ..config import settings
from ..models.schemas import JobSkill, JobRoleAnalysis
from ..prompts.job_analysis import JOB_ANALYSIS_SYSTEM_PROMPT, JOB_ANALYSIS_USER_PROMPT
from .skill_matcher import normalize_skill_name, get_skill_category

logger = logging.getLogger(__name__)

# Standard industry benchmarks for well-known roles
JOB_ROLE_CATALOG: Dict[str, List[Dict[str, str]]] = {
    "Full Stack Developer": [
        {"name": "JavaScript", "importance": "high", "relevance_reason": "Core language powering both client-side and server-side runtimes."},
        {"name": "TypeScript", "importance": "high", "relevance_reason": "Ensures type safety and maintainability in large full-stack codebases."},
        {"name": "React", "importance": "high", "relevance_reason": "Dominant modern component library for dynamic user interfaces."},
        {"name": "Node.js", "importance": "high", "relevance_reason": "High-performance JavaScript runtime for backend services and APIs."},
        {"name": "PostgreSQL", "importance": "medium", "relevance_reason": "Standard robust relational database for persistent business data."},
        {"name": "RESTful APIs", "importance": "high", "relevance_reason": "Standard architecture for connecting client interfaces with backend microservices."},
        {"name": "Docker", "importance": "medium", "relevance_reason": "Ensures consistent environments across development and production deployments."},
        {"name": "AWS", "importance": "medium", "relevance_reason": "Industry standard cloud provider for hosting web apps and managed databases."},
        {"name": "Git", "importance": "high", "relevance_reason": "Essential for collaborative version control and team development workflows."},
        {"name": "CI/CD", "importance": "medium", "relevance_reason": "Automates automated testing, continuous integration, and seamless deployments."},
        {"name": "Tailwind CSS", "importance": "medium", "relevance_reason": "Modern utility-first CSS framework for rapid and responsive UI development."},
        {"name": "GraphQL", "importance": "low", "relevance_reason": "Flexible API query language that eliminates frontend over-fetching."}
    ],
    "Backend Developer": [
        {"name": "Python", "importance": "high", "relevance_reason": "Widely used backend language with rich frameworks and automation tools."},
        {"name": "FastAPI", "importance": "high", "relevance_reason": "Modern, high-performance web framework for building asynchronous Python APIs."},
        {"name": "PostgreSQL", "importance": "high", "relevance_reason": "Primary relational database for ACID transactions and complex schemas."},
        {"name": "Docker", "importance": "high", "relevance_reason": "Standard containerization for microservices and cloud deployment."},
        {"name": "Redis", "importance": "high", "relevance_reason": "Essential for caching, distributed locking, and fast session management."},
        {"name": "RESTful APIs", "importance": "high", "relevance_reason": "Core architectural pattern for microservices and third-party integrations."},
        {"name": "AWS", "importance": "medium", "relevance_reason": "Cloud infrastructure for deploying serverless functions and compute instances."},
        {"name": "CI/CD", "importance": "medium", "relevance_reason": "Enables automated testing and reliable zero-downtime releases."},
        {"name": "Git", "importance": "high", "relevance_reason": "Standard version control system for distributed engineering teams."},
        {"name": "Unit Testing", "importance": "medium", "relevance_reason": "Guarantees backend logic reliability, edge-case coverage, and regression prevention."}
    ],
    "Frontend Developer": [
        {"name": "JavaScript", "importance": "high", "relevance_reason": "Fundamental scripting language of modern browsers and client applications."},
        {"name": "TypeScript", "importance": "high", "relevance_reason": "Standard for frontend scalability, preventing runtime bugs and enhancing DX."},
        {"name": "React", "importance": "high", "relevance_reason": "Industry standard component-driven library for single-page web applications."},
        {"name": "HTML5", "importance": "high", "relevance_reason": "Semantic building blocks of accessible, SEO-friendly web documents."},
        {"name": "CSS3", "importance": "high", "relevance_reason": "Styling, flexbox/grid layouts, animations, and media queries for responsive web."},
        {"name": "Tailwind CSS", "importance": "high", "relevance_reason": "Utility-first framework accelerating responsive, modern UI implementation."},
        {"name": "Redux", "importance": "medium", "relevance_reason": "Predictable state container for managing complex application-wide state."},
        {"name": "Git", "importance": "high", "relevance_reason": "Version control for multi-developer UI collaboration and branch management."},
        {"name": "RESTful APIs", "importance": "medium", "relevance_reason": "Consuming backend endpoints and handling asynchronous data states."},
        {"name": "Jest", "importance": "medium", "relevance_reason": "Frontend unit and component snapshot testing framework."}
    ],
    "Data Scientist": [
        {"name": "Python", "importance": "high", "relevance_reason": "Premier language for statistical analysis, modeling, and data pipelines."},
        {"name": "SQL", "importance": "high", "relevance_reason": "Querying and extracting structured data from enterprise warehouses."},
        {"name": "Pandas", "importance": "high", "relevance_reason": "Core library for data cleaning, transformation, and exploratory analysis."},
        {"name": "NumPy", "importance": "high", "relevance_reason": "High-performance vectorized mathematical operations and matrix processing."},
        {"name": "Scikit-Learn", "importance": "high", "relevance_reason": "Standard framework for supervised and unsupervised classical machine learning."},
        {"name": "Machine Learning", "importance": "high", "relevance_reason": "Theoretical and applied knowledge of classification, regression, and clustering."},
        {"name": "Data Visualization", "importance": "medium", "relevance_reason": "Communicating insights effectively to business stakeholders with visual dashboards."},
        {"name": "Git", "importance": "medium", "relevance_reason": "Tracking code, model scripts, and collaborative experimentation."},
        {"name": "Communication", "importance": "high", "relevance_reason": "Translating technical modeling results into actionable executive business value."}
    ],
    "Machine Learning Engineer": [
        {"name": "Python", "importance": "high", "relevance_reason": "Standard language for building ML architectures, data pipelines, and APIs."},
        {"name": "PyTorch", "importance": "high", "relevance_reason": "Leading deep learning framework for research and scalable production deployment."},
        {"name": "TensorFlow", "importance": "medium", "relevance_reason": "Widely deployed enterprise ML library for training and edge deployment."},
        {"name": "Machine Learning", "importance": "high", "relevance_reason": "Foundational understanding of loss functions, optimization, and evaluation metrics."},
        {"name": "Deep Learning", "importance": "high", "relevance_reason": "Neural network architectures (CNNs, RNNs, Transformers) for complex tasks."},
        {"name": "Docker", "importance": "high", "relevance_reason": "Packaging model runtimes, CUDA dependencies, and inference microservices."},
        {"name": "Large Language Models (LLMs)", "importance": "high", "relevance_reason": "Fine-tuning, prompt engineering, and deploying generative AI pipelines."},
        {"name": "Git", "importance": "high", "relevance_reason": "Version control for reproducible ML pipelines and source code."},
        {"name": "AWS", "importance": "medium", "relevance_reason": "Cloud GPU provisioning, model serving endpoints, and S3 data storage."}
    ],
    "DevOps Engineer": [
        {"name": "Docker", "importance": "high", "relevance_reason": "Standard container runtime for portable, reproducible application artifacts."},
        {"name": "Kubernetes", "importance": "high", "relevance_reason": "Dominant orchestration engine for automated scaling, self-healing, and deployments."},
        {"name": "CI/CD", "importance": "high", "relevance_reason": "Designing robust pipelines that automate build, test, and production release flows."},
        {"name": "Linux", "importance": "high", "relevance_reason": "Core operating system foundation for server infrastructure and containers."},
        {"name": "Terraform", "importance": "high", "relevance_reason": "Infrastructure as Code (IaC) tool for declaratively managing cloud resources."},
        {"name": "AWS", "importance": "high", "relevance_reason": "Cloud platform services (EC2, EKS, IAM, VPC, S3) powering infrastructure."},
        {"name": "Bash / Shell Scripting", "importance": "high", "relevance_reason": "Server automation, routine maintenance, and system configuration scripts."},
        {"name": "GitHub Actions", "importance": "medium", "relevance_reason": "Modern workflow automation integrated directly with repository events."},
        {"name": "Git", "importance": "high", "relevance_reason": "GitOps practices where infrastructure state is tracked declaratively in git."}
    ],
    "Cloud Engineer": [
        {"name": "AWS", "importance": "high", "relevance_reason": "Comprehensive cloud platform for enterprise compute, storage, and networking."},
        {"name": "Terraform", "importance": "high", "relevance_reason": "Multi-cloud Infrastructure as Code for reliable resource provisioning."},
        {"name": "Docker", "importance": "high", "relevance_reason": "Creating containerized microservices ready for cloud cluster hosting."},
        {"name": "Kubernetes", "importance": "medium", "relevance_reason": "Deploying and managing containerized workloads at scale."},
        {"name": "Linux", "importance": "high", "relevance_reason": "Underlying server OS for virtual machines and container host nodes."},
        {"name": "Python", "importance": "medium", "relevance_reason": "Scripting cloud automation, Lambda functions, and infrastructure tools."},
        {"name": "CI/CD", "importance": "medium", "relevance_reason": "Continuous delivery of infrastructure updates and application deployments."}
    ],
    "Software Engineer": [
        {"name": "Python", "importance": "high", "relevance_reason": "Versatile programming language used across backend services, tools, and testing."},
        {"name": "JavaScript", "importance": "high", "relevance_reason": "Ubiquitous web language for building interactive applications."},
        {"name": "Git", "importance": "high", "relevance_reason": "Industry standard distributed version control system."},
        {"name": "SQL", "importance": "high", "relevance_reason": "Relational data querying and database schema interactions."},
        {"name": "RESTful APIs", "importance": "high", "relevance_reason": "Designing and integrating decoupled networked services."},
        {"name": "Docker", "importance": "medium", "relevance_reason": "Packaging software for isolated and reliable execution across environments."},
        {"name": "Unit Testing", "importance": "medium", "relevance_reason": "Writing automated test suites to ensure system correctness and quality."},
        {"name": "Problem Solving", "importance": "high", "relevance_reason": "Analytical thinking required for designing algorithms and troubleshooting bugs."}
    ]
}

async def call_llm_for_job_analysis(job_role: str) -> Optional[List[JobSkill]]:
    """Calls configured LLM to generate industry skills for an arbitrary job role."""
    if not settings.llm_api_key:
        return None

    user_content = JOB_ANALYSIS_USER_PROMPT.format(job_role=job_role)
    system_content = JOB_ANALYSIS_SYSTEM_PROMPT

    try:
        # Check LLM provider
        if "gemini" in settings.llm_provider:
            # Gemini REST API
            model = settings.llm_model or "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.llm_api_key}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_content}\n\n{user_content}"}]}
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2
                }
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_text)
                    skills_list = parsed.get("skills", [])
                    return [
                        JobSkill(
                            name=normalize_skill_name(s["name"]),
                            importance=s.get("importance", "medium"),
                            category=s.get("category", get_skill_category(s["name"])),
                            relevance_reason=s.get("relevance_reason", "")
                        )
                        for s in skills_list if "name" in s
                    ]
        else:
            # OpenAI compatible endpoint
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": settings.llm_model or "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data["choices"][0]["message"]["content"]
                    parsed = json.loads(raw_text)
                    skills_list = parsed.get("skills", [])
                    return [
                        JobSkill(
                            name=normalize_skill_name(s["name"]),
                            importance=s.get("importance", "medium"),
                            category=s.get("category", get_skill_category(s["name"])),
                            relevance_reason=s.get("relevance_reason", "")
                        )
                        for s in skills_list if "name" in s
                    ]
    except Exception as e:
        logger.warning(f"LLM call failed for job role analysis: {e}. Falling back to heuristic catalog.")

    return None

async def analyze_job_role(job_role: str) -> JobRoleAnalysis:
    """
    Analyzes a target job role.
    If exact or close match in catalog, uses the curated benchmark (fast & robust).
    If custom role and LLM configured, asks LLM.
    If demo mode or LLM unavailable, matches closest role or synthesizes smartly.
    """
    cleaned_role = job_role.strip()
    lowered = cleaned_role.lower()

    # 1. Exact catalog match
    for role_name, skills_data in JOB_ROLE_CATALOG.items():
        if role_name.lower() == lowered:
            skills = [
                JobSkill(
                    name=normalize_skill_name(s["name"]),
                    importance=s["importance"],
                    category=get_skill_category(s["name"]),
                    relevance_reason=s["relevance_reason"]
                )
                for s in skills_data
            ]
            return JobRoleAnalysis(
                job_role=role_name,
                skills=skills,
                is_demo_mode=settings.demo_mode or not bool(settings.llm_api_key)
            )

    # 2. Try LLM if configured and not demo mode
    if not settings.demo_mode and settings.llm_api_key:
        llm_skills = await call_llm_for_job_analysis(cleaned_role)
        if llm_skills:
            return JobRoleAnalysis(
                job_role=cleaned_role,
                skills=llm_skills,
                is_demo_mode=False
            )

    # 3. Partial keyword matching against catalog for custom roles (e.g. 'Senior Full Stack Engineer')
    for role_name, skills_data in JOB_ROLE_CATALOG.items():
        if role_name.lower() in lowered or any(word in lowered for word in role_name.lower().split() if len(word) > 3):
            skills = [
                JobSkill(
                    name=normalize_skill_name(s["name"]),
                    importance=s["importance"],
                    category=get_skill_category(s["name"]),
                    relevance_reason=s["relevance_reason"]
                )
                for s in skills_data
            ]
            return JobRoleAnalysis(
                job_role=cleaned_role,
                skills=skills,
                is_demo_mode=True
            )

    # 4. Fallback default software engineer profile if custom role is completely novel
    default_skills = [
        JobSkill(
            name=normalize_skill_name(s["name"]),
            importance=s["importance"],
            category=get_skill_category(s["name"]),
            relevance_reason=s["relevance_reason"]
        )
        for s in JOB_ROLE_CATALOG["Software Engineer"]
    ]
    return JobRoleAnalysis(
        job_role=cleaned_role,
        skills=default_skills,
        is_demo_mode=True
    )

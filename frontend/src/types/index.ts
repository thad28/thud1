export interface Skill {
  name: string;
  category: string;
  confidence: number;
  evidence: string;
  is_explicit: boolean;
}

export interface ResumeUploadResponse {
  resume_id: string;
  filename: string;
  file_size_bytes: number;
  page_count: number;
  preview_text: string;
}

export interface ResumeAnalysis {
  resume_id: string;
  filename: string;
  total_skills: number;
  skills: Skill[];
  categories: Record<string, string[]>;
  is_demo_mode: boolean;
}

export interface JobSkill {
  name: string;
  importance: 'high' | 'medium' | 'low';
  category?: string;
  relevance_reason?: string;
}

export interface JobRoleAnalysis {
  job_role: string;
  skills: JobSkill[];
  is_demo_mode: boolean;
}

export interface MissingSkillDetail {
  name: string;
  importance: string;
  rank: number;
  relevance_reason: string;
  category?: string;
}

export interface SkillGapResult {
  job_role: string;
  total_target_skills: number;
  total_resume_skills: number;
  matched_skills: string[];
  missing_skills: string[];
  top_missing_skills: MissingSkillDetail[];
  match_percentage: number;
  summary: string;
}

export interface HealthResponse {
  status: string;
  llm_provider: string;
  llm_model: string;
  demo_mode: boolean;
}

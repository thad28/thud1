import type {
  ResumeUploadResponse,
  ResumeAnalysis,
  JobRoleAnalysis,
  JobSkill,
  SkillGapResult,
  HealthResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `Server error (${res.status})`;
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        errorMsg = typeof errorJson.detail === 'string'
          ? errorJson.detail
          : JSON.stringify(errorJson.detail);
      }
    } catch {
      // Non-JSON error body
    }
    throw new Error(errorMsg);
  }
  return res.json() as Promise<T>;
}

export const api = {
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE_URL}/health`);
    return handleResponse<HealthResponse>(res);
  },

  async getPresetJobRoles(): Promise<string[]> {
    const res = await fetch(`${API_BASE_URL}/job/roles`);
    const data = await handleResponse<{ roles: string[] }>(res);
    return data.roles;
  },

  async uploadResume(file: File): Promise<ResumeUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/resume/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<ResumeUploadResponse>(res);
  },

  async loadSampleResume(): Promise<ResumeUploadResponse> {
    const res = await fetch(`${API_BASE_URL}/demo/load-sample`, {
      method: 'POST',
    });
    return handleResponse<ResumeUploadResponse>(res);
  },

  async analyzeResume(resumeId: string): Promise<ResumeAnalysis> {
    const res = await fetch(`${API_BASE_URL}/resume/${resumeId}/analyze`, {
      method: 'POST',
    });
    return handleResponse<ResumeAnalysis>(res);
  },

  async analyzeJobRole(jobRole: string): Promise<JobRoleAnalysis> {
    const res = await fetch(`${API_BASE_URL}/job/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ job_role: jobRole }),
    });
    return handleResponse<JobRoleAnalysis>(res);
  },

  async calculateSkillGap(
    resumeSkills: string[],
    jobSkills: JobSkill[],
    jobRole: string
  ): Promise<SkillGapResult> {
    const res = await fetch(`${API_BASE_URL}/skill-gap`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume_skills: resumeSkills,
        job_skills: jobSkills,
        job_role: jobRole,
      }),
    });
    return handleResponse<SkillGapResult>(res);
  },
};

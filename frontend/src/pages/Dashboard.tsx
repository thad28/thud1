import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type {
  ResumeUploadResponse,
  ResumeAnalysis,
  JobRoleAnalysis,
  SkillGapResult,
  Skill,
  HealthResponse
} from '../types';
import { Navbar } from '../components/Navbar';
import { ResumeUpload } from '../components/ResumeUpload';
import { SkillBadges } from '../components/SkillBadges';
import { JobRoleSelector } from '../components/JobRoleSelector';
import { SkillGapCard } from '../components/SkillGapCard';
import { EvidenceModal } from '../components/EvidenceModal';
import { AlertTriangle, Loader2, FileText, ChevronDown, ChevronUp } from 'lucide-react';

const DEFAULT_PRESET_ROLES = [
  'Full Stack Developer',
  'Backend Developer',
  'Frontend Developer',
  'Data Scientist',
  'Machine Learning Engineer',
  'DevOps Engineer',
  'Cloud Engineer',
  'Software Engineer'
];

export const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [presetRoles, setPresetRoles] = useState<string[]>(DEFAULT_PRESET_ROLES);

  // Resume State
  const [uploadedResume, setUploadedResume] = useState<ResumeUploadResponse | null>(null);
  const [resumeAnalysis, setResumeAnalysis] = useState<ResumeAnalysis | null>(null);
  const [showTextPreview, setShowTextPreview] = useState<boolean>(false);

  // Target Job & Gap State
  const [selectedRole, setSelectedRole] = useState<string>('Full Stack Developer');
  const [skillGapResult, setSkillGapResult] = useState<SkillGapResult | null>(null);

  // Modal State
  const [inspectingSkill, setInspectingSkill] = useState<Skill | null>(null);

  // Loading States
  const [isProcessingResume, setIsProcessingResume] = useState<boolean>(false);
  const [loadingMessage, setLoadingMessage] = useState<string>('');
  const [isAnalyzingRole, setIsAnalyzingRole] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Fetch initial health & preset roles on mount
  useEffect(() => {
    const initApp = async () => {
      try {
        const [healthRes, rolesRes] = await Promise.allSettled([
          api.getHealth(),
          api.getPresetJobRoles()
        ]);
        if (healthRes.status === 'fulfilled') {
          setHealth(healthRes.value);
        }
        if (rolesRes.status === 'fulfilled' && rolesRes.value.length > 0) {
          setPresetRoles(rolesRes.value);
        }
      } catch (e) {
        console.warn('Initial server health check failed', e);
      }
    };
    initApp();
  }, []);

  // Compute skill gap whenever resume analysis or job analysis changes
  const runGapAnalysis = async (
    resumeSkills: string[],
    jobRole: string,
    jobSkillsData?: JobRoleAnalysis
  ) => {
    try {
      setIsAnalyzingRole(true);
      let targetJob = jobSkillsData;

      if (!targetJob) {
        targetJob = await api.analyzeJobRole(jobRole);
      }

      const gap = await api.calculateSkillGap(
        resumeSkills,
        targetJob.skills,
        jobRole
      );
      setSkillGapResult(gap);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to complete skill gap analysis.');
    } finally {
      setIsAnalyzingRole(false);
    }
  };

  // Main flow: upload PDF -> extract text -> LLM skill extraction -> initial gap analysis
  const handleAnalyzeResumeFile = async (file: File) => {
    try {
      setErrorMessage(null);
      setIsProcessingResume(true);
      setLoadingMessage('Extracting clean text with PyMuPDF...');

      // Step 1: Upload & Extract text
      const uploadRes = await api.uploadResume(file);
      setUploadedResume(uploadRes);

      // Step 2: Extract & Normalize skills with LLM / Heuristics
      setLoadingMessage('Analyzing skills and normalizing aliases...');
      const analysisRes = await api.analyzeResume(uploadRes.resume_id);
      setResumeAnalysis(analysisRes);

      // Step 3: Run target job role benchmark & skill gap
      setLoadingMessage(`Benchmarking skills against ${selectedRole}...`);
      const skillNames = analysisRes.skills.map((s) => s.name);
      await runGapAnalysis(skillNames, selectedRole);
    } catch (err: any) {
      setErrorMessage(err.message || 'An error occurred during resume processing.');
      setUploadedResume(null);
      setResumeAnalysis(null);
    } finally {
      setIsProcessingResume(false);
      setLoadingMessage('');
    }
  };

  // 1-Click Demo Sample Resume Loader
  const handleLoadSampleResume = async () => {
    try {
      setErrorMessage(null);
      setIsProcessingResume(true);
      setLoadingMessage('Loading sample full-stack resume...');

      const uploadRes = await api.loadSampleResume();
      setUploadedResume(uploadRes);

      setLoadingMessage('Extracting and categorizing skills...');
      const analysisRes = await api.analyzeResume(uploadRes.resume_id);
      setResumeAnalysis(analysisRes);

      setLoadingMessage(`Benchmarking skills against ${selectedRole}...`);
      const skillNames = analysisRes.skills.map((s) => s.name);
      await runGapAnalysis(skillNames, selectedRole);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load sample resume.');
      setUploadedResume(null);
      setResumeAnalysis(null);
    } finally {
      setIsProcessingResume(false);
      setLoadingMessage('');
    }
  };

  // When user selects or types a new target role
  const handleSelectJobRole = async (role: string) => {
    setSelectedRole(role);
    if (resumeAnalysis) {
      const skillNames = resumeAnalysis.skills.map((s) => s.name);
      await runGapAnalysis(skillNames, role);
    }
  };

  // Reset to initial upload state
  const handleReset = () => {
    setUploadedResume(null);
    setResumeAnalysis(null);
    setSkillGapResult(null);
    setErrorMessage(null);
    setSelectedRole('Full Stack Developer');
    setShowTextPreview(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar
        health={health}
        onLoadSample={handleLoadSampleResume}
        onReset={handleReset}
        hasResume={Boolean(resumeAnalysis)}
        isLoading={isProcessingResume || isAnalyzingRole}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        {/* Global Error Banner */}
        {errorMessage && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start space-x-3 shadow-sm animate-fade-in">
            <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="font-semibold block">Notification</span>
              <span className="text-rose-700">{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-rose-400 hover:text-rose-600 font-bold px-1"
            >
              ×
            </button>
          </div>
        )}

        {!resumeAnalysis ? (
          /* STEP 1: RESUME UPLOAD LANDING PAGE */
          <div className="py-6 sm:py-12">
            <ResumeUpload
              onAnalyze={handleAnalyzeResumeFile}
              onLoadSample={handleLoadSampleResume}
              isLoading={isProcessingResume}
              loadingMessage={loadingMessage}
              errorMessage={errorMessage}
              onClearError={() => setErrorMessage(null)}
            />
          </div>
        ) : (
          /* STEP 2 & 3: ANALYSIS DASHBOARD */
          <div className="space-y-8 animate-fade-in">
            {/* Extracted Resume Text Accordion (PyMuPDF verification) */}
            {uploadedResume && (
              <div className="bg-white rounded-2xl border border-slate-200/80 px-6 py-4 shadow-xs">
                <button
                  type="button"
                  onClick={() => setShowTextPreview(!showTextPreview)}
                  className="w-full flex items-center justify-between text-xs font-semibold text-slate-700 hover:text-slate-900"
                >
                  <span className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-brand-600" />
                    <span>
                      Extracted Text Preview ({uploadedResume.page_count} page{uploadedResume.page_count > 1 ? 's' : ''}, {uploadedResume.file_size_bytes} bytes)
                    </span>
                  </span>
                  <span className="flex items-center space-x-1 text-slate-500">
                    <span>{showTextPreview ? 'Hide text' : 'Inspect extracted text'}</span>
                    {showTextPreview ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </span>
                </button>

                {showTextPreview && (
                  <div className="mt-3 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs font-mono text-slate-700 max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                    {uploadedResume.preview_text}
                  </div>
                )}
              </div>
            )}

            {/* Target Job Role Selection */}
            <JobRoleSelector
              selectedRole={selectedRole}
              presetRoles={presetRoles}
              onSelectRole={handleSelectJobRole}
              isLoading={isAnalyzingRole}
            />

            {/* Skill Gap Analysis & Top 3 Missing Skills */}
            {isAnalyzingRole ? (
              <div className="p-12 rounded-2xl bg-white border border-slate-200/80 shadow-md text-center flex flex-col items-center justify-center space-y-3">
                <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
                <p className="text-sm font-semibold text-slate-700">
                  Analyzing skill gap for {selectedRole}...
                </p>
                <p className="text-xs text-slate-400">
                  Comparing normalized resume skills against industry requirements
                </p>
              </div>
            ) : (
              skillGapResult && <SkillGapCard result={skillGapResult} />
            )}

            {/* Extracted Skills Dashboard with Categories & Evidence */}
            <SkillBadges
              analysis={resumeAnalysis}
              onSelectSkill={(skill) => setInspectingSkill(skill)}
            />
          </div>
        )}
      </main>

      {/* Verbatim Resume Evidence Modal */}
      <EvidenceModal
        skill={inspectingSkill}
        onClose={() => setInspectingSkill(null)}
      />

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <div>
            AI Resume Skill Extractor & Job Skill Gap Analyzer • FastAPI + React + Tailwind
          </div>
          <div className="flex items-center space-x-4">
            <span>PyMuPDF Text Engine</span>
            <span>•</span>
            <span>LLM Skill Normalization</span>
            <span>•</span>
            <span>Set-Difference Matching</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

import React, { useState, useRef } from 'react';
import type { DragEvent, ChangeEvent } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, ArrowRight, Loader2, Sparkles } from 'lucide-react';

interface ResumeUploadProps {
  onAnalyze: (file: File) => void;
  onLoadSample: () => void;
  isLoading: boolean;
  loadingMessage?: string;
  errorMessage?: string | null;
  onClearError: () => void;
}

export const ResumeUpload: React.FC<ResumeUploadProps> = ({
  onAnalyze,
  onLoadSample,
  isLoading,
  loadingMessage,
  errorMessage,
  onClearError
}) => {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const validateAndSetFile = (file: File) => {
    setLocalError(null);
    onClearError();

    // Check file type
    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      setLocalError('Invalid file type. Please upload a PDF file (.pdf).');
      setSelectedFile(null);
      return;
    }

    // Check file size (10 MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setLocalError('File size exceeds the 10 MB limit. Please upload a smaller PDF resume.');
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleTriggerUpload = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleSubmit = () => {
    if (selectedFile) {
      onAnalyze(selectedFile);
    }
  };

  const activeError = localError || errorMessage;

  return (
    <div className="w-full max-w-3xl mx-auto">
      {/* Hero Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-50 border border-brand-200/80 text-brand-700 text-xs font-semibold mb-3">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>AI-Powered Resume Skill Intelligence</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          AI Resume Skill Extractor
        </h1>
        <p className="mt-2.5 text-sm sm:text-base text-slate-600 max-w-xl mx-auto leading-relaxed">
          Upload your resume in PDF format to extract, normalize, and categorize your technical capabilities, then benchmark them against target industry job roles.
        </p>
      </div>

      {/* Error Banner */}
      {activeError && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start space-x-3 shadow-sm animate-fade-in">
          <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold block">Upload Error</span>
            <span className="text-rose-700">{activeError}</span>
          </div>
          <button
            onClick={() => {
              setLocalError(null);
              onClearError();
            }}
            className="text-rose-400 hover:text-rose-600 font-bold px-1"
          >
            ×
          </button>
        </div>
      )}

      {/* Main Upload Card */}
      <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/60 border border-slate-200/80 p-6 sm:p-8 transition-all">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          className="hidden"
          onChange={handleChange}
          disabled={isLoading}
        />

        {/* Dropzone Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={handleTriggerUpload}
          className={`relative border-2 border-dashed rounded-xl p-8 sm:p-10 text-center cursor-pointer transition-all duration-200 ${
            dragActive
              ? 'border-brand-500 bg-brand-50/70 scale-[0.99]'
              : selectedFile
              ? 'border-emerald-400 bg-emerald-50/30 hover:bg-emerald-50/50'
              : 'border-slate-300 hover:border-brand-400 bg-slate-50/50 hover:bg-brand-50/20'
          }`}
        >
          <div className="flex flex-col items-center justify-center space-y-3">
            <div
              className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all ${
                selectedFile
                  ? 'bg-emerald-100 text-emerald-600'
                  : dragActive
                  ? 'bg-brand-100 text-brand-600 scale-110'
                  : 'bg-indigo-50 text-brand-600'
              }`}
            >
              {selectedFile ? (
                <FileText className="w-8 h-8" />
              ) : (
                <UploadCloud className="w-8 h-8" />
              )}
            </div>

            {selectedFile ? (
              <div>
                <div className="flex items-center justify-center space-x-2 text-slate-800 font-semibold text-base">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span className="truncate max-w-xs">{selectedFile.name}</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  {formatFileSize(selectedFile.size)} • Click or drop another PDF to replace
                </p>
              </div>
            ) : (
              <div>
                <p className="text-base font-semibold text-slate-700">
                  Drag & Drop your resume PDF here
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  or <span className="text-brand-600 font-medium underline">browse files</span> from your computer
                </p>
                <p className="text-[11px] text-slate-400 mt-2">
                  Only PDF files up to 10 MB supported
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Action Button & Demo Option */}
        <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <button
            type="button"
            onClick={onLoadSample}
            disabled={isLoading}
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 text-xs font-semibold text-slate-600 hover:text-brand-700 hover:bg-brand-50 px-4 py-2.5 rounded-xl border border-slate-200 transition disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4 text-accent-500" />
            <span>Try with Sample Resume</span>
          </button>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!selectedFile || isLoading}
            className={`w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-3 rounded-xl text-sm font-semibold text-white transition-all shadow-md active:scale-95 ${
              !selectedFile || isLoading
                ? 'bg-slate-300 cursor-not-allowed text-slate-500 shadow-none'
                : 'bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-700 hover:to-accent-700 shadow-brand-500/25 hover:shadow-lg'
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{loadingMessage || 'Extracting Skills...'}</span>
              </>
            ) : (
              <>
                <span>Analyze Resume</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Feature Badges Footer */}
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
        <div className="p-3 rounded-xl bg-white/70 border border-slate-200/60 shadow-xs">
          <span className="text-xs font-semibold text-slate-800 block">PyMuPDF Text Engine</span>
          <span className="text-[11px] text-slate-500">Fast, clean multi-page text extraction</span>
        </div>
        <div className="p-3 rounded-xl bg-white/70 border border-slate-200/60 shadow-xs">
          <span className="text-xs font-semibold text-slate-800 block">Skill Normalization</span>
          <span className="text-[11px] text-slate-500">Resolves aliases (JS → JavaScript)</span>
        </div>
        <div className="p-3 rounded-xl bg-white/70 border border-slate-200/60 shadow-xs">
          <span className="text-xs font-semibold text-slate-800 block">Gap & Top 3 Missing</span>
          <span className="text-[11px] text-slate-500">Benchmark against target job roles</span>
        </div>
      </div>
    </div>
  );
};

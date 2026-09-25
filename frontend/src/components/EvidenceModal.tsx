import React, { useEffect } from 'react';
import { X, Quote, ShieldCheck, Tag } from 'lucide-react';
import type { Skill } from '../types';

interface EvidenceModalProps {
  skill: Skill | null;
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ skill, onClose }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!skill) return null;

  const confidencePct = Math.round(skill.confidence * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-fade-in">
      <div
        className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden transform transition-all animate-scale-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50/80 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Tag className="w-4 h-4 text-brand-600" />
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Skill Details & Evidence
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* Skill Title & Badges */}
          <div>
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-slate-900">{skill.name}</h3>
              <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-brand-100 text-brand-800 border border-brand-200">
                {skill.category}
              </span>
            </div>
            <div className="mt-2 flex items-center space-x-3 text-xs text-slate-500">
              <span className="inline-flex items-center space-x-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                <span className="font-medium text-slate-700">
                  {skill.is_explicit ? 'Explicitly Mentioned' : 'Contextually Inferred'}
                </span>
              </span>
              <span>•</span>
              <span>
                Confidence: <strong className="text-slate-800">{confidencePct}%</strong>
              </span>
            </div>
          </div>

          {/* Confidence Meter */}
          <div>
            <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
              <span>Extraction Confidence</span>
              <span className="text-brand-600 font-bold">{confidencePct}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-brand-500 to-accent-500 rounded-full transition-all duration-500"
                style={{ width: `${confidencePct}%` }}
              />
            </div>
          </div>

          {/* Evidence Quote */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <Quote className="w-3.5 h-3.5 text-brand-600" />
              <span>Resume Evidence Snippet</span>
            </label>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/90 text-slate-700 text-sm italic font-mono leading-relaxed relative">
              "{skill.evidence}"
            </div>
            <p className="text-[11px] text-slate-400 mt-2">
              Extracted directly from the submitted resume context without fabrication.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-200 rounded-xl transition shadow-xs"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

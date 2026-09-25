import React from 'react';
import { Sparkles, FileText, RefreshCw, Cpu } from 'lucide-react';
import type { HealthResponse } from '../types';

interface NavbarProps {
  health: HealthResponse | null;
  onLoadSample: () => void;
  onReset: () => void;
  hasResume: boolean;
  isLoading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  onLoadSample,
  onReset,
  hasResume,
  isLoading
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 bg-white/90 backdrop-blur-md transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={onReset}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-accent-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">
                  AI Resume Skill Extractor
                </span>
                <span className="hidden md:inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-brand-50 text-brand-700 border border-brand-200">
                  v1.0
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Skill Normalization & Job Role Gap Analyzer
              </p>
            </div>
          </div>

          {/* Right Status & Actions */}
          <div className="flex items-center space-x-3">
            {/* Mode Indicator */}
            {health && (
              <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-100 border border-slate-200/70 text-xs">
                <Cpu className="w-3.5 h-3.5 text-brand-600" />
                <span className="text-slate-600 font-medium">Engine:</span>
                {health.demo_mode ? (
                  <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-semibold bg-amber-100 text-amber-800">
                    Demo Mode (Catalog & Heuristics)
                  </span>
                ) : (
                  <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">
                    Live AI ({health.llm_provider.toUpperCase()})
                  </span>
                )}
              </div>
            )}

            {/* Quick Demo Sample Button */}
            {!hasResume && (
              <button
                type="button"
                onClick={onLoadSample}
                disabled={isLoading}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-brand-700 bg-brand-50 hover:bg-brand-100 border border-brand-200/80 transition shadow-sm active:scale-95 disabled:opacity-50"
              >
                <FileText className="w-3.5 h-3.5 text-brand-600" />
                <span>Load Sample Resume</span>
              </button>
            )}

            {/* Reset / Start Over */}
            {hasResume && (
              <button
                type="button"
                onClick={onReset}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 transition"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Start Over</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

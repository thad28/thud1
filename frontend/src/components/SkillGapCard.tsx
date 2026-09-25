import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Award,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Info
} from 'lucide-react';
import type { SkillGapResult } from '../types';

interface SkillGapCardProps {
  result: SkillGapResult;
}

export const SkillGapCard: React.FC<SkillGapCardProps> = ({ result }) => {
  const [showAllMissing, setShowAllMissing] = useState<boolean>(false);

  const matchScore = Math.round(result.match_percentage);

  // Score color scheme
  const getScoreTheme = (score: number) => {
    if (score >= 75) {
      return {
        badgeBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
        progressBar: 'from-emerald-500 to-teal-500',
        text: 'text-emerald-700',
        label: 'Strong Match'
      };
    }
    if (score >= 50) {
      return {
        badgeBg: 'bg-amber-50 text-amber-800 border-amber-200',
        progressBar: 'from-amber-500 to-orange-500',
        text: 'text-amber-700',
        label: 'Moderate Match'
      };
    }
    return {
      badgeBg: 'bg-rose-50 text-rose-800 border-rose-200',
      progressBar: 'from-rose-500 to-red-500',
      text: 'text-rose-700',
      label: 'Foundational Match'
    };
  };

  const theme = getScoreTheme(matchScore);
  const remainingMissing = result.missing_skills.slice(3);

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-200/80 overflow-hidden space-y-6">
      {/* Top Banner / Match Score Card */}
      <div className="p-6 sm:p-7 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white relative overflow-hidden">
        {/* Decorative backdrop shapes */}
        <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-brand-500/10 blur-2xl pointer-events-none" />
        <div className="absolute -bottom-10 -left-10 w-40 h-40 rounded-full bg-accent-500/10 blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center space-x-2 text-brand-300 text-xs font-bold uppercase tracking-wider mb-1">
              <TrendingUp className="w-4 h-4" />
              <span>Job Role Skill Gap Analysis</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {result.job_role}
            </h2>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-xl leading-relaxed">
              {result.summary}
            </p>
          </div>

          {/* Match Score Gauge */}
          <div className="flex items-center space-x-4 bg-white/10 backdrop-blur-md px-5 py-4 rounded-2xl border border-white/10 shrink-0 self-stretch sm:self-auto justify-between sm:justify-start">
            <div className="text-right">
              <span className="block text-[11px] font-semibold uppercase tracking-wider text-slate-300">
                Your Match
              </span>
              <span className="text-3xl font-black tracking-tight text-white">
                {matchScore}%
              </span>
            </div>
            <div className="h-10 w-px bg-white/20" />
            <div className="text-left">
              <span className="block text-[11px] font-medium text-slate-300">Alignment</span>
              <span className="inline-block px-2 py-0.5 rounded-full text-xs font-bold bg-white/20 text-white">
                {theme.label}
              </span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${theme.progressBar} rounded-full transition-all duration-700 ease-out`}
              style={{ width: `${Math.min(Math.max(matchScore, 5), 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-[11px] text-slate-400 mt-1.5 font-medium">
            <span>{result.matched_skills.length} skills matched</span>
            <span>{result.total_target_skills} industry benchmark skills</span>
          </div>
        </div>
      </div>

      <div className="px-6 sm:px-7 pb-7 space-y-6">
        {/* TOP 3 MISSING SKILLS SECTION (PRIMARY REQUIREMENT) */}
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-7 h-7 rounded-lg bg-rose-50 flex items-center justify-center text-rose-600 border border-rose-200">
              <AlertCircle className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 tracking-tight">
                Top 3 Missing Skills
              </h3>
              <p className="text-xs text-slate-500">
                Prioritized recommendations to bridge the gap for {result.job_role}
              </p>
            </div>
          </div>

          {result.top_missing_skills.length === 0 ? (
            <div className="p-6 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-center space-y-2">
              <Award className="w-8 h-8 text-emerald-600 mx-auto" />
              <p className="text-sm font-bold">Outstanding Profile Alignment!</p>
              <p className="text-xs text-emerald-700 max-w-md mx-auto">
                Your resume includes all core skills identified for this role benchmark.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {result.top_missing_skills.map((skill) => (
                <div
                  key={skill.name}
                  className="relative p-5 rounded-2xl bg-slate-50/70 border border-slate-200/90 shadow-2xs hover:shadow-md hover:border-slate-300 transition-all flex flex-col justify-between space-y-3"
                >
                  <div>
                    {/* Rank Badge & Importance */}
                    <div className="flex items-center justify-between">
                      <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-white border border-slate-200 shadow-2xs">
                        <span className="text-xs font-extrabold text-brand-600">
                          #{skill.rank}
                        </span>
                        <span className="text-[11px] font-semibold text-slate-600">
                          Priority
                        </span>
                      </div>

                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${
                          skill.importance === 'high'
                            ? 'bg-rose-100 text-rose-800 border border-rose-200'
                            : 'bg-amber-100 text-amber-800 border border-amber-200'
                        }`}
                      >
                        {skill.importance} Priority
                      </span>
                    </div>

                    {/* Skill Name */}
                    <h4 className="text-base font-bold text-slate-900 mt-3">
                      {skill.name}
                    </h4>

                    {/* Category */}
                    {skill.category && (
                      <span className="inline-block text-[11px] text-slate-500 font-medium">
                        {skill.category}
                      </span>
                    )}

                    {/* Relevance Explanation */}
                    <p className="mt-2 text-xs text-slate-600 leading-relaxed">
                      {skill.relevance_reason}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-200/60 text-[11px] text-brand-700 font-semibold flex items-center space-x-1">
                    <Sparkles className="w-3.5 h-3.5 text-accent-500" />
                    <span>Recommended for upskilling</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Realistic Career Context Disclaimer */}
          <div className="mt-4 p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] text-slate-500 flex items-start space-x-2">
            <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
            <span>
              <strong>Note:</strong> These suggestions reflect commonly requested industry skills for {result.job_role} stacks and serve as strategic career guidance rather than universal employment guarantees.
            </span>
          </div>
        </div>

        {/* Matched Skills Overview */}
        <div className="pt-4 border-t border-slate-100">
          <div className="flex items-center space-x-2 mb-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <h4 className="text-sm font-bold text-slate-900">
              Matched Skills ({result.matched_skills.length})
            </h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {result.matched_skills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-50 text-emerald-900 border border-emerald-200 shadow-2xs"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>{skill}</span>
              </span>
            ))}
          </div>
        </div>

        {/* Other Missing Skills Accordion */}
        {remainingMissing.length > 0 && (
          <div className="pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setShowAllMissing(!showAllMissing)}
              className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
            >
              <span>
                {showAllMissing ? 'Hide' : 'Show'} other missing skills ({remainingMissing.length})
              </span>
              {showAllMissing ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>

            {showAllMissing && (
              <div className="mt-3 flex flex-wrap gap-2 animate-fade-in">
                {remainingMissing.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center px-3 py-1 rounded-xl text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

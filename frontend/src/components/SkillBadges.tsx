import React, { useState, useMemo } from 'react';
import { Search, Filter, FileText, Eye } from 'lucide-react';
import type { ResumeAnalysis, Skill } from '../types';

interface SkillBadgesProps {
  analysis: ResumeAnalysis;
  onSelectSkill: (skill: Skill) => void;
}

// Category color mappings
const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string; pill: string }> = {
  'Programming Language': {
    bg: 'bg-indigo-50/80 hover:bg-indigo-100/90',
    text: 'text-indigo-900',
    border: 'border-indigo-200',
    pill: 'bg-indigo-200/80 text-indigo-900'
  },
  'Frontend': {
    bg: 'bg-sky-50/80 hover:bg-sky-100/90',
    text: 'text-sky-900',
    border: 'border-sky-200',
    pill: 'bg-sky-200/80 text-sky-900'
  },
  'Backend': {
    bg: 'bg-emerald-50/80 hover:bg-emerald-100/90',
    text: 'text-emerald-900',
    border: 'border-emerald-200',
    pill: 'bg-emerald-200/80 text-emerald-900'
  },
  'Database': {
    bg: 'bg-amber-50/80 hover:bg-amber-100/90',
    text: 'text-amber-900',
    border: 'border-amber-200',
    pill: 'bg-amber-200/80 text-amber-900'
  },
  'Cloud / DevOps': {
    bg: 'bg-purple-50/80 hover:bg-purple-100/90',
    text: 'text-purple-900',
    border: 'border-purple-200',
    pill: 'bg-purple-200/80 text-purple-900'
  },
  'AI & Machine Learning': {
    bg: 'bg-rose-50/80 hover:bg-rose-100/90',
    text: 'text-rose-900',
    border: 'border-rose-200',
    pill: 'bg-rose-200/80 text-rose-900'
  },
  'Tools & Methodologies': {
    bg: 'bg-teal-50/80 hover:bg-teal-100/90',
    text: 'text-teal-900',
    border: 'border-teal-200',
    pill: 'bg-teal-200/80 text-teal-900'
  },
  'Professional Skills': {
    bg: 'bg-slate-100 hover:bg-slate-200',
    text: 'text-slate-800',
    border: 'border-slate-300',
    pill: 'bg-slate-200 text-slate-800'
  },
  'Mobile Development': {
    bg: 'bg-cyan-50/80 hover:bg-cyan-100/90',
    text: 'text-cyan-900',
    border: 'border-cyan-200',
    pill: 'bg-cyan-200/80 text-cyan-900'
  }
};

const DEFAULT_CATEGORY_COLOR = {
  bg: 'bg-slate-50 hover:bg-slate-100',
  text: 'text-slate-800',
  border: 'border-slate-200',
  pill: 'bg-slate-200 text-slate-800'
};

export const SkillBadges: React.FC<SkillBadgesProps> = ({ analysis, onSelectSkill }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [viewMode, setViewMode] = useState<'grouped' | 'cloud'>('grouped');

  // Categories list
  const categoryOptions = useMemo(() => {
    const cats = Object.keys(analysis.categories);
    return ['All', ...cats];
  }, [analysis.categories]);

  // Filter skills based on search and category
  const filteredSkills = useMemo(() => {
    return analysis.skills.filter((skill) => {
      const matchesSearch = skill.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory =
        selectedCategory === 'All' || skill.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [analysis.skills, searchTerm, selectedCategory]);

  // Group filtered skills by category
  const groupedSkills = useMemo(() => {
    const groups: Record<string, Skill[]> = {};
    for (const skill of filteredSkills) {
      const cat = skill.category || 'Other Technical Skills';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(skill);
    }
    return groups;
  }, [filteredSkills]);

  return (
    <div className="bg-white rounded-2xl shadow-md border border-slate-200/80 p-6 sm:p-7 space-y-6">
      {/* Resume Overview Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-slate-100 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold text-brand-600 uppercase tracking-wider">
              Resume Analysis
            </span>
            {analysis.is_demo_mode && (
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-100 text-amber-800 border border-amber-200">
                Demo Analysis Active
              </span>
            )}
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mt-1 flex items-center space-x-2">
            <FileText className="w-5 h-5 text-slate-400" />
            <span className="truncate max-w-sm sm:max-w-md">{analysis.filename}</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Normalized across canonical industry terms • {analysis.total_skills} unique skills extracted
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center space-x-1.5 p-1 bg-slate-100 rounded-xl self-start sm:self-center border border-slate-200/60">
          <button
            type="button"
            onClick={() => setViewMode('grouped')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              viewMode === 'grouped'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            By Category
          </button>
          <button
            type="button"
            onClick={() => setViewMode('cloud')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              viewMode === 'cloud'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            All Skills ({analysis.total_skills})
          </button>
        </div>
      </div>

      {/* Search and Category Filter Toolbar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search extracted skills (e.g. Python, React)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs font-bold"
            >
              ×
            </button>
          )}
        </div>

        {/* Category Pills Slider / Bar */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 max-w-full text-xs no-scrollbar">
          <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0 mr-1" />
          {categoryOptions.map((cat) => {
            const count =
              cat === 'All'
                ? analysis.total_skills
                : analysis.categories[cat]?.length || 0;
            return (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-lg whitespace-nowrap font-medium transition shrink-0 ${
                  selectedCategory === cat
                    ? 'bg-brand-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {cat} <span className="text-[10px] opacity-80">({count})</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Empty State */}
      {filteredSkills.length === 0 && (
        <div className="py-12 text-center text-slate-500">
          <p className="text-sm font-medium">No skills match "{searchTerm}"</p>
          <button
            onClick={() => {
              setSearchTerm('');
              setSelectedCategory('All');
            }}
            className="mt-2 text-xs text-brand-600 hover:underline font-semibold"
          >
            Clear filters
          </button>
        </div>
      )}

      {/* Skills Display: Grouped by Category */}
      {viewMode === 'grouped' && (
        <div className="space-y-6">
          {Object.entries(groupedSkills).map(([category, skills]) => {
            const colors = CATEGORY_COLORS[category] || DEFAULT_CATEGORY_COLOR;
            return (
              <div key={category} className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center space-x-1.5">
                    <span className="w-2 h-2 rounded-full bg-brand-500" />
                    <span>{category}</span>
                    <span className="text-slate-400 font-normal">({skills.length})</span>
                  </h3>
                </div>

                <div className="flex flex-wrap gap-2">
                  {skills.map((skill) => (
                    <button
                      key={skill.name}
                      type="button"
                      onClick={() => onSelectSkill(skill)}
                      className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border transition-all duration-150 cursor-pointer shadow-2xs hover:scale-102 active:scale-98 ${colors.bg} ${colors.text} ${colors.border}`}
                      title={`Click to view resume evidence for ${skill.name}`}
                    >
                      <span className="font-semibold">{skill.name}</span>
                      <span
                        className={`px-1.5 py-0.5 rounded-md text-[10px] font-bold ${colors.pill}`}
                      >
                        {Math.round(skill.confidence * 100)}%
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Skills Display: Flat Cloud */}
      {viewMode === 'cloud' && (
        <div className="flex flex-wrap gap-2.5">
          {filteredSkills.map((skill) => {
            const colors = CATEGORY_COLORS[skill.category] || DEFAULT_CATEGORY_COLOR;
            return (
              <button
                key={skill.name}
                type="button"
                onClick={() => onSelectSkill(skill)}
                className={`inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all duration-150 cursor-pointer shadow-xs hover:scale-103 active:scale-97 ${colors.bg} ${colors.text} ${colors.border}`}
                title={`Click to view resume evidence for ${skill.name}`}
              >
                <span>{skill.name}</span>
                <span className={`px-1.5 py-0.5 rounded-md text-[10px] font-bold ${colors.pill}`}>
                  {Math.round(skill.confidence * 100)}%
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Footer tip */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center space-x-1">
          <Eye className="w-3.5 h-3.5" />
          <span>Click any skill chip to inspect supporting evidence quote from your resume</span>
        </span>
        <span>Normalized & Deduplicated</span>
      </div>
    </div>
  );
};

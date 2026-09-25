import React, { useState } from 'react';
import { Target, Search, ArrowRight, Loader2, Check } from 'lucide-react';

interface JobRoleSelectorProps {
  selectedRole: string;
  presetRoles: string[];
  onSelectRole: (role: string) => void;
  isLoading: boolean;
}

export const JobRoleSelector: React.FC<JobRoleSelectorProps> = ({
  selectedRole,
  presetRoles,
  onSelectRole,
  isLoading
}) => {
  const [customInput, setCustomInput] = useState<string>('');

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customInput.trim().length >= 2) {
      onSelectRole(customInput.trim());
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-md border border-slate-200/80 p-6 sm:p-7 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-brand-50 flex items-center justify-center text-brand-600 border border-brand-200/60">
            <Target className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              Select Target Job Role
            </h3>
            <p className="text-xs text-slate-500">
              Benchmark your extracted skills against current industry role expectations
            </p>
          </div>
        </div>
      </div>

      {/* Preset Role Badges / Chips */}
      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2.5">
          Popular Tech Roles
        </label>
        <div className="flex flex-wrap gap-2">
          {presetRoles.map((role) => {
            const isSelected = selectedRole.toLowerCase() === role.toLowerCase();
            return (
              <button
                key={role}
                type="button"
                onClick={() => onSelectRole(role)}
                disabled={isLoading}
                className={`inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all duration-150 active:scale-95 disabled:opacity-50 ${
                  isSelected
                    ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20 ring-2 ring-brand-600 ring-offset-1'
                    : 'bg-slate-100 hover:bg-slate-200/80 text-slate-700 border border-slate-200/70 hover:border-slate-300'
                }`}
              >
                {isSelected && <Check className="w-3.5 h-3.5 text-white" />}
                <span>{role}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Custom Job Role Input */}
      <div className="pt-3 border-t border-slate-100">
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
          Or Enter Custom Role
        </label>
        <form onSubmit={handleCustomSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="e.g. Senior Full Stack Developer, AI Solutions Architect..."
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              disabled={isLoading}
              className="w-full pl-9 pr-4 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition"
            />
          </div>
          <button
            type="submit"
            disabled={customInput.trim().length < 2 || isLoading}
            className="inline-flex items-center space-x-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition shadow-xs"
          >
            {isLoading && selectedRole === customInput.trim() ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <>
                <span>Analyze</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

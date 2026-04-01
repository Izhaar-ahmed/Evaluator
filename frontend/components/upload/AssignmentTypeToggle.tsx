'use client'

import React from 'react'

interface AssignmentTypeToggleProps {
  assignmentType: 'code' | 'content' | 'mixed'
  setAssignmentType: (type: 'code' | 'content' | 'mixed') => void
}

export const AssignmentTypeToggle: React.FC<AssignmentTypeToggleProps> = ({
  assignmentType,
  setAssignmentType
}) => {
  return (
    <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white flex items-center gap-3">
          <span className="text-2xl">🎯</span> Assignment Type
        </h2>
        <div className="flex bg-slate-950/50 rounded-2xl p-1.5 border border-slate-700/30">
          {(['code', 'content', 'mixed'] as const).map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => setAssignmentType(type)}
              className={`px-5 py-2 text-xs font-bold uppercase tracking-widest rounded-xl transition-all duration-300 ${assignmentType === type
                ? 'bg-gradient-to-br from-indigo-500 to-indigo-600 text-white shadow-[0_0_20px_rgba(99,102,241,0.25)]'
                : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50'
                }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>
      <div className="p-4 bg-slate-950/30 rounded-2xl border border-slate-800/50">
        <p className="text-sm font-medium text-slate-400 leading-relaxed text-center italic">
          {assignmentType === 'code' && "Optimized for evaluating logic, structure, and syntax in Python/C++ codebases."}
          {assignmentType === 'content' && "Ideal for analyzing text quality, core concepts, and structural flow in PDF/TXT."}
          {assignmentType === 'mixed' && "Dual-mode analysis for comprehensive evaluation across both code and text."}
        </p>
      </div>
    </div>
  )
}

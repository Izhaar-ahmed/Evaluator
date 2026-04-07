'use client'

import React from 'react'

interface AssignmentTypeToggleProps {
  assignmentType: 'code' | 'content' | 'mixed'
  setAssignmentType: (type: 'code' | 'content' | 'mixed') => void
}

const typeInfo: Record<string, { icon: string; desc: string }> = {
  code: { icon: 'code', desc: 'Optimized for logic & syntax analysis' },
  content: { icon: 'article', desc: 'Concept & structural format analysis' },
  mixed: { icon: 'join_inner', desc: 'Comprehensive dual-mode evaluation' },
}

export const AssignmentTypeToggle: React.FC<AssignmentTypeToggleProps> = ({
  assignmentType,
  setAssignmentType
}) => {
  return (
    <div className="mb-8">
      <label className="block text-xs font-semibold uppercase tracking-wider text-frost-muted mb-3">
        Assignment Type
      </label>

      <div className="flex p-1 bg-surface-container-lowest rounded-lg w-fit border border-outline-variant/10">
        {(['code', 'content', 'mixed'] as const).map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => setAssignmentType(type)}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-md text-sm font-medium transition-all duration-200 ${
              assignmentType === type
                ? 'bg-violet-primary text-obsidian shadow-sm'
                : 'text-frost-muted hover:text-frost'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">{typeInfo[type].icon}</span>
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      <p className="mt-2 text-xs text-frost-muted/60 ml-1">
        {typeInfo[assignmentType].desc}
      </p>
    </div>
  )
}

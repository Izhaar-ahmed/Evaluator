'use client'

import React from 'react'

interface ContextInputsProps {
  problemStatement: string
  setProblemStatement: (val: string) => void
  rubricSource: 'text' | 'file'
  setRubricSource: (val: 'text' | 'file') => void
  rubricText: string
  setRubricText: (val: string) => void
  rubricFile: File | null
  setRubricFile: (file: File | null) => void
  rubricInputRef: React.RefObject<HTMLInputElement>
  handleRubricFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void
}

export const ContextInputs: React.FC<ContextInputsProps> = ({
  problemStatement,
  setProblemStatement,
  rubricSource,
  setRubricSource,
  rubricText,
  setRubricText,
  rubricFile,
  setRubricFile,
  rubricInputRef,
  handleRubricFileSelect
}) => {
  return (
    <div className="space-y-6">
      {/* Problem Context */}
      <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-3">
            <span className="text-2xl">📝</span> Problem Context
          </h2>
          <span className="px-4 py-1.5 text-xs font-bold tracking-widest uppercase text-slate-500 bg-slate-950/50 rounded-full border border-slate-800/50">
            Optional
          </span>
        </div>
        <div className="relative group">
          <textarea
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
            placeholder="Describe the assignment requirements, specific constraints, or grading criteria..."
            className="w-full h-40 px-6 py-5 bg-slate-950/40 border-2 border-slate-800/50 rounded-2xl text-slate-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 transition-all resize-none text-sm leading-relaxed scrollbar-thin scrollbar-thumb-slate-700 font-medium"
          />
        </div>
      </div>

      {/* Rubric Definition */}
      <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-3">
            <span className="text-2xl">📊</span> Grading Rubric
          </h2>
          <div className="flex bg-slate-950/50 rounded-2xl p-1.5 border border-slate-700/30">
            <button
              type="button"
              onClick={() => setRubricSource('text')}
              className={`px-4 py-2 text-xs font-bold uppercase tracking-widest rounded-xl transition-all duration-300 ${rubricSource === 'text'
                ? 'bg-gradient-to-br from-indigo-500 to-indigo-600 text-white'
                : 'text-slate-500 hover:text-slate-300'
                }`}
            >
              Manual
            </button>
            <button
              type="button"
              onClick={() => setRubricSource('file')}
              className={`px-4 py-2 text-xs font-bold uppercase tracking-widest rounded-xl transition-all duration-300 ${rubricSource === 'file'
                ? 'bg-gradient-to-br from-indigo-500 to-indigo-600 text-white'
                : 'text-slate-500 hover:text-slate-300'
                }`}
            >
              JSON File
            </button>
          </div>
        </div>

        {rubricSource === 'text' ? (
          <div className="relative animate-fade-in group">
            <textarea
              value={rubricText}
              onChange={(e) => setRubricText(e.target.value)}
              placeholder={`Paste text description of the rubric or JSON data...`}
              className="w-full h-48 px-6 py-5 bg-slate-950/40 border-2 border-slate-800/50 rounded-2xl text-indigo-300/80 placeholder-slate-600 font-mono text-xs focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 transition-all resize-none scrollbar-thin scrollbar-thumb-slate-700 leading-normal"
            />
          </div>
        ) : (
          <div className="relative animate-fade-in">
            <input
              ref={rubricInputRef}
              type="file"
              accept=".json"
              onChange={handleRubricFileSelect}
              className="hidden"
            />
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => rubricInputRef.current?.click()}
                className="flex-1 px-6 py-5 bg-slate-950/40 border-2 border-slate-800/50 border-dashed rounded-2xl text-slate-400 hover:text-indigo-400 hover:border-indigo-500/50 hover:bg-slate-900/60 transition-all flex items-center justify-center gap-4 group"
              >
                <div className="w-10 h-10 rounded-xl bg-slate-800/50 flex items-center justify-center group-hover:scale-110 transiton-transform duration-500">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                </div>
                <span className="text-sm font-bold tracking-tight">
                  {rubricFile ? rubricFile.name : 'Choose Rubric Payload'}
                </span>
              </button>
              {rubricFile && (
                <button
                  type="button"
                  onClick={() => setRubricFile(null)}
                  className="px-6 py-5 bg-red-400/5 border-2 border-red-400/10 rounded-2xl text-red-400 hover:bg-red-400/10 transition-all"
                >
                  ✕
                </button>
              )}
            </div>
            <p className="mt-4 text-xs font-bold text-slate-500 tracking-widest text-center uppercase">
              Expects optimized .json schema
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

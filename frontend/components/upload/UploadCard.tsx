'use client'

import React from 'react'

interface UploadCardProps {
  onFileSelect: (files: FileList | null) => void
  dragActive: boolean
  onDrag: (e: React.DragEvent) => void
  onDrop: (e: React.DragEvent) => void
  inputRef: React.RefObject<HTMLInputElement>
  filesCount: number
}

export const UploadCard: React.FC<UploadCardProps> = ({
  onFileSelect,
  dragActive,
  onDrag,
  onDrop,
  inputRef,
  filesCount
}) => {
  return (
    <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white flex items-center gap-3">
          <span className="text-2xl">📂</span> Student Submissions
        </h2>
        <span className="px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-indigo-300 bg-indigo-500/10 rounded-full border border-indigo-500/20">
          Required
        </span>
      </div>

      <div
        onDragEnter={onDrag}
        onDragLeave={onDrag}
        onDragOver={onDrag}
        onDrop={onDrop}
        className={`relative group cursor-pointer transition-all duration-500 ease-out border-2 border-dashed rounded-2xl h-80 flex flex-col items-center justify-center text-center p-12 ${dragActive
          ? 'border-indigo-500 bg-indigo-500/10 scale-[1.01] shadow-[0_0_40px_rgba(99,102,241,0.1)]'
          : 'border-slate-600/50 hover:border-indigo-500/50 bg-slate-800/20 hover:bg-slate-800/40'
          }`}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          onChange={(e) => onFileSelect(e.target.files)}
          multiple
          accept=".py,.cpp,.cc,.cxx,.h,.hpp,.txt,.pdf"
          className="hidden"
        />

        <div className={`transition-all duration-500 ${dragActive ? 'scale-110' : 'group-hover:scale-110'}`}>
          <div className="w-20 h-20 mb-6 rounded-3xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-[0_0_30px_rgba(99,102,241,0.3)] group-hover:shadow-[0_0_40px_rgba(99,102,241,0.5)] transition-all">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
        </div>

        <h3 className="text-2xl font-bold text-white mb-3">
          {dragActive ? 'Drop files now' : 'Click or Drag files'}
        </h3>
        <p className="text-sm text-slate-400 max-w-sm mx-auto leading-relaxed font-medium">
          Upload Python, C++, Text, or PDF files to begin your automated evaluation
        </p>
        
        {/* Subtle decorative glow */}
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
      
      {filesCount > 0 && (
        <p className="text-xs font-bold text-indigo-400/80 uppercase tracking-widest text-center animate-fade-in">
          {filesCount} {filesCount === 1 ? 'file' : 'files'} ready for evaluation
        </p>
      )}
    </div>
  )
}

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
    <div className="space-y-3 mb-6">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-xs font-semibold uppercase tracking-wider text-frost-muted">
          Student Submissions
        </label>
        {filesCount > 0 && (
          <span className="text-xs text-emerald-trust font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-trust animate-pulse" />
            {filesCount} {filesCount === 1 ? 'file' : 'files'} selected
          </span>
        )}
      </div>

      <div
        className="relative cursor-pointer group"
        onDragEnter={onDrag}
        onDragLeave={onDrag}
        onDragOver={onDrag}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <div
          className={`border-2 border-dashed rounded-xl min-h-[200px] flex flex-col items-center justify-center transition-all duration-300 ${
            dragActive
              ? 'border-violet-primary/60 bg-violet-primary/10 scale-[1.01]'
              : 'border-outline-variant/30 bg-surface-container-low/50 hover:border-violet-primary/40 hover:bg-violet-primary/5'
          }`}
        >
          <div className="flex flex-col items-center text-center px-6 py-8">
            <span
              className={`material-symbols-outlined text-4xl text-violet-primary mb-4 transition-transform duration-300 ${
                dragActive ? 'scale-110' : 'group-hover:scale-105'
              }`}
            >
              cloud_upload
            </span>
            <h4 className="text-lg font-semibold mb-2 text-frost">
              {dragActive ? 'Drop files here...' : 'Drag & drop files here'}
            </h4>
            <p className="text-xs text-frost-muted max-w-sm">
              or click to browse. Supports .py, .cpp, .cc, .h, .hpp, .txt, .pdf
            </p>
          </div>
        </div>

        <input
          ref={inputRef}
          type="file"
          onChange={(e) => onFileSelect(e.target.files)}
          multiple
          accept=".py,.cpp,.cc,.cxx,.h,.hpp,.txt,.pdf"
          className="hidden"
        />
      </div>
    </div>
  )
}

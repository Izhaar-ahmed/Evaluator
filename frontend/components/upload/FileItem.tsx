'use client'

import React from 'react'

interface FileItemProps {
  file: File
  onRemove: () => void
}

export const FileItem: React.FC<FileItemProps> = ({ file, onRemove }) => {
  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'py': return '🐍'
      case 'cpp':
      case 'cc':
      case 'cxx':
      case 'h':
      case 'hpp': return '⚙️'
      case 'pdf': return '📕'
      default: return '📄'
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  return (
    <div className="group flex items-center justify-between p-4 bg-slate-800/40 hover:bg-slate-800/60 transition-all rounded-xl border border-slate-700/50 hover:border-slate-600/50 backdrop-blur-sm">
      <div className="flex items-center gap-4 overflow-hidden">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-600/20 flex items-center justify-center flex-shrink-0 border border-indigo-500/10 group-hover:border-indigo-500/30 transition-all">
          <span className="text-xl">{getFileIcon(file.name)}</span>
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-200 truncate group-hover:text-white transition-colors tracking-tight">
            {file.name}
          </p>
          <p className="text-xs text-indigo-400/60 font-medium">
            {formatSize(file.size)}
          </p>
        </div>
      </div>
      <button
        type="button"
        onClick={onRemove}
        className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-all opacity-0 group-hover:opacity-100 focus:opacity-100"
        title="Remove file"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}

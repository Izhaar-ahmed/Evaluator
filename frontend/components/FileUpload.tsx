'use client'

import { useState, useRef } from 'react'
import { FileItem } from './upload/FileItem'
import { UploadCard } from './upload/UploadCard'
import { AssignmentTypeToggle } from './upload/AssignmentTypeToggle'
import { ContextInputs } from './upload/ContextInputs'

interface FileUploadProps {
  onSubmit?: (data: FileUploadData) => void
  onFileChange?: (files: File[]) => void
  loading?: boolean
}

export interface FileUploadData {
  files: File[]
  problemStatement: string
  assignmentType: 'code' | 'content' | 'mixed'
  rubric: string | null
  rubricSource: 'text' | 'file'
}

export default function FileUpload({ onSubmit, onFileChange, loading }: FileUploadProps) {
  // File upload state
  const [files, setFiles] = useState<File[]>([])
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const rubricInputRef = useRef<HTMLInputElement>(null)

  const [problemStatement, setProblemStatement] = useState('')
  const [assignmentType, setAssignmentType] = useState<'code' | 'content' | 'mixed'>('code')
  const [rubricSource, setRubricSource] = useState<'text' | 'file'>('text')
  const [rubricText, setRubricText] = useState('')
  const [rubricFile, setRubricFile] = useState<File | null>(null)
  const [errors, setErrors] = useState<string[]>([])

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files)
    }
  }

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const newFiles: File[] = []
    const allowedExtensions = ['.py', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.txt', '.pdf']

    Array.from(selectedFiles).forEach((file) => {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase()
      if (allowedExtensions.includes(ext)) {
        if (!files.some((f) => f.name === file.name)) {
          newFiles.push(file)
        }
      } else {
        setErrors((prev) => [...prev, `File type not supported: ${file.name}`])
      }
    })

    if (newFiles.length > 0) {
      const updatedFiles = [...files, ...newFiles]
      setFiles(updatedFiles)
      onFileChange?.(updatedFiles)
      setErrors((prev) => prev.filter((e) => !e.startsWith('File type')))
    }
  }

  const removeFile = (index: number) => {
    const updatedFiles = files.filter((_, i) => i !== index)
    setFiles(updatedFiles)
    onFileChange?.(updatedFiles)
  }

  const handleRubricFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.name.endsWith('.json')) {
        setRubricFile(file)
        setErrors((prev) => prev.filter((e) => !e.includes('rubric')))
      } else {
        setErrors((prev) => [...prev, 'Rubric must be a JSON file'])
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const formErrors: string[] = []
    if (files.length === 0) formErrors.push('Please upload at least one student submission')

    if (formErrors.length > 0) {
      setErrors(formErrors)
      return
    }

    let finalRubric = null
    if (rubricSource === 'text') {
      finalRubric = rubricText
    } else if (rubricSource === 'file' && rubricFile) {
      try {
        finalRubric = await rubricFile.text()
        JSON.parse(finalRubric) // Validate JSON
      } catch (err) {
        setErrors(['Invalid JSON in rubric file'])
        return
      }
    }

    if (onSubmit) {
      onSubmit({
        files,
        problemStatement,
        assignmentType,
        rubric: finalRubric,
        rubricSource,
      })
    }
  }

  return (
    <div className="w-full max-w-7xl mx-auto space-y-10">
      <form onSubmit={handleSubmit} className="space-y-12">

        {/* Error Messages */}
        {errors.length > 0 && (
          <div className="bg-red-500/5 border-l-4 border-red-500/50 p-6 rounded-r-2xl animate-fade-in backdrop-blur-sm">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-bold text-red-200 uppercase tracking-widest">Correction Required</h3>
                <ul className="mt-2 text-sm text-red-400/80 list-disc list-inside space-y-1 font-medium">
                  {errors.map((error, idx) => (
                    <li key={idx}>{error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
          {/* Left Column: File Upload */}
          <div className="space-y-10 sticky top-32">
            <UploadCard
              onFileSelect={handleFileSelect}
              dragActive={dragActive}
              onDrag={handleDrag}
              onDrop={handleDrop}
              inputRef={fileInputRef}
              filesCount={files.length}
            />

            {files.length > 0 && (
              <div className="space-y-4 animate-slide-up">
                <p className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] ml-2">
                  Payload Manifest ({files.length})
                </p>
                <div className="grid gap-3 max-h-[32rem] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
                  {files.map((file, idx) => (
                    <FileItem
                      key={idx}
                      file={file}
                      onRemove={() => removeFile(idx)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Context & Rubric */}
          <div className="space-y-10">
            <AssignmentTypeToggle
              assignmentType={assignmentType}
              setAssignmentType={setAssignmentType}
            />

            <ContextInputs
              problemStatement={problemStatement}
              setProblemStatement={setProblemStatement}
              rubricSource={rubricSource}
              setRubricSource={setRubricSource}
              rubricText={rubricText}
              setRubricText={setRubricText}
              rubricFile={rubricFile}
              setRubricFile={setRubricFile}
              rubricInputRef={rubricInputRef}
              handleRubricFileSelect={handleRubricFileSelect}
            />
          </div>
        </div>

        {/* Action Bar */}
        <div className="pt-10 border-t border-slate-800/50">
          <div className="bg-slate-900/60 backdrop-blur-2xl border border-slate-700/30 rounded-3xl p-5 shadow-2xl flex items-center justify-between gap-6 max-w-3xl mx-auto">
            <button
              type="button"
              disabled={loading}
              onClick={() => {
                setFiles([])
                setProblemStatement('')
                setRubricText('')
                setRubricFile(null)
                setErrors([])
                if (fileInputRef.current) fileInputRef.current.value = ''
                if (rubricInputRef.current) rubricInputRef.current.value = ''
              }}
              className="px-8 py-3 rounded-2xl text-xs font-black uppercase tracking-[0.15em] text-slate-500 hover:text-white hover:bg-slate-800/80 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Reset Terminal
            </button>
            <button
              type="submit"
              disabled={loading || files.length === 0}
              className="flex-1 px-10 py-4 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white text-xs font-black uppercase tracking-[0.2em] rounded-2xl shadow-[0_0_30px_rgba(99,102,241,0.2)] transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-3"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Syncing Results...</span>
                </>
              ) : (
                <>
                  <span>Initialize Evaluation</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}

'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import FileUpload, { type FileUploadData } from '@/components/FileUpload'
import { ResultsStore, type EvaluationResponse } from '@/lib/results-store'

const API_BASE_URL = 'http://127.0.0.1:8000'

export default function UploadPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'info' | 'success' | 'error'>('info')

  const handleFileUploadSubmit = async (data: FileUploadData) => {
    setLoading(true)
    setMessage('Establishing secure link to evaluation engine...')
    setMessageType('info')

    try {
      const formData = new FormData()
      data.files.forEach((file) => {
        formData.append('files', file)
      })

      formData.append('assignment_type', data.assignmentType)

      if (data.problemStatement) {
        formData.append('problem_statement', data.problemStatement)
      }

      if (data.rubric) {
        formData.append('rubric_content', data.rubric)
      }

      const res = await fetch(`${API_BASE_URL}/api/evaluate`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(
          errorData.detail || `Network error: ${res.status}`
        )
      }

      const result: EvaluationResponse = await res.json()

      if (result.status === 'success') {
        ResultsStore.setResults(result)
        setMessage(`SUCCESS: Synchronized ${result.summary?.total_submissions || 0} evaluations.`)
        setMessageType('success')
        setTimeout(() => {
          router.push('/results')
        }, 800)
      } else {
        setMessage(`CRIT: Evaluation protocol failure.`)
        setMessageType('error')
      }
    } catch (error) {
      setMessage(`ERROR: System offline or malformed payload.`)
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-obsidian bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/10 via-obsidian to-obsidian relative overflow-hidden">
      
      {/* Dynamic Background Accents */}
      <div className="absolute top-0 left-0 w-full h-screen pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-indigo-500/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-5%] w-[40%] h-[40%] bg-purple-600/5 rounded-full blur-[100px]" />
      </div>

      {/* Navigation */}
      <nav className="glass-edge backdrop-blur-3xl sticky top-0 z-50 bg-obsidian/40 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-8 py-5 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-[0_0_20px_rgba(99,102,241,0.3)] group-hover:scale-105 transition-all">
              <span className="text-white font-black text-xl italic tracking-tighter">E</span>
            </div>
            <span className="text-xl font-bold text-white/90 group-hover:text-white transition-colors uppercase tracking-[0.1em] font-space-grotesk">
              Evaluator 2.0
            </span>
          </Link>
          <div className="flex items-center gap-10">
            <Link href="/upload" className="text-indigo-400 font-black text-xs uppercase tracking-[0.2em] relative after:absolute after:bottom-[-4px] after:left-0 after:w-full after:h-0.5 after:bg-indigo-400 after:rounded-full">
              Upload
            </Link>
            <Link href="/results" className="text-white/40 hover:text-white/80 transition-all font-black text-xs uppercase tracking-[0.2em]">
              Results
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-8 py-20 relative z-10 font-inter">
        <div className="mb-20 text-center max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/5 border border-indigo-500/10 mb-2">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-300/80 font-space-grotesk">Evaluation Interface V2.0</span>
          </div>
          <h1 className="text-6xl md:text-7xl font-black text-white leading-[1.1] tracking-tighter">
            Submit Your <span className="text-indigo-400 drop-shadow-[0_0_15px_rgba(129,140,248,0.3)]">Submissions</span>
          </h1>
          <p className="text-lg text-slate-400 leading-relaxed font-medium">
            AI-powered semantic evaluation. Upload student payloads and establish rubric parameters 
            to begin deep-reasoning multi-agent critique.
          </p>
        </div>

        {/* Message Banner */}
        {message && (
          <div className={`max-w-4xl mx-auto mb-12 p-6 rounded-3xl border backdrop-blur-2xl flex items-center justify-between gap-4 animate-slide-up shadow-2xl ${messageType === 'success'
            ? 'bg-emerald-trust/5 border-emerald-trust/20 text-emerald-trust'
            : messageType === 'error'
              ? 'bg-red-500/5 border-red-500/20 text-red-300'
              : 'bg-indigo-500/5 border-indigo-500/20 text-indigo-300'
            }`}>
            <div className="flex items-center gap-4">
               <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-lg ${messageType === 'success' ? 'bg-emerald-trust/10' : messageType === 'error' ? 'bg-red-500/10' : 'bg-indigo-500/10'}`}>
                {messageType === 'success' ? '✓' : messageType === 'error' ? '!' : 'i'}
              </div>
              <p className="font-black text-xs uppercase tracking-[0.1em]">{message}</p>
            </div>
          </div>
        )}

        {/* Main Upload Component */}
        <div className="animate-fade-in delay-200">
           <FileUpload
            onSubmit={handleFileUploadSubmit}
            loading={loading}
          />
        </div>

        {/* Decorative Grid Background (subtle) */}
        <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-[-1]" 
             style={{ backgroundImage: `radial-gradient(#6366f1 1px, transparent 1px)`, backgroundSize: '40px 40px' }} />
      </div>
    </main>
  )
}

'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { ResultsStore } from '@/lib/results-store'
import type { EvaluationResponse } from '@/lib/results-store'
import { ResultsDashboard } from '@/components/results/ResultsDashboard'
import { ResultCard } from '@/components/results/ResultCard'

interface StudentResult {
  id: string
  name: string
  score: number
  maxScore: number
  percentage: number
  feedback: string[]
  type: string
}

export default function ResultsPage() {
  const [results, setResults] = useState<StudentResult[]>([])
  const [apiResponse, setApiResponse] = useState<EvaluationResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load results from storage
    const storedResults = ResultsStore.getResults()

    if (storedResults && storedResults.status === 'success' && storedResults.results) {
      setApiResponse(storedResults)

      const formattedResults: StudentResult[] = storedResults.results.map(
        (result, idx) => ({
          id: String(idx),
          name: result.submission_id,
          score: result.final_score,
          maxScore: result.max_score,
          percentage: result.percentage,
          feedback: result.feedback,
          type: result.assignment_type
        })
      )

      setResults(formattedResults)
    } else {
      // Placeholder if no results
      setResults([])
    }
    setLoading(false)
  }, [])

  const averagePercentage = 
    results.length > 0
      ? results.reduce((sum, r) => sum + r.percentage, 0) / results.length
      : 0

  const highestPercentage = 
    results.length > 0
      ? Math.max(...results.map(r => r.percentage))
      : 0

  const lowestPercentage = 
    results.length > 0
      ? Math.min(...results.map(r => r.percentage))
      : 0

  if (loading) {
     return (
        <div className="min-h-screen bg-obsidian flex items-center justify-center">
            <div className="w-16 h-1 w-64 bg-slate-900 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 animate-slide-left-right" />
            </div>
        </div>
     )
  }

  return (
    <main className="min-h-screen bg-obsidian bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/10 via-obsidian to-obsidian relative overflow-hidden">
      
      {/* Dynamic Background Accents */}
      <div className="absolute top-0 right-0 w-full h-[150vh] pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[-25%] right-[-15%] w-[60%] h-[60%] bg-indigo-500/10 rounded-full blur-[140px]" />
        <div className="absolute top-[20%] left-[-10%] w-[40%] h-[40%] bg-purple-600/5 rounded-full blur-[100px]" />
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
            <Link href="/upload" className="text-white/40 hover:text-white/80 transition-all font-black text-xs uppercase tracking-[0.2em] font-space-grotesk">
              Upload
            </Link>
            <Link href="/results" className="text-indigo-400 font-black text-xs uppercase tracking-[0.2em] relative after:absolute after:bottom-[-4px] after:left-0 after:w-full after:h-0.5 after:bg-indigo-400 after:rounded-full font-space-grotesk">
              Results
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-8 py-20 relative z-10">
        
        <div className="flex flex-col md:flex-row justify-between items-end gap-10 mb-20 animate-fade-in font-inter">
          <div className="max-w-3xl space-y-4">
             <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-trust/5 border border-emerald-trust/10 mb-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-trust animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-trust/80 font-space-grotesk">Real-time Analysis Complete</span>
            </div>
            <h1 className="text-6xl md:text-7xl font-black text-white leading-tight tracking-tighter shadow-[0_0_40px_rgba(255,255,255,0.05)]">
              Protocol <span className="text-indigo-400">Results</span>
            </h1>
            <p className="text-xl text-slate-400 font-medium leading-relaxed max-w-xl">
              Consult the deep-reasoning critique data and performance benchmarks synthesized from your academic payloads.
            </p>
          </div>
          
           {results.length > 0 && (
             <div className="flex gap-4 mb-2">
               <Link
                href="/upload"
                className="px-8 py-4 bg-slate-900/60 border border-slate-700/50 hover:border-indigo-500/50 text-white text-[10px] font-black uppercase tracking-[0.2em] rounded-2xl transition-all font-space-grotesk"
               >
                 Flush & Re-init
               </Link>
               {apiResponse?.csv_output_path && (
                <a
                  href={apiResponse.csv_output_path}
                  download
                  className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] font-black uppercase tracking-[0.2em] rounded-2xl transition-all shadow-[0_0_20px_rgba(99,102,241,0.2)] font-space-grotesk"
                >
                  Download Summary Manifest
                </a>
               )}
             </div>
           )}
        </div>

        {results.length > 0 ? (
          <>
            <ResultsDashboard
              total={results.length}
              average={`${averagePercentage.toFixed(1)}%`}
              highest={`${highestPercentage.toFixed(1)}%`}
              lowest={`${lowestPercentage.toFixed(1)}%`}
            />

            <div className="space-y-4 font-space-grotesk">
              <p className="text-xs font-black text-slate-500 uppercase tracking-[0.3em] mb-4 ml-2">Classroom Performance Grid</p>
              <div className="animate-fade-in delay-200">
                {results.map((result) => (
                  <ResultCard
                    key={result.id}
                    name={result.name}
                    score={result.score}
                    maxScore={result.maxScore}
                    percentage={result.percentage}
                    feedback={result.feedback}
                    type={result.type}
                  />
                ))}
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-40 animate-fade-in space-y-10">
             <div className="w-32 h-32 bg-slate-950/50 rounded-full border-2 border-slate-900 mx-auto flex items-center justify-center text-5xl">
                ⛓️
             </div>
             <div className="space-y-4">
               <h2 className="text-4xl font-black text-white/50 tracking-tighter">No Protocol Data Found</h2>
               <p className="text-slate-500 font-medium max-w-sm mx-auto">Please initialize an evaluation session in the Upload Terminal before consulting results.</p>
             </div>
             <Link
              href="/upload"
              className="inline-block px-12 py-5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-black uppercase tracking-[0.2em] rounded-3xl transition-all shadow-2xl font-space-grotesk hover:scale-105 active:scale-95"
            >
              Open Upload Terminal
            </Link>
          </div>
        )}
      </div>
      
      {/* Decorative Grid Background */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-[-1]" 
           style={{ backgroundImage: `radial-gradient(#6366f1 1px, transparent 1px)`, backgroundSize: '40px 40px' }} />
    </main>
  )
}

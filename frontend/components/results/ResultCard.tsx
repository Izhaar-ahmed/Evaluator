'use client'

import React, { useState } from 'react'

interface ResultCardProps {
  name: string
  score: number
  maxScore: number
  percentage: number
  feedback: string[]
  type: string
}

export const ResultCard: React.FC<ResultCardProps> = ({
  name,
  score,
  maxScore,
  percentage,
  feedback,
  type
}) => {
  const [expanded, setExpanded] = useState(false)

  const getPerformanceColor = (p: number) => {
    if (p >= 90) return 'text-emerald-trust border-emerald-trust/20 bg-emerald-trust/5 shadow-[0_0_20px_rgba(16,185,129,0.15)]'
    if (p >= 80) return 'text-indigo-400 border-indigo-500/20 bg-indigo-500/5 shadow-[0_0_20px_rgba(99,102,241,0.15)]'
    if (p >= 70) return 'text-amber-400 border-amber-500/20 bg-amber-500/5 shadow-[0_0_20px_rgba(245,158,11,0.15)]'
    return 'text-red-400 border-red-500/20 bg-red-400/5 shadow-[0_0_20px_rgba(248,113,113,0.15)]'
  }

  const getRailColor = (p: number) => {
    if (p >= 90) return 'bg-emerald-trust'
    if (p >= 80) return 'bg-indigo-500'
    if (p >= 70) return 'bg-amber-500'
    return 'bg-red-500'
  }

  return (
    <div className={`bg-slate-900/40 backdrop-blur-3xl border border-slate-700/30 rounded-3xl p-8 mb-6 shadow-2xl transition-all duration-500 hover:border-indigo-500/30 font-inter`}>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-3 px-4 py-1.5 rounded-full bg-slate-950 border border-slate-800 animate-fade-in">
             <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
             <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 font-space-grotesk">{type || 'submission'} Protocol</span>
          </div>
          <h3 className="text-3xl font-black text-white leading-tight tracking-tighter">
            {name}
          </h3>
        </div>
        
        <div className="text-right flex items-center md:flex-col gap-6 md:gap-2">
          <span className={`text-5xl font-black tracking-tighter ${getPerformanceColor(percentage).split(' ')[0]}`}>
            {percentage.toFixed(0)}%
          </span>
          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 font-space-grotesk">
            {score.toFixed(1)} / {maxScore} points
          </p>
        </div>
      </div>

      {/* High-Fidelity Progress Rail */}
      <div className="mb-10 group relative">
        <div className="h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800/50">
          <div
            style={{ width: `${percentage}%` }}
            className={`h-full transition-all duration-1000 ease-out rounded-full relative ${getRailColor(percentage)} shadow-[0_0_20px_rgba(99,102,241,0.5)]`}
          >
            <div className="absolute top-0 right-0 w-8 h-full bg-white/20 animate-pulse animate-duration-[2000ms]" />
          </div>
        </div>
        {/* Rail Benchmarks */}
        <div className="absolute top-[-10px] left-1/2 w-px h-7 bg-slate-700/50 z-0" />
        <div className="absolute top-[-10px] left-[80%] w-px h-7 bg-indigo-500/30 z-0" />
      </div>

      {/* Critique Panel Toggle */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between gap-4 p-5 bg-slate-950/50 rounded-2xl border border-slate-800 hover:border-indigo-500/30 transition-all group font-space-grotesk"
      >
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.674a1 1 0 00.908-.588l3.358-7.659a1 1 0 00-.908-1.523H4.405a1 1 0 00-.908 1.523l3.358 7.659a1 1 0 00.908.588z" />
            </svg>
          </div>
          <span className="text-xs font-black uppercase tracking-[0.2em] text-slate-400 group-hover:text-white transition-colors">
            {expanded ? 'Hide Machine Intelligence Report' : 'Consult Critique Consensus'}
          </span>
        </div>
        <svg className={`w-5 h-5 text-slate-500 transition-transform duration-500 ${expanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expandable Content reached via Fira Code or standard Sans */}
      {expanded && (
        <div className="mt-6 p-8 bg-slate-950/80 rounded-2xl border border-indigo-500/10 animate-slide-up">
           <div className="grid gap-6">
            {feedback.map((item, idx) => (
              <div key={idx} className="flex gap-6 group/item">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/5 flex items-center justify-center flex-shrink-0 text-indigo-500/40 font-black text-xs font-space-grotesk group-hover/item:text-indigo-400 transition-colors">
                  0{idx + 1}
                </div>
                <p className="text-sm text-slate-400/90 leading-relaxed font-mono">
                  {item}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

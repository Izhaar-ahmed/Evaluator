'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import AppNavbar from '@/components/AppNavbar'

interface PerformanceMetric {
  label: string
  value: number
  color: string
}

export default function StudentProfilePage() {
  const { id } = useParams()
  const [loading, setLoading] = useState(true)

  const fetchStudentData = async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/students/${id}/history`)
      if (res.ok) {
        // Data loaded successfully - could be used to populate dynamic content
        await res.json()
      }
    } catch {
      // Backend may not be running - use fallback data
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStudentData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const metrics: PerformanceMetric[] = [
    { label: 'Algorithm Efficiency', value: 88, color: 'bg-violet-primary' },
    { label: 'Code Structure', value: 92, color: 'bg-violet-primary' },
    { label: 'Content Alignment', value: 75, color: 'bg-violet-container' },
    { label: 'Syntax Accuracy', value: 98, color: 'bg-emerald-trust' },
    { label: 'Problem Solving', value: 81, color: 'bg-violet-container' },
  ]

  const barHeights = ['40%', '45%', '42%', '55%', '65%', '60%', '75%', '82%', '78%', '92%']

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-violet-primary/30 border-t-violet-primary rounded-full animate-spin" />
          <p className="text-sm text-frost-muted">Loading student data...</p>
        </div>
      </div>
    )
  }

  const displayId = typeof id === 'string' ? id : id?.[0] || 'unknown'

  return (
    <div className="min-h-screen bg-background text-frost flex flex-col">
      <AppNavbar />

      <main className="flex-1 max-w-[1440px] mx-auto w-full px-8 py-10">
        {/* Back link */}
        <Link href="/results" className="inline-flex items-center gap-1 text-sm text-frost-muted hover:text-violet-primary transition-colors mb-6">
          <span className="material-symbols-outlined text-[18px]">arrow_back</span>
          Back to Results
        </Link>

        {/* Header */}
        <section className="mb-10">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div>
              <span className="text-xs font-medium text-violet-primary mb-1 block">{displayId}</span>
              <h1 className="text-4xl font-bold text-frost tracking-tight mb-2">
                Student Performance
              </h1>
              <p className="text-frost-muted text-base">
                Track academic trajectory and skill progression over time.
              </p>
            </div>
          </div>
        </section>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">

          {/* Historical Trend Chart */}
          <div className="md:col-span-8 bg-surface-container-low rounded-xl border border-outline-variant/10 p-6 overflow-hidden">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-lg font-semibold text-frost">Performance Trend</h3>
                <p className="text-xs text-frost-muted mt-1">Last 10 submissions</p>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-trust/10 rounded-full border border-emerald-trust/20">
                <div className="w-2 h-2 rounded-full bg-emerald-trust animate-pulse" />
                <span className="text-emerald-trust text-xs font-medium">Improving</span>
              </div>
            </div>

            <div className="h-56 w-full flex items-end justify-between gap-2 relative">
              {/* SVG trend line */}
              <svg className="absolute inset-0 w-full h-full opacity-40" preserveAspectRatio="none" viewBox="0 0 1000 200">
                <defs>
                  <linearGradient id="line-grad" x1="0%" x2="100%" y1="0%" y2="0%">
                    <stop offset="0%" style={{stopColor: '#8083ff', stopOpacity: 0.2}} />
                    <stop offset="100%" style={{stopColor: '#c0c1ff', stopOpacity: 1}} />
                  </linearGradient>
                </defs>
                <path d="M0,180 L100,160 L200,170 L300,140 L400,120 L500,130 L600,90 L700,70 L800,80 L900,40 L1000,30" fill="none" stroke="url(#line-grad)" strokeWidth="3" />
              </svg>

              {/* Bars */}
              <div className="w-full h-full flex items-end justify-between px-2 relative z-10">
                {barHeights.map((h, i) => (
                  <div
                    key={i}
                    className={`w-full max-w-[32px] rounded-t transition-all duration-500 ${
                      i >= 7
                        ? 'bg-violet-primary/60 shadow-[0_0_10px_rgba(192,193,255,0.3)]'
                        : 'bg-surface-container-highest/80'
                    }`}
                    style={{ height: h }}
                  >
                    {i === 9 && (
                      <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-violet-primary text-obsidian text-[10px] font-bold px-2 py-0.5 rounded font-mono whitespace-nowrap">
                        94%
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Class Rank Card */}
          <div className="md:col-span-4 bg-gradient-to-br from-violet-container to-primary-dim rounded-xl p-6 flex flex-col justify-between relative overflow-hidden shadow-lg">
            <div className="absolute top-0 right-0 p-3 opacity-10">
              <span className="material-symbols-outlined text-8xl">workspace_premium</span>
            </div>
            <div className="relative z-10">
              <h3 className="text-lg font-semibold text-white/90">Class Rank</h3>
              <p className="text-xs text-white/60 mt-1">Overall percentile</p>
            </div>
            <div className="relative z-10 py-6">
              <div className="text-6xl font-bold tracking-tight text-white">84th</div>
              <p className="text-lg font-medium text-white/80">Percentile</p>
            </div>
            <div className="relative z-10 flex items-center gap-2">
              <span className="material-symbols-outlined text-white/80 text-[18px]">trending_up</span>
              <span className="text-xs text-white/70 font-medium">+4% since last evaluation</span>
            </div>
          </div>

          {/* Skill Radar */}
          <div className="md:col-span-6 bg-surface-container-low rounded-xl border border-outline-variant/10 p-6">
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-frost">Skill Breakdown</h3>
              <p className="text-xs text-frost-muted mt-1">Competency across evaluation dimensions</p>
            </div>
            <div className="space-y-5">
              {metrics.map((metric) => (
                <div className="group" key={metric.label}>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-frost">{metric.label}</span>
                    <span className="text-sm font-mono text-violet-primary font-medium">{(metric.value / 10).toFixed(1)}/10</span>
                  </div>
                  <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
                    <div
                      style={{ width: `${metric.value}%` }}
                      className={`h-full ${metric.color} rounded-full transition-all duration-500 group-hover:brightness-110`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Academic Transcript */}
          <div className="md:col-span-6 bg-surface-container-low rounded-xl border border-outline-variant/10 overflow-hidden flex flex-col">
            <div className="p-6 border-b border-outline-variant/10 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold text-frost">Academic Summary</h3>
                <p className="text-xs text-frost-muted mt-1">ID: {displayId.split('-')[0]}</p>
              </div>
              <button className="flex items-center gap-2 bg-surface-container-high hover:bg-surface-container-highest text-frost px-4 py-2 border border-outline-variant/10 rounded-lg transition-all text-xs font-medium">
                <span className="material-symbols-outlined text-[16px]">download</span>
                Export
              </button>
            </div>
            <div className="p-6 flex-grow grid grid-cols-2 gap-6">
              <div>
                <p className="text-xs text-frost-muted mb-1">Cumulative Grade</p>
                <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-primary to-violet-container">A-</div>
              </div>
              <div>
                <p className="text-xs text-frost-muted mb-1">GPA Equivalent</p>
                <div className="text-5xl font-bold text-frost">3.88</div>
              </div>
              <div className="col-span-2 p-5 bg-surface-container-lowest border border-outline-variant/10 rounded-xl flex items-center gap-5">
                <div className="w-14 h-14 bg-gradient-to-tr from-amber-400 to-amber-500 rounded-full flex items-center justify-center shrink-0 shadow-lg">
                  <span className="material-symbols-outlined text-obsidian text-2xl">workspace_premium</span>
                </div>
                <div>
                  <h4 className="font-semibold text-frost">Top 10% Achievement</h4>
                  <p className="text-sm text-frost-muted">Outstanding performance in algorithmic complexity and logical reasoning.</p>
                </div>
              </div>
            </div>
            <div className="px-6 py-3 bg-surface-container-highest/30 text-[10px] text-frost-muted flex justify-between">
              <span>Generated: {new Date().toISOString().split('T')[0]}</span>
              <span>Evaluator 2.0</span>
            </div>
          </div>

        </div>
      </main>

      {/* Subtle background pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.015] z-[-1]"
        style={{ backgroundImage: `radial-gradient(#c0c1ff 1px, transparent 1px)`, backgroundSize: '32px 32px' }} />
    </div>
  )
}

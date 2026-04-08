'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { ResultsStore } from '@/lib/results-store'
import type { EvaluationResult } from '@/lib/results-store'
import { ResultCard } from '@/components/results/ResultCard'
import AppNavbar from '@/components/AppNavbar'

export default function ResultsPage() {
  const [results, setResults] = useState<EvaluationResult[]>([])
  const [latestCsv, setLatestCsv] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const { results: historyResults, batches } = await ResultsStore.fetchHistory()

        if (historyResults.length > 0) {
          setResults(historyResults)
          // Get CSV from latest batch
          if (batches.length > 0 && batches[0].csv_output_path) {
            setLatestCsv(batches[0].csv_output_path)
          }
        } else {
          // Fall back to session storage for latest evaluation
          const session = ResultsStore.getResults()
          if (session?.status === 'success' && session.results) {
            setResults(session.results)
            if (session.csv_output_path) {
              setLatestCsv(session.csv_output_path)
            }
          }
        }
      } catch {
        // Last resort: session storage
        const session = ResultsStore.getResults()
        if (session?.status === 'success' && session.results) {
          setResults(session.results)
        }
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const averagePercentage =
    results.length > 0
      ? results.reduce((sum, r) => sum + r.percentage, 0) / results.length
      : 0

  const totalIntegrityFlags =
    results.reduce((count, r) => count + (r.flag_reasons?.length || 0), 0)

  const uniqueStudents = new Set(results.map(r => r.submission_id)).size

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-violet-primary/30 border-t-violet-primary rounded-full animate-spin" />
          <p className="text-sm text-frost-muted">Loading results...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-frost flex flex-col">
      <AppNavbar />

      <main className="flex-1 max-w-[1440px] mx-auto w-full px-8 py-10">
        {/* Page Header */}
        <section className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-10">
          <div>
            <h1 className="text-4xl font-bold text-frost tracking-tight mb-2">
              Results Dashboard
            </h1>
            <p className="text-frost-muted text-base">
              {results.length > 0
                ? `${results.length} evaluation${results.length !== 1 ? 's' : ''} across ${uniqueStudents} student${uniqueStudents !== 1 ? 's' : ''}`
                : 'View evaluation results and performance analytics.'}
            </p>
          </div>
          {results.length > 0 && (
            <div className="flex gap-3">
              <Link
                href="/upload"
                className="px-5 py-2.5 bg-surface-container-high border border-outline-variant/20 text-sm font-medium text-frost rounded-lg hover:bg-surface-container-highest transition-all"
              >
                New Evaluation
              </Link>
              {latestCsv && (
                <a
                  href={latestCsv}
                  download
                  className="px-5 py-2.5 bg-gradient-to-r from-violet-primary to-violet-container text-obsidian text-sm font-semibold rounded-lg hover:opacity-90 transition-all shadow-violet flex items-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">download</span>
                  Export CSV
                </a>
              )}
            </div>
          )}
        </section>

        {results.length > 0 ? (
          <>
            {/* Summary Metrics */}
            <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
              {/* Average Score */}
              <div className="bg-surface-container-low rounded-xl border border-outline-variant/10 p-6 hover:border-outline-variant/20 transition-all">
                <p className="text-xs font-semibold uppercase tracking-wider text-frost-muted mb-3">Average Score</p>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-bold font-mono text-violet-primary">{averagePercentage.toFixed(1)}</span>
                  <span className="text-lg text-frost-muted">/100</span>
                </div>
                <div className="mt-4 h-1.5 w-full bg-surface-container-highest rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-violet-primary to-violet-container rounded-full transition-all duration-500" style={{ width: `${averagePercentage}%` }} />
                </div>
              </div>

              {/* Total Evaluations */}
              <div className="bg-surface-container-low rounded-xl border border-outline-variant/10 p-6 hover:border-outline-variant/20 transition-all">
                <p className="text-xs font-semibold uppercase tracking-wider text-frost-muted mb-3">Total Evaluations</p>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-bold font-mono text-emerald-trust">{results.length}</span>
                </div>
                <p className="mt-3 text-xs text-frost-muted">{uniqueStudents} unique student{uniqueStudents !== 1 ? 's' : ''} evaluated</p>
              </div>

              {/* Integrity Alerts */}
              <div className="bg-surface-container-low rounded-xl border border-outline-variant/10 p-6 hover:border-outline-variant/20 transition-all">
                <p className="text-xs font-semibold uppercase tracking-wider text-frost-muted mb-3">Integrity Alerts</p>
                <div className="flex items-baseline gap-1">
                  <span className={`text-4xl font-bold font-mono ${totalIntegrityFlags > 0 ? 'text-coral' : 'text-emerald-trust'}`}>
                    {totalIntegrityFlags}
                  </span>
                </div>
                <p className="mt-3 text-xs text-frost-muted">
                  {totalIntegrityFlags === 0 ? 'No concerns detected' : `${totalIntegrityFlags} submission${totalIntegrityFlags > 1 ? 's' : ''} flagged`}
                </p>
              </div>
            </section>

            {/* Results List */}
            <section>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-semibold text-frost">All Evaluation Results</h2>
                <span className="text-xs text-frost-muted">{results.length} result{results.length !== 1 ? 's' : ''}</span>
              </div>
              <div className="space-y-3">
                {results.map((result, idx) => (
                  <ResultCard
                    key={`${result.submission_id}-${result.batch_id || idx}-${idx}`}
                    index={idx + 1}
                    name={result.submission_id}
                    percentage={result.percentage}
                    feedback={result.feedback}
                    flag_score={result.flag_score}
                    flag_reasons={result.flag_reasons}
                    percentile={result.percentile}
                    improvement_delta={result.improvement_delta}
                    trend={result.trend}
                  />
                ))}
              </div>
            </section>
          </>
        ) : (
          /* Empty State */
          <div className="text-center py-24 animate-fade-in">
            <div className="w-20 h-20 bg-surface-container-low rounded-2xl mx-auto flex items-center justify-center mb-6 border border-outline-variant/10">
              <span className="material-symbols-outlined text-4xl text-frost-muted">folder_off</span>
            </div>
            <h2 className="text-xl font-semibold text-frost mb-2">No results yet</h2>
            <p className="text-frost-muted mb-6">Upload student submissions to see evaluation results here.</p>
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-primary to-violet-container text-obsidian font-semibold rounded-lg hover:opacity-90 transition-all shadow-violet"
            >
              <span className="material-symbols-outlined text-[18px]">upload</span>
              Upload Submissions
            </Link>
          </div>
        )}
      </main>

      {/* Subtle background pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.015] z-[-1]"
        style={{ backgroundImage: `radial-gradient(#c0c1ff 1px, transparent 1px)`, backgroundSize: '32px 32px' }} />
    </div>
  )
}

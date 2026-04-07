'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import AppNavbar from '@/components/AppNavbar'

interface ReviewItem {
  id: string
  submission_id: string
  score: number
  reasoning: string
  status: 'PENDING' | 'RESOLVED'
  created_at: string
  assignment_type: string
  student_id: string
}

export default function ReviewQueuePage() {
  const [reviews, setReviews] = useState<ReviewItem[]>([])
  const [selectedReview, setSelectedReview] = useState<ReviewItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [overrideScore, setOverrideScore] = useState<number>(0)
  const [teacherNotes, setTeacherNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const fetchReviews = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/reviews?status=pending')
      if (res.ok) {
        const data = await res.json()
        setReviews(data.reviews || [])
        if (data.reviews && data.reviews.length > 0) {
          setSelectedReview(data.reviews[0])
          setOverrideScore(data.reviews[0].score || 0)
        }
      }
    } catch {
      // Backend may not be running
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReviews()
  }, [])

  const handleOverride = async () => {
    if (!selectedReview) return
    setIsSubmitting(true)
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/reviews/${selectedReview.id}/override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ teacher_score: overrideScore, teacher_notes: teacherNotes || 'Manual override' })
      })
      if (res.ok) {
        const remaining = reviews.filter(r => r.id !== selectedReview.id)
        setReviews(remaining)
        setSelectedReview(remaining[0] || null)
        setTeacherNotes('')
        if (remaining[0]) {
          setOverrideScore(remaining[0].score || 0)
        }
      }
    } catch {
      // Handle silently
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-violet-primary/30 border-t-violet-primary rounded-full animate-spin" />
          <p className="text-sm text-frost-muted">Loading review queue...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-frost flex flex-col">
      <AppNavbar />

      {reviews.length === 0 ? (
        /* Empty State */
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-6 animate-fade-in">
            <div className="w-20 h-20 bg-emerald-trust/10 rounded-2xl mx-auto flex items-center justify-center border border-emerald-trust/20">
              <span className="material-symbols-outlined text-4xl text-emerald-trust">verified_user</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-frost mb-2">All Clear</h2>
              <p className="text-frost-muted max-w-md">
                No pending reviews. All submissions have been processed and verified.
              </p>
            </div>
            <Link
              href="/results"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-primary to-violet-container text-obsidian font-semibold rounded-lg hover:opacity-90 transition-all shadow-violet"
            >
              Go to Results
            </Link>
          </div>
        </div>
      ) : (
        /* Split Layout */
        <div className="flex flex-1 overflow-hidden" style={{ height: 'calc(100vh - 64px)' }}>
          {/* Left Panel: Review List */}
          <aside className="w-[380px] border-r border-outline-variant/10 bg-surface-container-low overflow-y-auto scrollbar-thin flex-shrink-0">
            <div className="p-5 border-b border-outline-variant/10 flex items-center justify-between sticky top-0 bg-surface-container-low z-10">
              <h3 className="text-sm font-semibold text-frost">Pending Reviews</h3>
              <span className="px-2 py-0.5 bg-violet-primary/10 text-violet-primary text-xs font-medium rounded-full">
                {reviews.length}
              </span>
            </div>

            <div>
              {reviews.map(review => (
                <button
                  key={review.id}
                  onClick={() => {
                    setSelectedReview(review)
                    setOverrideScore(review.score || 0)
                    setTeacherNotes('')
                  }}
                  className={`w-full p-5 text-left transition-all border-b border-outline-variant/5 ${
                    selectedReview?.id === review.id
                      ? 'bg-violet-primary/5 border-l-2 border-l-violet-primary'
                      : 'hover:bg-surface-container-high/30'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-sm font-medium text-frost truncate mr-2">{review.submission_id}</span>
                    <span className={`text-lg font-bold font-mono ${review.score < 50 ? 'text-coral' : 'text-frost'}`}>
                      {(review.score ?? 0).toFixed(0)}
                    </span>
                  </div>
                  <p className="text-xs text-frost-muted line-clamp-2 leading-relaxed">
                    {review.reasoning}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-coral/10 text-coral border border-coral/20">
                      {review.assignment_type || 'Code'}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </aside>

          {/* Right Panel: Review Details */}
          <div className="flex-1 bg-background p-8 overflow-y-auto">
            {selectedReview ? (
              <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex justify-between items-start">
                  <div>
                    <h1 className="text-2xl font-bold text-frost mb-1">Review Details</h1>
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-medium px-2.5 py-1 rounded-md bg-surface-container-high border border-outline-variant/10 text-frost-muted">
                        {selectedReview.submission_id}
                      </span>
                      <span className="text-xs font-medium px-2.5 py-1 rounded-md bg-surface-container-high border border-outline-variant/10 text-frost-muted">
                        {selectedReview.assignment_type || 'Code'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                  {/* Evidence & Reasoning */}
                  <div className="lg:col-span-7 space-y-6">
                    {/* Code Evidence */}
                    <div className="bg-surface-container-low rounded-xl border border-outline-variant/10 overflow-hidden">
                      <div className="px-5 py-3 border-b border-outline-variant/10 flex justify-between items-center">
                        <span className="text-xs font-semibold text-frost-muted uppercase tracking-wider">Student Submission</span>
                        <span className="text-[10px] text-coral font-medium">Flagged Region</span>
                      </div>
                      <div className="bg-surface-container-lowest p-5 font-mono text-xs leading-relaxed overflow-x-auto">
                        <pre className="text-frost-muted"><span className="text-violet-container">def</span> <span className="text-violet-primary">process_payload</span>(data):{'\n'}    <span className="text-emerald-trust"># Structural analysis</span>{'\n'}    hash_val = <span className="text-violet-primary">md5</span>(data.raw){'\n'}    <span className="text-coral/80 bg-coral/5 border-l-2 border-coral px-2 block my-1">result = [x * 1.05 for x in hash_val]</span>    <span className="text-violet-container">return</span> result</pre>
                      </div>
                    </div>

                    {/* AI Reasoning */}
                    <div className="bg-surface-container-low rounded-xl border border-outline-variant/10 p-5">
                      <div className="flex items-center gap-2 mb-4">
                        <span className="material-symbols-outlined text-[18px] text-emerald-trust">psychology</span>
                        <span className="text-xs font-semibold uppercase tracking-wider text-frost-muted">AI Analysis</span>
                      </div>
                      <div className="text-sm text-frost/80 leading-relaxed">
                        {selectedReview.reasoning}
                      </div>
                    </div>
                  </div>

                  {/* Score Override */}
                  <div className="lg:col-span-5">
                    <div className="bg-surface-container-low rounded-xl border border-outline-variant/10 p-6 sticky top-8">
                      <h3 className="text-xs font-semibold uppercase tracking-wider text-frost-muted mb-6">Manual Score Adjustment</h3>

                      <div className="text-center mb-6">
                        <span className="text-6xl font-bold font-mono text-transparent bg-clip-text bg-gradient-to-r from-violet-primary to-violet-container">
                          {overrideScore}
                        </span>
                        <span className="text-lg text-frost-muted ml-1">/100</span>
                      </div>

                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={overrideScore}
                        onChange={(e) => setOverrideScore(parseInt(e.target.value))}
                        className="w-full mb-2"
                      />
                      <div className="flex justify-between text-[10px] text-frost-muted mb-6">
                        <span>0</span>
                        <span>50</span>
                        <span>100</span>
                      </div>

                      <div className="space-y-2 mb-6">
                        <label className="text-xs font-semibold text-frost-muted">Teacher Notes</label>
                        <textarea
                          value={teacherNotes}
                          onChange={(e) => setTeacherNotes(e.target.value)}
                          className="w-full h-[100px] bg-surface-container-lowest border border-outline-variant/20 rounded-lg text-sm p-4 text-frost focus:ring-2 focus:ring-violet-primary/40 focus:border-violet-primary/60 outline-none transition-all placeholder:text-frost-muted/40 resize-none"
                          placeholder="Add justification for this score..."
                        />
                      </div>

                      <button
                        onClick={handleOverride}
                        disabled={isSubmitting}
                        className="w-full bg-gradient-to-r from-violet-primary to-violet-container hover:opacity-90 active:scale-[0.98] transition-all rounded-lg font-semibold text-sm py-3.5 text-obsidian shadow-violet disabled:opacity-50"
                      >
                        {isSubmitting ? 'Submitting...' : 'Submit Override'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-frost-muted">
                Select a review from the list
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

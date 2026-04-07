'use client'

export interface EvaluationResponse {
  status: string
  message: string
  results?: Array<{
    submission_id: string
    final_score: number
    max_score: number
    percentage: number
    feedback: string[]
    assignment_type: string
    file: string
    // --- Integrity fields (Feature 4) ---
    flag_score?: number
    flag_reasons?: string[]
    // --- Student profile fields (Feature 6) ---
    percentile?: number
    improvement_delta?: number
    trend?: string
  }>
  summary?: {
    total_submissions: number
    average_score: number
    average_percentage: number
    highest_score: number
    lowest_score: number
  }
  csv_output_path?: string
  csv_detailed_output_path?: string
  error_message?: string
}

const STORAGE_KEY = 'evaluation_results'

export const ResultsStore = {
  setResults: (results: EvaluationResponse) => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(results))
    }
  },

  getResults: (): EvaluationResponse | null => {
    if (typeof window !== 'undefined') {
      const data = sessionStorage.getItem(STORAGE_KEY)
      return data ? JSON.parse(data) : null
    }
    return null
  },

  clearResults: () => {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(STORAGE_KEY)
    }
  },
}

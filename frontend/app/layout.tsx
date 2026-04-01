import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Evaluator 2.0 | Intelligent AI-Powered Academic Assessment',
  description: 'Automate rigorous academic grading with our proprietary multi-agent approach. Conditional Scoring, Strict Relevance Checks, and LLM-powered feedback.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        {children}
      </body>
    </html>
  )
}

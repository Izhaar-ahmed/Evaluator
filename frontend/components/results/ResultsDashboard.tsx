'use client'

import React from 'react'

interface StatsCardProps {
  label: string
  value: string | number
  color: 'indigo' | 'emerald' | 'coral' | 'amber'
  icon: string
}

const StatsCard: React.FC<StatsCardProps> = ({ label, value, color, icon }) => {
  const colorMap = {
    indigo: 'from-indigo-600/20 to-indigo-900/10 border-indigo-500/20 text-indigo-400',
    emerald: 'from-emerald-500/20 to-emerald-900/10 border-emerald-500/20 text-emerald-400',
    coral: 'from-red-500/20 to-red-900/10 border-red-500/20 text-red-400',
    amber: 'from-amber-500/20 to-amber-900/10 border-amber-500/20 text-amber-400'
  }

  return (
    <div className={`bg-gradient-to-br ${colorMap[color]} backdrop-blur-2xl border rounded-3xl p-8 shadow-2xl transition-all hover:scale-[1.02] duration-500`}>
      <div className="flex items-center justify-between mb-4">
        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">{label}</p>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-5xl font-black tracking-tighter">{value}</p>
    </div>
  )
}

interface ResultsDashboardProps {
  total: number | string
  average: number | string
  highest: number | string
  lowest: number | string
}

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({
  total,
  average,
  highest,
  lowest
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16 animate-slide-up">
      <StatsCard label="Total Submissions" value={total} color="indigo" icon="📊" />
      <StatsCard label="Average Performance" value={average} color="amber" icon="📈" />
      <StatsCard label="Global Peak" value={highest} color="emerald" icon="🏆" />
      <StatsCard label="Critical Floor" value={lowest} color="coral" icon="⚠" />
    </div>
  )
}

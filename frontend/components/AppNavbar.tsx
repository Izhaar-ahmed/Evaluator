'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navLinks = [
  { href: '/upload', label: 'Upload' },
  { href: '/results', label: 'Results' },
  { href: '/review', label: 'Review Queue' },
]

export default function AppNavbar() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 w-full z-50 bg-obsidian/80 backdrop-blur-xl border-b border-outline-variant/10">
      <nav className="flex justify-between items-center px-8 h-16 max-w-[1440px] mx-auto">
        <div className="flex items-center gap-8">
          <Link href="/" className="font-inter font-extrabold text-xl tracking-tight text-frost">
            Evaluator 2.0
          </Link>
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const isActive = pathname === link.href || pathname?.startsWith(link.href + '/')
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'text-violet-primary bg-violet-primary/10'
                      : 'text-frost-muted hover:text-frost hover:bg-surface-container-high/50'
                  }`}
                >
                  {link.label}
                </Link>
              )
            })}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button className="p-2 text-frost-muted hover:text-violet-primary transition-colors rounded-lg hover:bg-surface-container-high/50">
            <span className="material-symbols-outlined text-[20px]">notifications</span>
          </button>
          <button className="p-2 text-frost-muted hover:text-violet-primary transition-colors rounded-lg hover:bg-surface-container-high/50">
            <span className="material-symbols-outlined text-[20px]">settings</span>
          </button>
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-primary to-violet-container flex items-center justify-center text-xs font-bold text-obsidian ml-2">
            T
          </div>
        </div>
      </nav>
    </header>
  )
}

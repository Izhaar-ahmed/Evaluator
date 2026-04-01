import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Obsidian Scholar Design System
        obsidian: '#0b1326',
        'obsidian-deep': '#060e20',
        'obsidian-light': '#131b2e',
        'slate-surface': '#171f33',
        'slate-surface-high': '#222a3d',
        'slate-surface-highest': '#2d3449',
        'slate-surface-bright': '#31394d',
        violet: {
          primary: '#c0c1ff',
          container: '#8083ff',
          fixed: '#e1e0ff',
          dim: '#c0c1ff',
          deep: '#6366F1',
        },
        'emerald-trust': '#4edea3',
        'emerald-trust-container': '#00a572',
        coral: '#ffb2b7',
        'coral-container': '#ff516a',
        frost: '#dae2fd',
        'frost-muted': '#c7c4d7',
        'frost-steel': '#908fa0',
        ghost: '#464554',
      },
      fontFamily: {
        inter: ['Inter', 'system-ui', 'sans-serif'],
        grotesk: ['Space Grotesk', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glow: {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '0.8' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out forwards',
        'slide-up': 'slideUp 0.6s ease-out forwards',
        'slide-down': 'slideDown 0.4s ease-out forwards',
        'glow': 'glow 3s ease-in-out infinite',
        'float': 'float 4s ease-in-out infinite',
        'shimmer': 'shimmer 3s linear infinite',
      },
      backgroundImage: {
        'violet-gradient': 'linear-gradient(135deg, #c0c1ff, #8083ff)',
        'hero-glow': 'radial-gradient(ellipse at center, rgba(99, 102, 241, 0.15) 0%, transparent 70%)',
      },
      boxShadow: {
        'violet-glow': '0 0 20px rgba(99, 102, 241, 0.3)',
        'violet-glow-lg': '0 0 40px rgba(99, 102, 241, 0.2)',
        'ambient': '0px 20px 40px rgba(7, 0, 108, 0.15)',
      },
    },
  },
  plugins: [],
}
export default config

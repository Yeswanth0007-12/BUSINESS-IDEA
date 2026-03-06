/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme colors with WCAG AA contrast ratios
        background: '#0f172a',      // slate-900
        surface: '#1e293b',          // slate-800
        'surface-light': '#334155',  // slate-700
        primary: '#3b82f6',          // blue-500
        'primary-dark': '#2563eb',   // blue-600
        'primary-light': '#60a5fa',  // blue-400
        secondary: '#64748b',        // slate-500
        accent: '#10b981',           // green-500
        'accent-dark': '#059669',    // green-600
        danger: '#ef4444',           // red-500
        'danger-dark': '#dc2626',    // red-600
        warning: '#f59e0b',          // amber-500
        text: '#f1f5f9',             // slate-100 - WCAG AA on dark bg
        'text-secondary': '#cbd5e1', // slate-300 - WCAG AA on dark bg
        'text-muted': '#94a3b8',     // slate-400
        border: '#334155',           // slate-700
        'border-light': '#475569',   // slate-600
      },
      boxShadow: {
        'dark-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
        'dark-md': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
        'dark-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
        'dark-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
      },
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cybersecurity SOC theme
        'soc-dark': '#0f172a',
        'soc-darker': '#0a0e27',
        'soc-accent': '#3b82f6',
        'soc-accent-dark': '#1e40af',
        'soc-success': '#10b981',
        'soc-warning': '#f59e0b',
        'soc-danger': '#ef4444',
        'soc-critical': '#dc2626',
        'soc-info': '#06b6d4',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      boxShadow: {
        'soc': '0 4px 6px rgba(0, 0, 0, 0.5)',
        'soc-lg': '0 20px 25px rgba(0, 0, 0, 0.6)',
      },
    },
  },
  plugins: [
    require('tailwind-scrollbar'),
  ],
}

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        legal: {
          25: '#fefefe',
          50: '#f8f9ff',
          100: '#f1f4ff',
          200: '#e4e7ff',
          300: '#c7cdff',
          400: '#a5acff',
          500: '#8288ff',
          600: '#667eea',
          700: '#5a67d8',
          800: '#4c51bf',
          900: '#3c366b',
        },
        justice: {
          25: '#fcfdfe',
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
      },
    },
  },
  plugins: [],
}

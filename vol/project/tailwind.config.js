/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'crypto-dark': '#0d1421',
        'crypto-card': '#1a2332',
        'crypto-border': '#2d3748',
        'crypto-green': '#10b981',
        'crypto-red': '#ef4444',
        'crypto-blue': '#3b82f6',
      }
    },
  },
  plugins: [],
}
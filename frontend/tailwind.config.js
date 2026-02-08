/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable dark mode with class strategy
  theme: {
    extend: {
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
      },
      boxShadow: {
        'neon': '0 0 5px rgba(51, 255, 255, 0.3), 0 0 10px rgba(51, 255, 255, 0.2)',
        'neon-lg': '0 0 10px rgba(51, 255, 255, 0.5), 0 0 20px rgba(51, 255, 255, 0.3)',
        'neon-purple': '0 0 5px rgba(187, 134, 252, 0.3), 0 0 10px rgba(187, 134, 252, 0.2)',
        'neon-purple-lg': '0 0 10px rgba(187, 134, 252, 0.5), 0 0 20px rgba(187, 134, 252, 0.3)',
      },
      animation: {
        'pulse-neon': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}

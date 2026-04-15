/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'agentpay-green': '#00ff88',
        'agentpay-dark': '#0a0a0a',
        'agentpay-card': '#111111',
        'agentpay-border': '#222222',
      },
    },
  },
  plugins: [],
}
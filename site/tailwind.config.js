/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        amphora: '#171310',
        papyrus: '#F2E7D5',
        terracotta: '#C45A3C',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'sans-serif'],
        display: ['Georgia', 'Times New Roman', 'serif'],
        mono: ['Cascadia Code', 'SFMono-Regular', 'monospace'],
      },
    },
  },
  plugins: [],
}

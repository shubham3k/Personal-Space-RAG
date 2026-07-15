/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#070A13',
        surface: 'rgba(17, 24, 39, 0.7)',
        surfaceMuted: 'rgba(31, 41, 55, 0.4)',
        primary: '#FFC174',      // primary amber-fixed-dim
        secondary: '#D0BCFF',    // secondary light purple
        tertiary: '#54DDFC',     // tertiary cyan
        onSurface: '#F0E0D1',
        onSurfaceMuted: '#A08E7A',
        outline: '#534434',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        display: ['Space Grotesk', 'sans-serif'],
        cyber: ['Orbitron', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

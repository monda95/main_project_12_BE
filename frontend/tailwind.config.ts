import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#22d3ee',
          secondary: '#818cf8',
          accent: '#fcd34d'
        }
      },
      boxShadow: {
        glow: '0 0 30px rgba(34, 211, 238, 0.35)'
      }
    }
  },
  plugins: []
};

export default config;

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // 主色：深蓝 + 白 + 绿（打卡成功色）
        navy: {
          50: '#eef2f9',
          100: '#d6e0f0',
          200: '#adc1e1',
          300: '#7f9ecf',
          400: '#4f79b8',
          500: '#2d5c9e',
          600: '#214d86',
          700: '#1a3d6b',
          800: '#142f53',
          900: '#0e2340',
        },
        ricegreen: {
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
        },
      },
    },
  },
  plugins: [],
}

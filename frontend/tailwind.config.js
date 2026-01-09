/** @type {import('tailwindcss').Config} */
export default {
  // 重点检查这一行！
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}', // 必须包含 .vue 后缀！
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

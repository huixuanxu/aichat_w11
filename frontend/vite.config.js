import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 🌟 Vite 設定檔
export default defineConfig({
  plugins: [react()],

  // ✅ 一定要是 '/'
  // Vercel 需要用「絕對路徑」載入資源
  base: '/',
})

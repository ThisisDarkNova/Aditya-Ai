import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './', // Output relative paths for OBS local file usage
  build: {
    outDir: 'dist',
  }
})

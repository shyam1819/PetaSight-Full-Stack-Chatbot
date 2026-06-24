import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// publicDir is disabled so the repo's existing public/ (brief + review/) is
// never copied into the build output and never served on the live URL.
export default defineConfig({
  plugins: [react()],
  publicDir: false,
})

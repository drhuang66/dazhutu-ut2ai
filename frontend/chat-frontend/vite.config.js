import { create } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})

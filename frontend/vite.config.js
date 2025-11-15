// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // server: {
  //   port: 5173, // Specify your development server port[citation:6]
  //   proxy: {
  //     // Configure a proxy to resolve CORS issues
  //     '/api': {
  //       target: 'http://localhost:8000',
  //       changeOrigin: true,
  //       secure: false,
  //     }
  //   }
  // }
})
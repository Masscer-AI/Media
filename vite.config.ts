import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: './client',
  envDir: './',
  define: {
    //polifil to avoid process from being undefined
    'process.env': {
      environment: "DEV"
    }
  },
  build: {
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        entryFileNames: 'assets/bundle.js',
        // chunkFileNames: 'bundle.js',
        // assetFileNames: 'bundle.[ext]'
      }
    }
  },
  server: {
    
  }
})

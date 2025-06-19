import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/run': 'http://localhost:8080', // proxy POST /run calls to Flask
        }
    }
});

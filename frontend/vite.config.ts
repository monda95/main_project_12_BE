import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    server: {
      port: Number(env.VITE_DEV_SERVER_PORT ?? 5173),
      host: true
    },
    build: {
      sourcemap: true,
      outDir: 'dist',
      emptyOutDir: true
    }
  };
});

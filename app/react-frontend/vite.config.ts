import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 開発時: python-backend をローカルで `python app.py` (port 5001) で起動しておく
const BACKEND_URL = "http://localhost:5001";

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: true,
    proxy: {
      "/api": {
        target: BACKEND_URL,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  plugins: [react()],
});

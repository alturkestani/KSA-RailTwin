// Adapted from TrafficTwin Jeddah web/vite.config.ts (Apache-2.0); see NOTICE.
import { defineConfig } from "vite";

// API target for the dev server: VITE_API_TARGET, else localhost:8000 (uv run uvicorn api.main:app).
const target = process.env.VITE_API_TARGET || "http://localhost:8000";

export default defineConfig({
  // React via esbuild's automatic JSX runtime (no plugin needed).
  esbuild: { jsx: "automatic" },
  server: {
    port: 5173,
    proxy: { "/api": { target, changeOrigin: true }, "/health": { target, changeOrigin: true } },
  },
  preview: {
    proxy: { "/api": { target, changeOrigin: true }, "/health": { target, changeOrigin: true } },
  },
  build: { chunkSizeWarningLimit: 3000, sourcemap: false },
});

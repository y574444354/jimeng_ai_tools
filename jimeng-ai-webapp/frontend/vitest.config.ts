import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'text-summary', 'lcov'],
      include: ['src/**/*.ts', 'src/**/*.vue'],
      exclude: [
        'src/__tests__/**',
        'src/**/*.spec.ts',
        'src/main.ts',
        'src/env.d.ts',
      ],
      // 全局阈值设为 0（当前处于测试补齐阶段，新模块实际覆盖率高）
      // 新增模块目标：lines >= 80%, functions >= 80%, branches >= 50%
      thresholds: {
        lines: 0,
        branches: 0,
        functions: 0,
        statements: 0,
      },
    },
  },
})

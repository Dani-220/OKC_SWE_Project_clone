import { defineConfig } from 'vitest/config';

// Unit tests for framework-free logic (e.g. src/app/_models). Run with `npm test`.
export default defineConfig({
  test: {
    include: ['src/**/*.spec.ts'],
  },
});

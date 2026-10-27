import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import globals from 'globals';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    ignores: ['dist/', 'node_modules/', 'scripts/*.js', 'vitest.config.ts', 'eslint.config.mjs'],
  },
  {
    // Scripts and node:test suites run on Node
    files: ['**/*.mjs'],
    languageOptions: { globals: globals.node },
  },
);

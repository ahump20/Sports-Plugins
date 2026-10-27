import eslint from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.mjs', '**/*.js'],
    languageOptions: { globals: globals.node },
  },
  {
    ignores: ['dist/', 'node_modules/', 'scripts/*.js', 'vitest.config.ts', 'eslint.config.mjs'],
  },
);

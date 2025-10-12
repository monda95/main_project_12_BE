import js from '@eslint/js';
import pluginReactHooks from 'eslint-plugin-react-hooks';
import pluginReactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    ignores: ['dist', 'coverage'],
    plugins: {
      'react-hooks': pluginReactHooks,
      'react-refresh': pluginReactRefresh
    },
    rules: {
      ...pluginReactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      'no-console': ['warn', { allow: ['warn', 'error'] }]
    }
  }
);

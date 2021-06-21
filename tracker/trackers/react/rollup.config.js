import commonjs from '@rollup/plugin-commonjs';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import cleanup from 'rollup-plugin-cleanup';
import filesize from 'rollup-plugin-filesize';
import peerDepsExternal from 'rollup-plugin-peer-deps-external';
import sizes from 'rollup-plugin-sizes';
import { terser } from 'rollup-plugin-terser';
import ts from 'rollup-plugin-ts';

const commonPlugins = [peerDepsExternal(), nodeResolve(), commonjs(), ts()];
const minificationPlugins = [cleanup(), terser()];
const statsPlugins = [sizes(), filesize()];

const makeOutput = (isMinified) => ({
  file: `dist/index${isMinified ? '.min' : ''}.js`,
  format: 'es',
  name: 'ObjectivReactTracker',
  sourcemap: true,
  globals: {
    react: 'React',
    'react/jsx-runtime': 'jsxRuntime',
  },
});

export default [
  // ES
  {
    input: './src/index.ts',
    output: [makeOutput(false)],
    plugins: [...commonPlugins, ...statsPlugins],
  },

  // ES minified
  {
    input: './src/index.ts',
    output: [makeOutput(true)],
    plugins: [...commonPlugins, ...minificationPlugins, ...statsPlugins],
  },
];

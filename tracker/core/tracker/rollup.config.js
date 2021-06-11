import commonjs from '@rollup/plugin-commonjs';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import ts from '@wessberg/rollup-plugin-ts'; // Official plugin crashes: https://github.com/rollup/plugins/issues/287
import cleanup from 'rollup-plugin-cleanup';
import filesize from 'rollup-plugin-filesize';
import sizes from 'rollup-plugin-sizes';
import { terser } from 'rollup-plugin-terser';

const commonPlugins = [nodeResolve(), commonjs(), ts()];
const minificationPlugins = [cleanup(), terser()];
const statsPlugins = [sizes(), filesize()];

const makeOutput = (format, isMinified, isDefault) => ({
  file: `dist/index${!isDefault ? `.${format}` : ''}${isMinified ? '.min' : ''}.js`,
  format: format,
  name: 'objectiv',
  sourcemap: true,
});

export default [
  // UMD, CJS, ES, IIFE
  {
    input: './src/index.ts',
    output: [makeOutput('umd', false, true), makeOutput('cjs'), makeOutput('es'), makeOutput('iife')],
    plugins: [...commonPlugins, ...statsPlugins],
  },

  // UMD, CJS, ES, IIFE - minified
  {
    input: './src/index.ts',
    output: [makeOutput('umd', true, true), makeOutput('cjs', true), makeOutput('es', true), makeOutput('iife', true)],
    plugins: [...commonPlugins, ...minificationPlugins, ...statsPlugins],
  },
];

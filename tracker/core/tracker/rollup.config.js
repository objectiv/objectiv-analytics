import commonjs from '@rollup/plugin-commonjs';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import filesize from 'rollup-plugin-filesize';
import sizes from 'rollup-plugin-sizes';
import { terser } from 'rollup-plugin-terser';
import ts from 'rollup-plugin-ts';

export default [
  {
    input: './src/index.ts',
    output: [
      {
        file: `dist/index.js`,
        format: 'esm',
        sourcemap: true,
      },
    ],
    plugins: [nodeResolve({ browser: true }), commonjs(), ts(), terser(), sizes(), filesize()],
  },
];

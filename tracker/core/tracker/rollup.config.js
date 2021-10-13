import commonjs from '@rollup/plugin-commonjs';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import filesize from 'rollup-plugin-filesize';
import sizes from 'rollup-plugin-sizes';
import { terser } from 'rollup-plugin-terser';
import ts from 'rollup-plugin-ts';

const dev = process.env.dev === 'true';
console.log(`Build type: ${dev ? 'dev' : 'production'}`);

export default [
  {
    input: './src/index.ts',
    output: [
      {
        file: `dist/index.js`,
        format: 'esm',
        sourcemap: dev,
      },
    ],
    plugins: [nodeResolve({ browser: true }), commonjs(), ts(), ...(dev ? [] : [terser()]), sizes(), filesize()],
  },
];

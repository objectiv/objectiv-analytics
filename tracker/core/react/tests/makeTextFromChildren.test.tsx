/*
 * Copyright 2021 Objectiv B.V.
 */

import { ReactNode } from 'react';
import { makeTextFromChildren } from '../src';

describe('makeTextFromChildren', () => {
  // setting output to `null` means expecting `makeTextFromChildren` to throw
  const testCases: [input: ReactNode, output: string | null][] = [
    [undefined, null],
    [null, null],
    [false, null],
    [true, null],
    [[], null],
    [{}, null],
    ['', null],

    [0, '0'],
    [123, '123'],
    [456.12, '456.12'],
    [['test', 456.12, 'abc'], 'test 456.12 abc'],
    [<div>what?</div>, 'what?'],
    [
      <div>
        <span>yes!</span>
      </div>,
      'yes!',
    ],
    [
      <div>
        <img alt={'orly?'} />
        <span>NOPE</span>
      </div>,
      'NOPE',
    ],
  ];

  testCases.forEach(([input, output]) =>
    it(`'${JSON.stringify(input)}' -> '${output === null ? 'throw' : JSON.stringify(output)}'`, () => {
      if (output === null) {
        expect(() => makeTextFromChildren(input)).toThrow(
          'Could not infer any text from children nodes. Please provide one manually.'
        );
      } else {
        expect(makeTextFromChildren(input)).toBe(output);
      }
    })
  );
});

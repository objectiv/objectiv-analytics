/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromTrackedAnchorProps } from '../src';

describe('makeIdFromTrackedAnchorProps', () => {
  const testCases: [input: {}, output: string | null][] = [
    [{}, null],
    [{ id: 'test' }, 'test'],
    [{ id: 'Click Me' }, 'Click Me'],
    [{ objectiv: { contextId: 'test' } }, 'test'],
    [{ objectiv: { contextId: 'Click Me' } }, 'Click Me'],
    [{ title: 'test' }, 'test'],
    [{ title: 'Click Me' }, 'click-me'],
    [{ children: 'test' }, 'test'],
    [{ children: 'Click Me' }, 'click-me'],
  ];

  testCases.forEach(([input, output]) =>
    it(`${JSON.stringify(input)} -> ${JSON.stringify(output)}`, () => {
      expect(makeIdFromTrackedAnchorProps(input)).toBe(output);
    })
  );
});

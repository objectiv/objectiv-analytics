/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromTrackedAnchorProps } from '../src';

describe('makeIdFromTrackedAnchorProps', () => {
  const testCases: [input: {}, output: string | null][] = [
    [{}, null],
    [{ id: 'test' }, 'test'],
    [{ id: 'Click Me' }, 'click-me'],
    [{ id: 'Click Me', normalizeId: false }, 'Click Me'],
    [{ contextId: 'test' }, 'test'],
    [{ contextId: 'Click Me' }, 'click-me'],
    [{ contextId: 'Click Me', normalizeId: false }, 'Click Me'],
    [{ title: 'test' }, 'test'],
    [{ title: 'Click Me' }, 'click-me'],
    [{ title: 'Click Me', normalizeId: false }, 'Click Me'],
    [{ children: 'test' }, 'test'],
    [{ children: 'Click Me' }, 'click-me'],
    [{ children: 'Click Me', normalizeId: false }, 'Click Me'],
  ];

  testCases.forEach(([input, output]) =>
    it(`${JSON.stringify(input)} -> ${JSON.stringify(output)}`, () => {
      expect(makeIdFromTrackedAnchorProps(input)).toBe(output);
    })
  );
});

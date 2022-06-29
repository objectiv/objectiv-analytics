/*
 * Copyright 2021-2022 Objectiv B.V.
 * @jest-environment node
 */

import { expectToThrow } from '@objectiv/testing-tools';
import { LocalStorageQueueStore } from '../src';

describe('Without DOM', () => {
  it('should throw if LocalStorageQueueStore gets constructed', async () => {
    expectToThrow(
      () => new LocalStorageQueueStore({ trackerId: 'app-id' }),
      'LocalStorageQueueStore: failed to initialize: localStorage is not available.'
    );
  });
});

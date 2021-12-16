/*
 * Copyright 2021 Objectiv B.V.
 * @jest-environment node
 */

import { TrackerQueueLocalStorage } from '../src';

describe('Without DOM', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should throw if TrackerQueueLocalStorage gets constructed', async () => {
    expect(() => new TrackerQueueLocalStorage({ trackerId: 'app-id' })).toThrow(
      'TrackerQueueLocalStorage: failed to initialize: window.localStorage is not available.'
    );
  });
});

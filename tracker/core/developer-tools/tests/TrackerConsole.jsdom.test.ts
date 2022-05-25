/*
 * Copyright 2022 Objectiv B.V.
 * @jest-environment jsdom
 */

import { NoopConsoleImplementation } from '../src/NoopConsoleImplementation';
import { TrackerConsole } from '../src/TrackerConsole';

describe('TrackerConsole', () => {
  it('should default to console', () => {
    jest.spyOn(NoopConsoleImplementation, 'log');
    jest.spyOn(console, 'log');
    TrackerConsole.log('should log to console');

    expect(console.log).toHaveBeenCalledTimes(1);
    expect(console.log).toHaveBeenCalledWith('should log to console');
    expect(NoopConsoleImplementation.log).not.toHaveBeenCalled();
  });
});

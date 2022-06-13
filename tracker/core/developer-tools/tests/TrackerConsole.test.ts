/*
 * Copyright 2022 Objectiv B.V.
 */

import { NoopConsoleImplementation } from '../src/NoopConsoleImplementation';
import { TrackerConsole } from '../src/TrackerConsole';

describe('TrackerConsole', () => {
  it('should return undefined', () => {
    TrackerConsole.setImplementation(NoopConsoleImplementation);
    expect(TrackerConsole.debug()).toBe(undefined);
    expect(TrackerConsole.error()).toBe(undefined);
    expect(TrackerConsole.group()).toBe(undefined);
    expect(TrackerConsole.groupCollapsed()).toBe(undefined);
    expect(TrackerConsole.groupEnd()).toBe(undefined);
    expect(TrackerConsole.info()).toBe(undefined);
    expect(TrackerConsole.log()).toBe(undefined);
    expect(TrackerConsole.warn()).toBe(undefined);
  });

  describe('env sensitive logic', () => {
    beforeEach(() => {
      jest.resetModules();
      jest.resetAllMocks();
      jest.spyOn(NoopConsoleImplementation, 'log');
      jest.spyOn(console, 'log');
    });

    it('TrackerConsole should automatically use NoopConsole when not in development', () => {
      TrackerConsole.log('should log to NoopConsole');

      expect(NoopConsoleImplementation.log).toHaveBeenCalledTimes(1);
      expect(NoopConsoleImplementation.log).toHaveBeenCalledWith('should log to NoopConsole');
      expect(console.log).not.toHaveBeenCalled();
    });
  });
});

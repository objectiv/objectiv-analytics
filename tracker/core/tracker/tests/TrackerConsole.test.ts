import { NoopConsole } from '../src';

describe('TrackerConsole', () => {
  it('should return undefined', () => {
    expect(NoopConsole.debug()).toBe(undefined);
    expect(NoopConsole.error()).toBe(undefined);
    expect(NoopConsole.group()).toBe(undefined);
    expect(NoopConsole.groupCollapsed()).toBe(undefined);
    expect(NoopConsole.groupEnd()).toBe(undefined);
    expect(NoopConsole.info()).toBe(undefined);
    expect(NoopConsole.log()).toBe(undefined);
    expect(NoopConsole.warn()).toBe(undefined);
  });
});

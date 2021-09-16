import { ApplicationContextPlugin, ContextsConfig, Tracker, TrackerEvent, TrackerPlugins } from '../src';

describe('ApplicationContextPlugin', () => {
  it('should generate a DeviceContext when constructed', () => {
    const testWebDeviceContextPlugin = new ApplicationContextPlugin({ applicationId: 'app-id' });
    expect(testWebDeviceContextPlugin.applicationContext).toEqual({
      __global_context: true,
      _type: 'ApplicationContext',
      id: 'app-id',
    });
  });

  it('should add the ApplicationContext to the Event when `beforeTransport` is executed by the Tracker', async () => {
    const plugins = new ApplicationContextPlugin({ applicationId: 'app-id' });
    const testTracker = new Tracker({ applicationId: 'app-id', plugins: new TrackerPlugins([plugins]) });
    const eventContexts: ContextsConfig = {
      global_contexts: [
        { __global_context: true, _type: 'section', id: 'X' },
        { __global_context: true, _type: 'section', id: 'Y' },
      ],
    };
    const testEvent = new TrackerEvent({ _type: 'test-event', ...eventContexts });
    expect(testEvent.global_contexts).toHaveLength(2);
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(3);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __global_context: true,
          _type: 'ApplicationContext',
          id: 'app-id',
        },
      ])
    );
  });
});

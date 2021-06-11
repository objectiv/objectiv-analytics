import { WebDocumentContextPlugin } from '../src';
import { ContextsConfig, Tracker, TrackerEvent, TrackerPlugins } from '@objectiv/tracker-core';
import { SpyTransport } from './mocks/SpyTransport';

const EXPECTED_URL_CHANGED_EVENT = {
  _interactive_event: false,
  event: 'URLChangedEvent',
  globalContexts: [],
  locationStack: [
    {
      _location_context: true,
      _section_context: true,
      _context_type: 'WebDocumentContext',
      id: '#document',
      url: 'http://localhost/',
    },
  ],
};

describe('WebDocumentContextPlugin', () => {
  it('should instantiate without specifying an ID at construction', () => {
    const testWebDocumentContextPlugin = new WebDocumentContextPlugin();
    expect(testWebDocumentContextPlugin.documentContextId).toBe(document.nodeName);
  });

  it('should instantiate with a custom ID at construction', () => {
    const customDocumentId = 'CustomId';
    const testWebDocumentContextPlugin = new WebDocumentContextPlugin({ documentContextId: customDocumentId });
    expect(testWebDocumentContextPlugin.documentContextId).toBe(customDocumentId);
  });

  it('should add the WebDocumentContext to the Event when `beforeTransport` is executed by the Tracker', () => {
    const testTracker = new Tracker({ plugins: new TrackerPlugins([WebDocumentContextPlugin]) });
    const eventContexts: ContextsConfig = {
      locationStack: [
        { _location_context: true, _context_type: 'section', id: 'A' },
        { _location_context: true, _context_type: 'section', id: 'B' },
      ],
    };
    const testEvent = new TrackerEvent({ event: 'test-event', ...eventContexts });
    expect(testEvent.locationStack).toHaveLength(2);
    const trackedEvent = testTracker.trackEvent(testEvent);
    expect(trackedEvent.locationStack).toHaveLength(3);
    expect(trackedEvent.locationStack).toEqual(
      expect.arrayContaining([
        {
          _location_context: true,
          _section_context: true,
          _context_type: 'WebDocumentContext',
          id: '#document',
          url: 'http://localhost/',
        },
      ])
    );
  });

  it('should automatically trigger URLChangedEvents in response to the History API', () => {
    const spyTransport = new SpyTransport();
    spyOn(spyTransport, 'handle');

    new Tracker({ transport: spyTransport, plugins: new TrackerPlugins([WebDocumentContextPlugin]) });

    expect(window.history).toHaveLength(1);

    /**
     * NOTE: In all these tests the WebDocumentContext url attribute is fixed to 'http://localhost/'.
     * It's a JSDOM bug: https://github.com/facebook/jest/issues/890
     * We can assume that eventually it will be fixed and that our WebDocumentContext will be correctly reported.
     */

    window.history.pushState({ page: 1 }, 'title 1', '/page1?page=1');
    expect(window.history).toHaveLength(2);
    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_URL_CHANGED_EVENT);

    window.history.pushState({ page: 2 }, 'title 2', '/page2?page=2');
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(2);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_URL_CHANGED_EVENT);

    window.history.replaceState({ page: 3 }, 'title 3', '?page=3');
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(3);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_URL_CHANGED_EVENT);

    window.history.replaceState({ page: 1 }, 'title1', '?page=1');
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(4);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_URL_CHANGED_EVENT);

    window.history.go(1);
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(5);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_URL_CHANGED_EVENT);

    window.history.back();
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(6);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_URL_CHANGED_EVENT);

    window.history.forward();
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(7);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_URL_CHANGED_EVENT);
  });
});

import { trackURLChangedEvent } from '../src';
import { makeWebDocumentContext, Tracker } from '@objectiv/tracker-core';
import { SpyTransport } from './mocks/SpyTransport';

const EXPECTED_DECORATED_URL_CHANGED_EVENT = {
  _interactive_event: false,
  event: 'URLChangedEvent',
  globalContexts: [],
  locationStack: [
    {
      _location_context: true,
      _section_context: true,
      _context_type: 'WebDocumentContext',
      id: '#document',
      url: '/test',
    },
  ],
};

describe('URLChangedEvent', () => {
  it('should trigger on all History API methods', () => {
    const spyTransport = new SpyTransport();
    spyOn(spyTransport, 'handle');

    // Create a test tracker and spy on its `trackEvent` method
    const testTracker = new Tracker({
      locationStack: [
        makeWebDocumentContext({
          id: '#document',
          url: '/test',
        }),
      ],
      transport: spyTransport,
    });

    // Start tracking `popstate` events
    trackURLChangedEvent(testTracker);

    // Make sure our current history is clean (always has an initial entry, thus we start from 1)
    expect(window.history).toHaveLength(1);

    window.history.pushState({ page: 1 }, 'title 1', '?page=1');
    expect(window.history).toHaveLength(2);
    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_DECORATED_URL_CHANGED_EVENT);

    window.history.pushState({ page: 2 }, 'title 2', '?page=2');
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(2);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_DECORATED_URL_CHANGED_EVENT);

    window.history.replaceState({ page: 3 }, 'title 3', '?page=3');
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(3);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_DECORATED_URL_CHANGED_EVENT);

    window.history.replaceState({ page: 1 }, 'title1', '?page=1');
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(4);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_DECORATED_URL_CHANGED_EVENT);

    window.history.go(1);
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(5);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_DECORATED_URL_CHANGED_EVENT);

    window.history.back();
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(6);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_DECORATED_URL_CHANGED_EVENT);

    window.history.forward();
    expect(window.history).toHaveLength(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(7);
    expect(spyTransport.handle).toHaveBeenCalledWith(EXPECTED_DECORATED_URL_CHANGED_EVENT);
  });
});

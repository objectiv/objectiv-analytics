import { makeWebDocumentContext, Tracker } from '@objectiv/tracker-core';
import { trackDocumentLoadedEvent } from '../src/';
import { SpyTransport } from './mocks/SpyTransport';

const UUID_REGEX = /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12}$/i;

describe('WebDocumentLoadedEvent', () => {
  it('should track as expected when document has been loaded already', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');

    const testTracker = new Tracker({
      applicationId: 'app-id',
      location_stack: [
        makeWebDocumentContext({
          id: '#document',
          url: '/test',
        }),
      ],
      transport: spyTransport,
    });

    trackDocumentLoadedEvent(testTracker);

    expect(spyTransport.handle).toHaveBeenCalledWith({
      __non_interactive_event: true,
      _type: 'DocumentLoadedEvent',
      id: expect.stringMatching(UUID_REGEX),
      global_contexts: [
        {
          __global_context: true,
          _type: 'ApplicationContext',
          id: 'app-id',
        },
      ],
      location_stack: [
        {
          __location_context: true,
          __section_context: true,
          _type: 'WebDocumentContext',
          id: '#document',
          url: '/test',
        },
      ],
      time: expect.toBeNumber(),
    });
  });

  it('should track as expected when document has yet to load', async () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');

    const testTracker = new Tracker({
      applicationId: 'app-id',
      location_stack: [
        makeWebDocumentContext({
          id: '#document',
          url: '/test',
        }),
      ],
      transport: spyTransport,
    });

    // Mock readyState to be "loading"
    Object.defineProperty(document, 'readyState', {
      get() {
        return 'loading';
      },
    });

    trackDocumentLoadedEvent(testTracker);

    // Re-trigger DOMContentLoaded manually
    await window.document.dispatchEvent(
      new Event('DOMContentLoaded', {
        bubbles: true,
        cancelable: true,
      })
    );

    expect(spyTransport.handle).toHaveBeenCalledWith({
      __non_interactive_event: true,
      _type: 'DocumentLoadedEvent',
      id: expect.stringMatching(UUID_REGEX),
      global_contexts: [
        {
          __global_context: true,
          _type: 'ApplicationContext',
          id: 'app-id',
        },
      ],
      location_stack: [
        {
          __location_context: true,
          __section_context: true,
          _type: 'WebDocumentContext',
          id: '#document',
          url: '/test',
        },
      ],
      time: expect.toBeNumber(),
    });
  });
});

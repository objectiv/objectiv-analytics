import { makeWebDocumentContext, Tracker } from '@objectiv/tracker-core';
import { trackDocumentLoadedEvent } from '../src/';
import { SpyTransport } from './mocks/SpyTransport';

describe('WebDocumentLoadedEvent', () => {
  it('should track as expected when document has been loaded already', () => {
    const spyTransport = new SpyTransport();
    spyOn(spyTransport, 'handle');

    const testTracker = new Tracker({
      locationStack: [
        makeWebDocumentContext({
          id: '#document',
          url: '/test',
        }),
      ],
      transport: spyTransport,
    });

    trackDocumentLoadedEvent(testTracker);

    expect(spyTransport.handle).toHaveBeenCalledWith({
      _interactive_event: false,
      event: 'DocumentLoadedEvent',
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
    });
  });

  it('should track as expected when document has yet to load', async () => {
    const spyTransport = new SpyTransport();
    spyOn(spyTransport, 'handle');

    const testTracker = new Tracker({
      locationStack: [
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
      _interactive_event: false,
      event: 'DocumentLoadedEvent',
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
    });
  });
});

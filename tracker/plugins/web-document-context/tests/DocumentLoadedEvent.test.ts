/*
 * Copyright 2021 Objectiv B.V.
 */

import { matchUUID, SpyTransport } from '@objectiv/testing-tools';
import { makeWebDocumentContext, Tracker } from '@objectiv/tracker-core';
import { trackDocumentLoadedEvent } from '../src/';

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
      id: matchUUID,
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
    window.document.dispatchEvent(
      new Event('DOMContentLoaded', {
        bubbles: true,
        cancelable: true,
      })
    );

    expect(spyTransport.handle).toHaveBeenCalledWith({
      __non_interactive_event: true,
      _type: 'DocumentLoadedEvent',
      id: matchUUID,
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

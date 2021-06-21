import { ContextsConfig, makeDeviceContext, makeOverlayContext, makeVideoLoadEvent, TrackerEvent } from '../src';

describe('TrackerEvent', () => {
  const testEventName = 'test-event';
  const testContexts: ContextsConfig = {
    location_stack: [{ __location_context: true, _context_type: 'section', id: 'test' }],
    global_contexts: [{ __global_context: true, _context_type: 'global', id: 'test' }],
  };

  it('should instantiate with the given properties as one Config', () => {
    const testEvent = new TrackerEvent({ event: 'test-event', ...testContexts });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent.event).toBe(testEventName);
    expect(testEvent.location_stack).toEqual(testContexts.location_stack);
    expect(testEvent.global_contexts).toEqual(testContexts.global_contexts);
  });

  it('should instantiate with the given properties as multiple Configs', () => {
    const testEvent = new TrackerEvent({ event: 'test-event' }, testContexts);
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent.event).toBe(testEventName);
    expect(testEvent.location_stack).toEqual(testContexts.location_stack);
    expect(testEvent.global_contexts).toEqual(testContexts.global_contexts);
  });

  it('should instantiate without location_stack', () => {
    const testEvent = new TrackerEvent({ event: 'test-event' }, { global_contexts: testContexts.global_contexts });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent.event).toBe(testEventName);
    expect(testEvent.location_stack).toEqual([]);
    expect(testEvent.global_contexts).toEqual(testContexts.global_contexts);
  });

  it('should instantiate without global_contexts', () => {
    const testEvent = new TrackerEvent({ event: 'test-event' }, { location_stack: testContexts.location_stack });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent.event).toBe(testEventName);
    expect(testEvent.location_stack).toEqual(testContexts.location_stack);
    expect(testEvent.global_contexts).toEqual([]);
  });

  it('should allow compositions with multiple configs or instances and produce a valid location_stack', () => {
    const eventContexts: ContextsConfig = {
      location_stack: [
        { __location_context: true, _context_type: 'section', id: 'D' },
        { __location_context: true, _context_type: 'item', id: 'X' },
      ],
    };
    const sectionContexts1: ContextsConfig = {
      location_stack: [
        { __location_context: true, _context_type: 'section', id: 'root' },
        { __location_context: true, _context_type: 'section', id: 'A' },
      ],
    };
    const sectionContexts2: ContextsConfig = {
      location_stack: [
        { __location_context: true, _context_type: 'section', id: 'B' },
        { __location_context: true, _context_type: 'section', id: 'C' },
      ],
    };
    const composedEvent = new TrackerEvent(
      { event: 'test-event', ...eventContexts },
      sectionContexts1,
      sectionContexts2
    );
    expect(composedEvent.location_stack).toEqual([
      { __location_context: true, _context_type: 'section', id: 'root' },
      { __location_context: true, _context_type: 'section', id: 'A' },
      { __location_context: true, _context_type: 'section', id: 'B' },
      { __location_context: true, _context_type: 'section', id: 'C' },
      { __location_context: true, _context_type: 'section', id: 'D' },
      { __location_context: true, _context_type: 'item', id: 'X' },
    ]);
  });

  it('should serialize to JSON without discriminating properties', () => {
    const testEvent = new TrackerEvent(
      makeVideoLoadEvent({
        location_stack: [makeOverlayContext({ id: 'player' })],
        global_contexts: [makeDeviceContext({ userAgent: 'test-user-agent' })],
      })
    );
    const jsonStringEvent = JSON.stringify(testEvent, null, 2);
    expect(jsonStringEvent).toEqual(`{
  "event": "VideoLoadEvent",
  "global_contexts": [
    {
      "_context_type": "DeviceContext",
      "id": "device",
      "user-agent": "test-user-agent"
    }
  ],
  "location_stack": [
    {
      "_context_type": "OverlayContext",
      "id": "player"
    }
  ]
}`);
  });
});

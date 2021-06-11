import { ContextsConfig, TrackerEvent } from '../src';

describe('TrackerEvent', () => {
  const testEventName = 'test-event';
  const testContexts: ContextsConfig = {
    locationStack: [{ _location_context: true, _context_type: 'section', id: 'test' }],
    globalContexts: [{ _global_context: true, _context_type: 'global', id: 'test' }],
  };

  it('should instantiate with the given properties as one Config', () => {
    const testEvent = new TrackerEvent({ event: 'test-event', ...testContexts });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent.event).toBe(testEventName);
    expect(testEvent.locationStack).toEqual(testContexts.locationStack);
    expect(testEvent.globalContexts).toEqual(testContexts.globalContexts);
  });

  it('should instantiate with the given properties as multiple Configs', () => {
    const testEvent = new TrackerEvent({ event: 'test-event' }, testContexts);
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent.event).toBe(testEventName);
    expect(testEvent.locationStack).toEqual(testContexts.locationStack);
    expect(testEvent.globalContexts).toEqual(testContexts.globalContexts);
  });

  it('should instantiate without LocationStack', () => {
    const testEvent = new TrackerEvent({ event: 'test-event' }, { globalContexts: testContexts.globalContexts });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent.event).toBe(testEventName);
    expect(testEvent.locationStack).toEqual([]);
    expect(testEvent.globalContexts).toEqual(testContexts.globalContexts);
  });

  it('should instantiate without GlobalContexts', () => {
    const testEvent = new TrackerEvent({ event: 'test-event' }, { locationStack: testContexts.locationStack });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent.event).toBe(testEventName);
    expect(testEvent.locationStack).toEqual(testContexts.locationStack);
    expect(testEvent.globalContexts).toEqual([]);
  });

  it('should allow compositions with multiple configs or instances and produce a valid LocationStack', () => {
    const eventContexts: ContextsConfig = {
      locationStack: [
        { _location_context: true, _context_type: 'section', id: 'D' },
        { _location_context: true, _context_type: 'item', id: 'X' },
      ],
    };
    const sectionContexts1: ContextsConfig = {
      locationStack: [
        { _location_context: true, _context_type: 'section', id: 'root' },
        { _location_context: true, _context_type: 'section', id: 'A' },
      ],
    };
    const sectionContexts2: ContextsConfig = {
      locationStack: [
        { _location_context: true, _context_type: 'section', id: 'B' },
        { _location_context: true, _context_type: 'section', id: 'C' },
      ],
    };
    const composedEvent = new TrackerEvent(
      { event: 'test-event', ...eventContexts },
      sectionContexts1,
      sectionContexts2
    );
    expect(composedEvent.locationStack).toEqual([
      { _location_context: true, _context_type: 'section', id: 'root' },
      { _location_context: true, _context_type: 'section', id: 'A' },
      { _location_context: true, _context_type: 'section', id: 'B' },
      { _location_context: true, _context_type: 'section', id: 'C' },
      { _location_context: true, _context_type: 'section', id: 'D' },
      { _location_context: true, _context_type: 'item', id: 'X' },
    ]);
  });
});

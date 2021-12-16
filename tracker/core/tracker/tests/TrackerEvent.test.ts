/*
 * Copyright 2021 Objectiv B.V.
 */

import MockDate from 'mockdate';
import { ContextsConfig, makeApplicationContext, makeOverlayContext, makeVideoLoadEvent, TrackerEvent } from '../src';

const mockedMs = 1434319925275;

beforeEach(() => {
  MockDate.reset();
  MockDate.set(mockedMs);
});

afterEach(() => {
  MockDate.reset();
});

describe('TrackerEvent', () => {
  const testEventName = 'test-event';
  const testContexts: ContextsConfig = {
    location_stack: [{ __location_context: true, _type: 'section', id: 'test' }],
    global_contexts: [{ __global_context: true, _type: 'global', id: 'test' }],
  };

  it('should instantiate with the given properties as one Config', () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', ...testContexts });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent._type).toBe(testEventName);
    expect(testEvent.location_stack).toEqual(testContexts.location_stack);
    expect(testEvent.global_contexts).toEqual(testContexts.global_contexts);
  });

  it('should instantiate with the given properties as multiple Configs', () => {
    const testEvent = new TrackerEvent({ _type: 'test-event' }, testContexts);
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent._type).toBe(testEventName);
    expect(testEvent.location_stack).toEqual(testContexts.location_stack);
    expect(testEvent.global_contexts).toEqual(testContexts.global_contexts);
  });

  it('should instantiate without location_stack', () => {
    const testEvent = new TrackerEvent({ _type: 'test-event' }, { global_contexts: testContexts.global_contexts });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent._type).toBe(testEventName);
    expect(testEvent.location_stack).toEqual([]);
    expect(testEvent.global_contexts).toEqual(testContexts.global_contexts);
  });

  it('should instantiate without global_contexts', () => {
    const testEvent = new TrackerEvent({ _type: 'test-event' }, { location_stack: testContexts.location_stack });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent._type).toBe(testEventName);
    expect(testEvent.location_stack).toEqual(testContexts.location_stack);
    expect(testEvent.global_contexts).toEqual([]);
  });

  it('should allow compositions with multiple configs or instances and produce a valid location_stack', () => {
    const eventContexts: ContextsConfig = {
      location_stack: [
        { __location_context: true, _type: 'section', id: 'D' },
        { __location_context: true, _type: 'item', id: 'X' },
      ],
    };
    const sectionContexts1: ContextsConfig = {
      location_stack: [
        { __location_context: true, _type: 'section', id: 'root' },
        { __location_context: true, _type: 'section', id: 'A' },
      ],
    };
    const sectionContexts2: ContextsConfig = {
      location_stack: [
        { __location_context: true, _type: 'section', id: 'B' },
        { __location_context: true, _type: 'section', id: 'C' },
      ],
    };
    const composedEvent = new TrackerEvent(
      { _type: 'test-event', ...eventContexts },
      sectionContexts1,
      sectionContexts2
    );
    expect(composedEvent.location_stack).toEqual([
      { __location_context: true, _type: 'section', id: 'root' },
      { __location_context: true, _type: 'section', id: 'A' },
      { __location_context: true, _type: 'section', id: 'B' },
      { __location_context: true, _type: 'section', id: 'C' },
      { __location_context: true, _type: 'section', id: 'D' },
      { __location_context: true, _type: 'item', id: 'X' },
    ]);
  });

  it('should serialize to JSON without internal properties', () => {
    const testEvent = new TrackerEvent(
      makeVideoLoadEvent({
        location_stack: [makeOverlayContext({ id: 'player' })],
        global_contexts: [makeApplicationContext({ id: 'test-app' })],
      })
    );
    const jsonStringEvent = JSON.stringify(testEvent, null, 2);
    expect(jsonStringEvent).toEqual(`{
  "_type": "VideoLoadEvent",
  "location_stack": [
    {
      "_type": "OverlayContext",
      "id": "player"
    }
  ],
  "global_contexts": [
    {
      "_type": "ApplicationContext",
      "id": "test-app"
    }
  ],
  "id": "${testEvent.id}"
}`);
  });

  it('should clone without generating a new id', () => {
    const testEvent = new TrackerEvent({ _type: 'test-event' });
    expect(testEvent.id).not.toBeUndefined();
    const testEventClone1 = new TrackerEvent(testEvent);
    const testEventClone1_1 = new TrackerEvent(testEventClone1);
    const testEventClone1_2 = new TrackerEvent(testEventClone1_1);
    expect(testEventClone1.id).toBe(testEvent.id);
    expect(testEventClone1_1.id).toBe(testEvent.id);
    expect(testEventClone1_2.id).toBe(testEvent.id);
  });

  describe('setTime', () => {
    it('should use Date.now() when timestampMs is not provided', () => {
      const testEvent = new TrackerEvent({ _type: 'test-event' });
      expect(testEvent.time).toBeUndefined();
      testEvent.setTime();
      expect(testEvent.time).toBe(mockedMs);
    });

    it('should use whatever timestampMs is provided', () => {
      const testEvent = new TrackerEvent({ _type: 'test-event' });
      expect(testEvent.time).toBeUndefined();
      const timestampMs = 1234567890123;
      testEvent.setTime(timestampMs);
      expect(testEvent.time).toBe(timestampMs);
      expect(testEvent.time).not.toBe(mockedMs);
    });
  });
});

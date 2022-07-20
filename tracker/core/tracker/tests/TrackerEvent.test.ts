/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID } from '@objectiv/testing-tools';
import MockDate from 'mockdate';
import {
  ContextsConfig,
  generateGUID,
  makeApplicationContext,
  makeMediaLoadEvent,
  makeOverlayContext,
  TrackerEvent,
} from '../src';

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
    location_stack: [{ __instance_id: generateGUID(), __location_context: true, _type: 'section', id: 'test' }],
    global_contexts: [{ __instance_id: generateGUID(), __global_context: true, _type: 'global', id: 'test' }],
  };

  it('should instantiate with the given properties as one Config', () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', ...testContexts, id: generateGUID(), time: Date.now() });
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent._type).toBe(testEventName);
    expect(testEvent.location_stack).toEqual(testContexts.location_stack);
    expect(testEvent.global_contexts).toEqual(testContexts.global_contexts);
  });

  it('should instantiate with the given properties as multiple Configs', () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() }, testContexts);
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent._type).toBe(testEventName);
    expect(testEvent.location_stack).toEqual(testContexts.location_stack);
    expect(testEvent.global_contexts).toEqual(testContexts.global_contexts);
  });

  it('should instantiate without location_stack', () => {
    const testEvent = new TrackerEvent(
      { _type: 'test-event', id: generateGUID(), time: Date.now() },
      { global_contexts: testContexts.global_contexts }
    );
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent._type).toBe(testEventName);
    expect(testEvent.location_stack).toEqual([]);
    expect(testEvent.global_contexts).toEqual(testContexts.global_contexts);
  });

  it('should instantiate without global_contexts', () => {
    const testEvent = new TrackerEvent(
      { _type: 'test-event', id: generateGUID(), time: Date.now() },
      { location_stack: testContexts.location_stack }
    );
    expect(testEvent).toBeInstanceOf(TrackerEvent);
    expect(testEvent._type).toBe(testEventName);
    expect(testEvent.location_stack).toEqual(testContexts.location_stack);
    expect(testEvent.global_contexts).toEqual([]);
  });

  it('should allow compositions with multiple configs or instances and produce a valid location_stack', () => {
    const eventContexts: ContextsConfig = {
      location_stack: [
        { __instance_id: generateGUID(), __location_context: true, _type: 'section', id: 'D' },
        { __instance_id: generateGUID(), __location_context: true, _type: 'item', id: 'X' },
      ],
    };
    const sectionContexts1: ContextsConfig = {
      location_stack: [
        { __instance_id: generateGUID(), __location_context: true, _type: 'section', id: 'root' },
        { __instance_id: generateGUID(), __location_context: true, _type: 'section', id: 'A' },
      ],
    };
    const sectionContexts2: ContextsConfig = {
      location_stack: [
        { __instance_id: generateGUID(), __location_context: true, _type: 'section', id: 'B' },
        { __instance_id: generateGUID(), __location_context: true, _type: 'section', id: 'C' },
      ],
    };
    const composedEvent = new TrackerEvent(
      { _type: 'test-event', id: generateGUID(), time: Date.now(), ...eventContexts },
      sectionContexts1,
      sectionContexts2
    );
    expect(composedEvent.location_stack).toEqual([
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'root' },
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'A' },
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'B' },
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'C' },
      { __instance_id: matchUUID, __location_context: true, _type: 'section', id: 'D' },
      { __instance_id: matchUUID, __location_context: true, _type: 'item', id: 'X' },
    ]);
  });

  it('should serialize to JSON without internal properties', () => {
    const testEvent = new TrackerEvent({
      id: generateGUID(),
      time: Date.now(),
      ...makeMediaLoadEvent({
        location_stack: [makeOverlayContext({ id: 'player' })],
        global_contexts: [makeApplicationContext({ id: 'test-app' })],
      }),
    });
    const jsonStringEvent = JSON.stringify(testEvent, null, 2);
    expect(jsonStringEvent).toEqual(`{
  "_type": "MediaLoadEvent",
  "id": "${testEvent.id}",
  "time": ${testEvent.time},
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
  ]
}`);
  });

  it('should clone without generating a new id', () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    expect(testEvent.id).not.toBeUndefined();
    const testEventClone1 = new TrackerEvent(testEvent);
    const testEventClone1_1 = new TrackerEvent(testEventClone1);
    const testEventClone1_2 = new TrackerEvent(testEventClone1_1);
    expect(testEventClone1.id).toBe(testEvent.id);
    expect(testEventClone1_1.id).toBe(testEvent.id);
    expect(testEventClone1_2.id).toBe(testEvent.id);
  });
});

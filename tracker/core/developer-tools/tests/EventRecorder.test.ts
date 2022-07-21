/*
 * Copyright 2022 Objectiv B.V.
 */

import { generateGUID, TrackerEvent } from '@objectiv/tracker-core';
import { EventRecorder } from '../src/EventRecorder';

describe('EventRecorder', () => {
  beforeEach(() => {
    EventRecorder.clear();
    EventRecorder.configure();
  });

  it('should be usable and auto-recording', async () => {
    expect(EventRecorder.isUsable()).toBe(true);
    expect(EventRecorder.autoStart).toBe(true);
    expect(EventRecorder.recording).toBe(true);
  });

  it('should not be usable and not auto-recording', async () => {
    EventRecorder.configure({ enabled: false });
    expect(EventRecorder.isUsable()).toBe(false);
    expect(EventRecorder.autoStart).toBe(true);
    expect(EventRecorder.recording).toBe(false);
  });

  it('should become usable and start recording', async () => {
    EventRecorder.configure({ enabled: false });
    expect(EventRecorder.isUsable()).toBe(false);
    expect(EventRecorder.autoStart).toBe(true);
    expect(EventRecorder.recording).toBe(false);
    EventRecorder.configure({ enabled: true });
    expect(EventRecorder.isUsable()).toBe(true);
    expect(EventRecorder.autoStart).toBe(true);
    expect(EventRecorder.recording).toBe(true);
  });

  it('should store the events in `events` and sort them up', async () => {
    const testPressEvent = new TrackerEvent({ _type: 'PressEvent', id: 'test-press-event', time: Date.now() });
    const testVisibleEvent = new TrackerEvent({ _type: 'VisibleEvent', id: 'test-visible-event', time: Date.now() });
    const testSuccessEvent = new TrackerEvent({ _type: 'SuccessEvent', id: 'test-success-event', time: Date.now() });

    expect(EventRecorder._events).toStrictEqual([]);

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);

    expect(EventRecorder._events).toStrictEqual([
      expect.objectContaining({ _type: 'PressEvent', id: 'PressEvent#1' }),
      expect.objectContaining({ _type: 'SuccessEvent', id: 'SuccessEvent#1' }),
      expect.objectContaining({ _type: 'VisibleEvent', id: 'VisibleEvent#1' }),
    ]);

    expect(EventRecorder.events.events).toStrictEqual([
      expect.objectContaining({ _type: 'PressEvent', id: 'PressEvent#1' }),
      expect.objectContaining({ _type: 'SuccessEvent', id: 'SuccessEvent#1' }),
      expect.objectContaining({ _type: 'VisibleEvent', id: 'VisibleEvent#1' }),
    ]);

    expect(EventRecorder.events.filter('VisibleEvent').events).toStrictEqual([
      expect.objectContaining({ _type: 'VisibleEvent', id: 'VisibleEvent#1' }),
    ]);
  });

  it('should store the error messages in `errors` and sort them up', async () => {
    expect(EventRecorder.errors).toStrictEqual([]);

    EventRecorder.error('error 3');
    EventRecorder.error('error 1');
    EventRecorder.error('error 2');

    expect(EventRecorder.errors).toStrictEqual(['error 1', 'error 2', 'error 3']);
  });

  it('should automatically assign a predictable identifier to Events of the same type', async () => {
    const testPressEvent1 = new TrackerEvent({ _type: 'PressEvent', id: generateGUID(), time: Date.now() });
    const testPressEvent2 = new TrackerEvent({ _type: 'PressEvent', id: generateGUID(), time: Date.now() });
    const testPressEvent3 = new TrackerEvent({ _type: 'PressEvent', id: generateGUID(), time: Date.now() });

    expect(EventRecorder._events).toStrictEqual([]);

    await EventRecorder.handle(testPressEvent1, testPressEvent2, testPressEvent3);

    expect(EventRecorder._events).toStrictEqual([
      expect.objectContaining({ _type: 'PressEvent', id: 'PressEvent#1' }),
      expect.objectContaining({ _type: 'PressEvent', id: 'PressEvent#2' }),
      expect.objectContaining({ _type: 'PressEvent', id: 'PressEvent#3' }),
    ]);
  });

  it('should remove time information from recorded Events', async () => {
    const testPressEvent1 = new TrackerEvent({ _type: 'PressEvent', id: generateGUID(), time: Date.now() });
    const testPressEvent2 = new TrackerEvent({ _type: 'PressEvent', id: generateGUID(), time: Date.now() });
    const testPressEvent3 = new TrackerEvent({ _type: 'PressEvent', id: generateGUID(), time: Date.now() });

    expect(testPressEvent1.time).not.toBeUndefined();
    expect(testPressEvent2.time).not.toBeUndefined();
    expect(testPressEvent3.time).not.toBeUndefined();

    expect(EventRecorder._events).toStrictEqual([]);

    await EventRecorder.handle(testPressEvent1, testPressEvent2, testPressEvent3);

    // @ts-ignore
    expect(EventRecorder._events[0].time).toBeUndefined();
    // @ts-ignore
    expect(EventRecorder._events[1].time).toBeUndefined();
    // @ts-ignore
    expect(EventRecorder._events[2].time).toBeUndefined();
  });

  it('should clear the recorded events', async () => {
    const testPressEvent = new TrackerEvent({ _type: 'PressEvent', id: 'test-press-event', time: Date.now() });
    const testVisibleEvent = new TrackerEvent({ _type: 'VisibleEvent', id: 'test-visible-event', time: Date.now() });
    const testSuccessEvent = new TrackerEvent({ _type: 'SuccessEvent', id: 'test-success-event', time: Date.now() });

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);
    expect(EventRecorder._events.length).toBe(3);

    EventRecorder.clear();

    expect(EventRecorder._events.length).toBe(0);
  });

  it('should start recording', async () => {
    EventRecorder.configure({ autoStart: false });
    expect(EventRecorder.recording).toBe(false);

    const testPressEvent = new TrackerEvent({ _type: 'PressEvent', id: 'test-press-event', time: Date.now() });
    const testVisibleEvent = new TrackerEvent({ _type: 'VisibleEvent', id: 'test-visible-event', time: Date.now() });
    const testSuccessEvent = new TrackerEvent({ _type: 'SuccessEvent', id: 'test-success-event', time: Date.now() });

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);

    expect(EventRecorder._events.length).toBe(0);

    EventRecorder.start();

    expect(EventRecorder.recording).toBe(true);

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);

    expect(EventRecorder._events.length).toBe(3);
  });

  it('should stop recording', async () => {
    const testPressEvent = new TrackerEvent({ _type: 'PressEvent', id: 'test-press-event', time: Date.now() });
    const testVisibleEvent = new TrackerEvent({ _type: 'VisibleEvent', id: 'test-visible-event', time: Date.now() });
    const testSuccessEvent = new TrackerEvent({ _type: 'SuccessEvent', id: 'test-success-event', time: Date.now() });

    expect(EventRecorder.recording).toBe(true);

    EventRecorder.stop();

    expect(EventRecorder.recording).toBe(false);

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);

    expect(EventRecorder._events.length).toBe(0);
  });
});

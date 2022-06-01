/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackerEvent } from '@objectiv/tracker-core';
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

  it('should allow configuring maxEvents', async () => {
    EventRecorder.configure({ maxEvents: 10 });

    expect(EventRecorder.maxEvents).toBe(10);
  });

  it('should store the events in recordedEvents', async () => {
    const testPressEvent = new TrackerEvent({ _type: 'PressEvent', id: 'test-press-event' });
    const testVisibleEvent = new TrackerEvent({ _type: 'VisibleEvent', id: 'test-visible-event' });
    const testSuccessEvent = new TrackerEvent({ _type: 'SuccessEvent', id: 'test-success-event' });

    expect(EventRecorder.events).toStrictEqual([]);

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);

    expect(EventRecorder.events).toStrictEqual([
      expect.objectContaining({ _type: 'PressEvent', id: 'PressEvent#1' }),
      expect.objectContaining({ _type: 'VisibleEvent', id: 'VisibleEvent#1' }),
      expect.objectContaining({ _type: 'SuccessEvent', id: 'SuccessEvent#1' }),
    ]);
  });

  it('should automatically assign a predictable identifier to Events of the same type', async () => {
    const testPressEvent1 = new TrackerEvent({ _type: 'PressEvent' });
    const testPressEvent2 = new TrackerEvent({ _type: 'PressEvent' });
    const testPressEvent3 = new TrackerEvent({ _type: 'PressEvent' });

    expect(EventRecorder.events).toStrictEqual([]);

    await EventRecorder.handle(testPressEvent1, testPressEvent2, testPressEvent3);

    expect(EventRecorder.events).toStrictEqual([
      expect.objectContaining({ _type: 'PressEvent', id: 'PressEvent#1' }),
      expect.objectContaining({ _type: 'PressEvent', id: 'PressEvent#2' }),
      expect.objectContaining({ _type: 'PressEvent', id: 'PressEvent#3' }),
    ]);
  });

  it('should remove time information from recorded Events', async () => {
    const testPressEvent1 = new TrackerEvent({ _type: 'PressEvent' });
    const testPressEvent2 = new TrackerEvent({ _type: 'PressEvent' });
    const testPressEvent3 = new TrackerEvent({ _type: 'PressEvent' });

    testPressEvent1.setTime();
    testPressEvent2.setTime();
    testPressEvent3.setTime();

    expect(testPressEvent1.time).not.toBeUndefined();
    expect(testPressEvent2.time).not.toBeUndefined();
    expect(testPressEvent3.time).not.toBeUndefined();

    expect(EventRecorder.events).toStrictEqual([]);

    await EventRecorder.handle(testPressEvent1, testPressEvent2, testPressEvent3);

    // @ts-ignore
    expect(EventRecorder.events[0].time).toBeUndefined();
    // @ts-ignore
    expect(EventRecorder.events[1].time).toBeUndefined();
    // @ts-ignore
    expect(EventRecorder.events[2].time).toBeUndefined();
  });

  it('should clear the recorded events', async () => {
    const testPressEvent = new TrackerEvent({ _type: 'PressEvent', id: 'test-press-event' });
    const testVisibleEvent = new TrackerEvent({ _type: 'VisibleEvent', id: 'test-visible-event' });
    const testSuccessEvent = new TrackerEvent({ _type: 'SuccessEvent', id: 'test-success-event' });

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);
    expect(EventRecorder.events.length).toBe(3);

    EventRecorder.clear();

    expect(EventRecorder.events.length).toBe(0);
  });

  it('should start recording', async () => {
    EventRecorder.configure({ autoStart: false });
    expect(EventRecorder.recording).toBe(false);

    const testPressEvent = new TrackerEvent({ _type: 'PressEvent', id: 'test-press-event' });
    const testVisibleEvent = new TrackerEvent({ _type: 'VisibleEvent', id: 'test-visible-event' });
    const testSuccessEvent = new TrackerEvent({ _type: 'SuccessEvent', id: 'test-success-event' });

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);

    expect(EventRecorder.events.length).toBe(0);

    EventRecorder.start();

    expect(EventRecorder.recording).toBe(true);

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);

    expect(EventRecorder.events.length).toBe(3);
  });

  it('should stop recording', async () => {
    const testPressEvent = new TrackerEvent({ _type: 'PressEvent', id: 'test-press-event' });
    const testVisibleEvent = new TrackerEvent({ _type: 'VisibleEvent', id: 'test-visible-event' });
    const testSuccessEvent = new TrackerEvent({ _type: 'SuccessEvent', id: 'test-success-event' });

    expect(EventRecorder.recording).toBe(true);

    EventRecorder.stop();

    expect(EventRecorder.recording).toBe(false);

    await EventRecorder.handle(testPressEvent, testVisibleEvent, testSuccessEvent);

    expect(EventRecorder.events.length).toBe(0);
  });

  it('should throw away the oldest recorder events when reaching maxEvents', async () => {
    EventRecorder.configure({ maxEvents: 3 });

    const event1 = new TrackerEvent({ _type: 'PressEvent' });
    const event2 = new TrackerEvent({ _type: 'PressEvent' });
    const event3 = new TrackerEvent({ _type: 'PressEvent' });
    const event4 = new TrackerEvent({ _type: 'PressEvent' });
    const event5 = new TrackerEvent({ _type: 'PressEvent' });
    const event6 = new TrackerEvent({ _type: 'PressEvent' });
    const event7 = new TrackerEvent({ _type: 'PressEvent' });
    const event8 = new TrackerEvent({ _type: 'PressEvent' });
    const event9 = new TrackerEvent({ _type: 'PressEvent' });

    await EventRecorder.handle(event1, event2, event3, event4);

    expect(EventRecorder.events.length).toBe(3);
    expect(EventRecorder.events[0].id).toBe('PressEvent#2');
    expect(EventRecorder.events[1].id).toBe('PressEvent#3');
    expect(EventRecorder.events[2].id).toBe('PressEvent#4');

    await EventRecorder.handle(event5);

    expect(EventRecorder.events.length).toBe(3);
    expect(EventRecorder.events[0].id).toBe('PressEvent#3');
    expect(EventRecorder.events[1].id).toBe('PressEvent#4');
    expect(EventRecorder.events[2].id).toBe('PressEvent#5');

    await EventRecorder.handle(event6, event7, event8);

    expect(EventRecorder.events.length).toBe(3);
    expect(EventRecorder.events[0].id).toBe('PressEvent#6');
    expect(EventRecorder.events[1].id).toBe('PressEvent#7');
    expect(EventRecorder.events[2].id).toBe('PressEvent#8');

    await EventRecorder.handle(event9);

    expect(EventRecorder.events.length).toBe(3);
    expect(EventRecorder.events[0].id).toBe('PressEvent#7');
    expect(EventRecorder.events[1].id).toBe('PressEvent#8');
    expect(EventRecorder.events[2].id).toBe('PressEvent#9');
  });
});

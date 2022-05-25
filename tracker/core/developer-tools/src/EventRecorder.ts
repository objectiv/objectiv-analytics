/*
 * Copyright 2022 Objectiv B.V.
 */

import {
  cleanObjectFromInternalProperties,
  EventRecorderConfig,
  EventRecorderInterface,
  NonEmptyArray,
  RecordedEvent,
  TrackerEvent,
  TransportableEvent,
} from '@objectiv/tracker-core';

/**
 * Some default values for the global instance of EventRecorder. Can be changed by calling EventRecorder.configure.
 */
const DEFAULT_ENABLED = true;
const DEFAULT_MAX_EVENTS = 1000;
const DEFAULT_AUTO_START = true;

/**
 * EventRecorder factory. A TrackerTransport to store TrackerEvents in the `recordedEvents` state for later analysis.
 * Recorded TrackerEvents are automatically assigned predictable identifiers: `event.type` + `#` + number of times
 * Event Type occurred, starting at 1. Also, their `time` is removed. This ensures comparability.
 */
export const EventRecorder = new (class implements EventRecorderInterface {
  readonly transportName = 'EventRecorder';
  enabled: boolean = DEFAULT_ENABLED;
  maxEvents: number = DEFAULT_MAX_EVENTS;
  autoStart: boolean = DEFAULT_AUTO_START;
  recording: boolean = this.enabled && this.autoStart;
  events: RecordedEvent[] = [];
  eventsCountByType: { [type: string]: number } = {};

  /**
   * Reconfigures EventRecorder `maxEvents` and/or `autoStart`.
   */
  configure(eventRecorderConfig?: EventRecorderConfig) {
    this.enabled = eventRecorderConfig?.enabled ?? DEFAULT_ENABLED;
    this.maxEvents = eventRecorderConfig?.maxEvents ?? DEFAULT_MAX_EVENTS;
    this.autoStart = eventRecorderConfig?.autoStart ?? DEFAULT_AUTO_START;
    this.recording = this.enabled && this.autoStart;
  }

  /**
   * Completely resets EventRecorder state.
   */
  clear() {
    this.events.length = 0;
    this.eventsCountByType = {};
  }

  /**
   * Starts recording events.
   */
  start() {
    if (!this.recording && this.enabled) {
      this.recording = true;
    }
  }

  /**
   * Stops recording events.
   */
  stop() {
    if (this.recording && this.enabled) {
      this.recording = false;
    }
  }

  /**
   * Stores incoming TrackerEvents to globalThis.objectiv.recordedEvents
   */
  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    if (!this.recording) {
      return;
    }

    (await Promise.all(args)).forEach((trackerEvent) => {
      const eventType = trackerEvent._type;

      // Clone the event
      const recordedEvent = new TrackerEvent(trackerEvent);

      // Increment how many times have we seen this event type so far
      this.eventsCountByType[eventType] = (this.eventsCountByType[eventType] ?? 0) + 1;

      // Make event predictable, set the new identifier and remove time information
      recordedEvent.id = `${eventType}#${this.eventsCountByType[eventType]}`;
      delete recordedEvent.time;

      this.events.push({
        ...cleanObjectFromInternalProperties(recordedEvent),
        location_stack: recordedEvent.location_stack.map(cleanObjectFromInternalProperties),
        global_contexts: recordedEvent.global_contexts.map(cleanObjectFromInternalProperties),
      });
    });

    if (this.events.length >= this.maxEvents) {
      this.events.splice(0, this.events.length - this.maxEvents);
    }
  }

  /**
   * EventRecorder is usable as a Transport if it's enabled.
   */
  isUsable(): boolean {
    return this.enabled;
  }
})();

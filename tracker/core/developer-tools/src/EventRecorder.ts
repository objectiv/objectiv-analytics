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
import { RecordedEvents } from './RecordedEvents';

/**
 * Some default values for the global instance of EventRecorder. Can be changed by calling EventRecorder.configure.
 */
const DEFAULT_ENABLED = true;
const DEFAULT_AUTO_START = true;

/**
 * EventRecorder is a TrackerTransport to store TrackerEvents and error messages for later analysis.
 * Recorded TrackerEvents are automatically assigned predictable identifiers: `event.type` + `#` + number of times
 * Event Type occurred, starting at 1. Also, their `time` is removed. This ensures comparability.
 * Furthermore, the lists of TrackedEvents and error messages are sorted for easier testing.
 */
export const EventRecorder = new (class implements EventRecorderInterface {
  readonly transportName = 'EventRecorder';
  enabled: boolean = DEFAULT_ENABLED;
  autoStart: boolean = DEFAULT_AUTO_START;
  recording: boolean = this.enabled && this.autoStart;
  errors: string[] = [];
  _events: RecordedEvent[] = [];
  eventsCountByType: { [type: string]: number } = {};

  /**
   * Reconfigures EventRecorder's `enabled` and `autoStart` options.
   */
  configure(eventRecorderConfig?: EventRecorderConfig) {
    this.enabled = eventRecorderConfig?.enabled ?? DEFAULT_ENABLED;
    this.autoStart = eventRecorderConfig?.autoStart ?? DEFAULT_AUTO_START;
    this.recording = this.enabled && this.autoStart;
  }

  /**
   * Completely resets EventRecorder state.
   */
  clear() {
    this.errors.length = 0;
    this._events.length = 0;
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
   * Stores incoming TrackerEvents in state
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

      this._events.push({
        ...cleanObjectFromInternalProperties(recordedEvent),
        location_stack: recordedEvent.location_stack.map(cleanObjectFromInternalProperties),
        global_contexts: recordedEvent.global_contexts.map(cleanObjectFromInternalProperties),
      });
    });

    // Make event list predictable, sort by event id
    this._events.sort((a: RecordedEvent, b: RecordedEvent) => a.id.localeCompare(b.id));
  }

  /**
   * Records an error.
   */
  error(errorMessage: string) {
    this.errors.push(errorMessage);

    // Make error list predictable by sorting it
    this.errors.sort();
  }

  /**
   * Returns a list of recorded events wrapped in a RecordedEvents instance for easier querying.
   */
  get events() {
    return new RecordedEvents(this._events);
  }

  /**
   * EventRecorder is usable as a Transport if it's enabled.
   */
  isUsable(): boolean {
    return this.enabled;
  }
})();

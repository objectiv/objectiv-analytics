/*
 * Copyright 2022 Objectiv B.V.
 */

import {
  AnyGlobalContextName,
  AnyLocationContextName,
  RecordedAbstractGlobalContext,
  RecordedAbstractLocationContext,
  RecordedEvent,
  RecordedEventPredicate,
  RecordedEventsInterface,
} from '@objectiv/tracker-core';

/**
 * RecordedEvents instances can filter the given RecordedEvents by event and/or their contexts.
 */
export class RecordedEvents implements RecordedEventsInterface {
  readonly name = 'RecordedEvents';
  readonly events: RecordedEvent[];

  /**
   * RecordedEvents is constructed with a list of RecordedEvents, stored in its internal state for later processing
   */
  constructor(events: RecordedEvent[]) {
    this.events = events;
  }

  /**
   * Filters events by Event name (_type attribute). It supports querying by:
   *
   * - a single event name, e.g. `PressEvent`
   * - a list of event names, e.g. [`PressEvent`, `ApplicationLoadedEvent`]
   * - a predicate, for advanced operations, e.g. (event) => boolean
   *
   * `filter` returns a new instance of RecordedEvents for further chaining.
   */
  filter(options: unknown) {
    if (typeof options === 'string') {
      return new RecordedEvents(this.events.filter((event) => event._type === options));
    }

    if (Array.isArray(options) && options.length) {
      return new RecordedEvents(this.events.filter((event) => options.includes(event._type)));
    }

    if (typeof options === 'function') {
      return new RecordedEvents(this.events.filter(options as RecordedEventPredicate));
    }

    throw new Error(`Invalid event filter options: ${JSON.stringify(options)}`);
  }

  /**
   * Filters events by their LocationContext's name (_type attribute), name and id or just name.
   * `withLocationContext` returns a new instance of RecordedEvents for further chaining.
   */
  withLocationContext(name: AnyLocationContextName, id?: string) {
    if (typeof name !== 'string') {
      throw new Error(`Invalid location context filter name option: ${JSON.stringify(name)}`);
    }
    if (id !== undefined && typeof id !== 'string') {
      throw new Error(`Invalid location context filter id option: ${JSON.stringify(id)}`);
    }

    return new RecordedEvents(this.events.filter((event) => hasContext(event.location_stack, name, id)));
  }

  /**
   * Filters events by their GlobalContext's name (_type attribute), name and id or just name.
   * `withGlobalContext` returns a new instance of RecordedEvents for further chaining.
   */
  withGlobalContext(name: AnyGlobalContextName, id?: string) {
    if (typeof name !== 'string') {
      throw new Error(`Invalid global context filter name option: ${JSON.stringify(name)}`);
    }
    if (id !== undefined && typeof id !== 'string') {
      throw new Error(`Invalid location context filter id option: ${JSON.stringify(id)}`);
    }

    return new RecordedEvents(this.events.filter((event) => hasContext(event.global_contexts, name, id)));
  }
}

/**
 * Helper private predicate to match a Context in the given list of contexts by name and id or just name.
 */
const hasContext = (
  contexts: (RecordedAbstractLocationContext | RecordedAbstractGlobalContext)[],
  name: string,
  id?: string
) =>
  contexts.find((context) => {
    if (name && id) {
      return context._type === name && context.id === id;
    }

    return context._type === name;
  });

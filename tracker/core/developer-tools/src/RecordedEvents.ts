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

    if (options instanceof Function) {
      return new RecordedEvents(this.events.filter(options as RecordedEventPredicate));
    }

    throw new Error(`Invalid event filter options: ${JSON.stringify(options)}`);
  }

  /**
   * Filters events by their LocationContext's name (_type attribute), name and id or just id. It supports:
   *
   * - a Location Context name, e.g. `RootLocationContext`
   * - a Location Context name and its identifier, separated by a colon, e.g. `RootLocationContext:home`
   * - a Location Context identifier, prefixed by a colon, e.g. `:home`
   *
   * `withLocationContext` returns a new instance of RecordedEvents for further chaining.
   */
  withLocationContext(nameAndMaybeId: AnyLocationContextName) {
    if (typeof nameAndMaybeId !== 'string') {
      throw new Error(`Invalid location context filter options: ${JSON.stringify(nameAndMaybeId)}`);
    }

    const [name, id] = splitNameAndMaybeId(nameAndMaybeId);

    return new RecordedEvents(this.events.filter((event) => hasContext(event.location_stack, name, id)));
  }

  /**
   * Filters events by their GlobalContext's name (_type attribute), name and id or just id. It supports:
   *
   * - a Global Context name, e.g. `PathContext`
   * - a Global Context name and its identifier, separated by a colon, e.g. `PathContext:http://localhost/`
   * - a Global Context identifier, prefixed by a colon, e.g. `:http://localhost/`
   *
   * `withGlobalContext` returns a new instance of RecordedEvents for further chaining.
   */
  withGlobalContext(nameAndMaybeId: AnyGlobalContextName) {
    if (typeof nameAndMaybeId !== 'string') {
      throw new Error(`Invalid global context filter options: ${JSON.stringify(nameAndMaybeId)}`);
    }

    const [name, id] = splitNameAndMaybeId(nameAndMaybeId);

    return new RecordedEvents(this.events.filter((event) => hasContext(event.global_contexts, name, id)));
  }
}

/**
 * Helper private function to split Context names from their identifiers.
 */
const splitNameAndMaybeId = (nameAndMaybeId: string) => {
  const [name, ...id] = nameAndMaybeId.split(':');
  return [name, id.join(':')];
};

/**
 * Helper private predicate to match a Context in the given list of contexts by name, id or both.
 */
const hasContext = (
  contexts: (RecordedAbstractLocationContext | RecordedAbstractGlobalContext)[],
  name: string,
  id: string
) =>
  contexts.find((context) => {
    if (name && id) {
      return context._type === name && context.id === id;
    }

    if (name) {
      return context._type === name;
    }

    return context.id === id;
  });

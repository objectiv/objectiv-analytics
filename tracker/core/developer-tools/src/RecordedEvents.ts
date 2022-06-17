/*
 * Copyright 2022 Objectiv B.V.
 */

import {
  EventName,
  GlobalContextName,
  LocationContextName,
  RecordedAbstractGlobalContext,
  RecordedAbstractLocationContext,
  RecordedEvent,
} from '@objectiv/tracker-core';

export type AnyEventName = `${EventName}`;
export type RecordedEventPredicate = (value: RecordedEvent) => boolean;
export type AnyLocationContextName = `${LocationContextName}`;
export type AnyLocationContextNameAndId = `${LocationContextName}:${string}` | `:${string}`;
export type AnyGlobalContextName = `${GlobalContextName}`;
export type AnyGlobalContextNameAndId = `${GlobalContextName}:${string}` | `:${string}`;

/**
 * RecordedEvents instances can filter the given RecordedEvents by event type and/or context name and id.
 */
export class RecordedEvents {
  readonly events: RecordedEvent[];

  /**
   * RecordedEvents is constructed with a list of RecordedEvents, stored in its internal state for later processing
   */
  constructor(events: RecordedEvent[]) {
    this.events = events;
  }

  /**
   * The filter method allows to filter by Event _type. It supports querying by:
   *
   * - a single event name, e.g. `PressEvent`
   * - a list of event names, e.g. [`PressEvent`, `ApplicationLoadedEvent`]
   * - a predicate, for advanced operations, e.g. (event) => boolean
   *
   * `filter` returns a new instance of RecordedEvents for further chaining.
   */
  filter(name: AnyEventName): RecordedEvents;
  filter(names: AnyEventName[]): RecordedEvents;
  filter(predicate: RecordedEventPredicate): RecordedEvents;

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
   * The withLocationContext method allows to filter LocationContexts by name, name and id or just id. It supports:
   *
   * - a Location Context name, e.g. `RootLocationContext`
   * - a Location Context name and its identifier, separated by a colon, e.g. `RootLocationContext:home`
   * - a Location Context identifier, prefixed by a colon, e.g. `:home`
   *
   * `withLocationContext` returns a new instance of RecordedEvents for further chaining.
   */
  withLocationContext(nameAndMaybeId: AnyLocationContextName | AnyLocationContextNameAndId) {
    if (typeof nameAndMaybeId !== 'string') {
      throw new Error(`Invalid location context filter options: ${JSON.stringify(nameAndMaybeId)}`);
    }

    const [name, id] = splitNameAndMaybeId(nameAndMaybeId);

    return new RecordedEvents(this.events.filter((event) => hasContext(event.location_stack, name, id)));
  }

  /**
   * The withGlobalContext method allows to filter GlobalContexts by name, name and id or just id. It supports:
   *
   * - a Global Context name, e.g. `PathContext`
   * - a Global Context name and its identifier, separated by a colon, e.g. `PathContext:http://localhost/`
   * - a Global Context identifier, prefixed by a colon, e.g. `:http://localhost/`
   *
   * `withGlobalContext` returns a new instance of RecordedEvents for further chaining.
   */
  withGlobalContext(nameAndMaybeId: AnyGlobalContextName | AnyGlobalContextNameAndId) {
    if (typeof nameAndMaybeId !== 'string') {
      throw new Error(`Invalid global context filter options: ${JSON.stringify(nameAndMaybeId)}`);
    }

    const [name, id] = splitNameAndMaybeId(nameAndMaybeId);

    return new RecordedEvents(this.events.filter((event) => hasContext(event.global_contexts, name, id)));
  }
}

const splitNameAndMaybeId = (nameAndMaybeId: string) => {
  const [name, ...id] = nameAndMaybeId.split(':');
  return [name, id.join(':')];
};

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

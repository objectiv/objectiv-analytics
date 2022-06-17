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

export class RecordedEvents {
  readonly events: RecordedEvent[];
  constructor(events: RecordedEvent[]) {
    this.events = events;
  }

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

  withLocationContext(nameAndMaybeId: AnyLocationContextName | AnyLocationContextNameAndId) {
    if (typeof nameAndMaybeId !== 'string') {
      throw new Error(`Invalid location context filter options: ${JSON.stringify(nameAndMaybeId)}`);
    }

    const [name, id] = splitNameAndMaybeId(nameAndMaybeId);

    return new RecordedEvents(this.events.filter((event) => hasContext(event.location_stack, name, id)));
  }

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

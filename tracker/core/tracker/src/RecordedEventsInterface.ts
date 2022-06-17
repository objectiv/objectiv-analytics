/*
 * Copyright 2022 Objectiv B.V.
 */

import { GlobalContextName, LocationContextName } from './ContextNames';
import { EventName } from './EventNames';
import { RecordedEvent } from './EventRecorderInterface';

/**
 * Set of all Event names.
 */
export type AnyEventName = `${EventName}`;

/**
 * Set of all Location Context names. An identifier can be also be present, prepended by a colon; e.g. Context:id.
 */
export type AnyLocationContextName = `${LocationContextName}` | `${LocationContextName}:${string}` | `:${string}`;

/**
 * Set of all Global Context names. An identifier can be also be present, prepended by a colon; e.g. Context:id.
 */
export type AnyGlobalContextName = `${GlobalContextName}` | `${GlobalContextName}:${string}` | `:${string}`;

/**
 * Predicate that can be passed to `filter`. Receives a recordedEvent as parameter.
 */
export type RecordedEventPredicate = (recordedEvent: RecordedEvent) => boolean;

/**
 * RecordedEvents instances can filter the given RecordedEvents by event and/or their contexts.
 */
export type RecordedEventsInterface = {
  /**
   * Holds a list of recorded events.
   */
  events: RecordedEvent[];

  /**
   * Filters events by Event name (_type attribute). It supports querying by:
   *
   * - a single event name, e.g. `PressEvent`
   * - a list of event names, e.g. [`PressEvent`, `ApplicationLoadedEvent`]
   * - a predicate, for advanced operations, e.g. (event) => boolean
   *
   * `filter` returns a new instance of RecordedEvents for further chaining.
   */
  filter(name: AnyEventName): RecordedEventsInterface;
  filter(names: AnyEventName[]): RecordedEventsInterface;
  filter(predicate: RecordedEventPredicate): RecordedEventsInterface;

  /**
   * Filters events by their LocationContext's name (_type attribute), name and id or just id. It supports:
   *
   * - a Location Context name, e.g. `RootLocationContext`
   * - a Location Context name and its identifier, separated by a colon, e.g. `RootLocationContext:home`
   * - a Location Context identifier, prefixed by a colon, e.g. `:home`
   *
   * `withLocationContext` returns a new instance of RecordedEvents for further chaining.
   */
  withLocationContext(nameAndMaybeId: AnyLocationContextName): RecordedEventsInterface;

  /**
   * Filters events by their GlobalContext's name (_type attribute), name and id or just id. It supports:
   *
   * - a Global Context name, e.g. `PathContext`
   * - a Global Context name and its identifier, separated by a colon, e.g. `PathContext:http://localhost/`
   * - a Global Context identifier, prefixed by a colon, e.g. `:http://localhost/`
   *
   * `withGlobalContext` returns a new instance of RecordedEvents for further chaining.
   */
  withGlobalContext(nameAndMaybeId: AnyGlobalContextName): RecordedEventsInterface;
};

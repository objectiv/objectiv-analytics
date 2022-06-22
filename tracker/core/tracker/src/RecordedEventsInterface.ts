/*
 * Copyright 2022 Objectiv B.V.
 */

import { AnyGlobalContextName, AnyLocationContextName } from './ContextNames';
import { AnyEventName } from './EventNames';
import { RecordedEvent } from './EventRecorderInterface';

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
   * Filters events by their LocationContext's name (_type attribute), name and id or just name.
   * `withLocationContext` returns a new instance of RecordedEvents for further chaining.
   */
  withLocationContext(name: AnyLocationContextName, id?: string): RecordedEventsInterface;

  /**
   * Filters events by their GlobalContext's name (_type attribute), name and id or just name.
   * `withGlobalContext` returns a new instance of RecordedEvents for further chaining.
   */
  withGlobalContext(name: AnyGlobalContextName, id?: string): RecordedEventsInterface;
};

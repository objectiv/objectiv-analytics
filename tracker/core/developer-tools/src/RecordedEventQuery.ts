/*
 * Copyright 2022 Objectiv B.V.
 */

import { EventNames, RecordedEvent, } from '@objectiv/tracker-core';

type EventName = `${EventNames}`;
const filterRecordedEventsByEventType = (events: RecordedEvent[], eventName: EventName) => {
  return events.filter(event => event._type === eventName);
}

const filterRecordedEventsByEventTypes = (events: RecordedEvent[], eventTypes: EventName[]) => {
  return events.filter(event => eventTypes.includes(event._type as EventName));
}

type RecordedEventPredicate<T=RecordedEvent> = (event: T, index: number, array: T[]) => boolean;
const filterRecordedEventsByPredicate = (events: RecordedEvent[], predicate: RecordedEventPredicate) => {
  return events.filter(predicate);
}

const filterRecordedEvents = (events: RecordedEvent[], filter: EventName | EventName[] | RecordedEventPredicate) => {
  if(Array.isArray(filter)) {
    return filterRecordedEventsByEventTypes(events, filter);
  }

  if(filter instanceof Function) {
    return filterRecordedEventsByPredicate(events, filter);
  }


  return filterRecordedEventsByEventType(events, filter);
}

filterRecordedEventsByEventType([], 'ApplicationLoadedEvent')
filterRecordedEventsByEventTypes([], ['ApplicationLoadedEvent', 'PressEvent'])
filterRecordedEvents([], 'ApplicationLoadedEvent');
filterRecordedEvents([], ['ApplicationLoadedEvent', 'PressEvent']);
filterRecordedEvents([], (event) => event.id !== 'lol');

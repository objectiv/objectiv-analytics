/*
 * Copyright 2022 Objectiv B.V.
 */

import { RecordedEvent, } from '@objectiv/tracker-core';

export type filterRecordedEventsOptions = ((event) => boolean) | string[] | string;

const filterRecordedEvents = (events: RecordedEvent[], filter: filterRecordedEventsOptions) => {
  if(typeof filter ==='string') {
    return events.filter(event => event._type === filter);
  }

  if(Array.isArray(filter)) {
    return events.filter(event => filter.includes(event._type));
  }

  return events.filter(filter)
}

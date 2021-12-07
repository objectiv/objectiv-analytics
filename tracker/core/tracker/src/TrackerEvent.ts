/*
 * Copyright 2021 Objectiv B.V.
 */

import {
  AbstractEvent,
  AbstractGlobalContext,
  AbstractLocationContext,
  Contexts,
  DiscriminatingPropertyPrefix,
} from '@objectiv/schema';
import { ContextsConfig } from './Context';
import { generateUUID, getObjectKeys } from './helpers';

/**
 * TrackerEvents are simply a combination of an `event` name and their Contexts.
 * Contexts are entirely optional, although Collectors will mostly likely enforce minimal requirements around them.
 * Eg. An interactive TrackerEvent without a Location Stack is probably not descriptive enough to be acceptable.
 */
export type TrackerEventConfig = Pick<AbstractEvent, '_type'> &
  ContextsConfig & {
    // Unless the Event config has been preconfigured with an id the TrackerEvent will generate one for us
    id?: string;
  };

/**
 * An Event before it has been handed over to the Tracker.
 * Properties that will be set by the Tracker or Transport are omitted: `id`, `time`
 */
export type UntrackedEvent = Omit<AbstractEvent, 'id' | 'time'>;

/**
 * Our main TrackerEvent interface and basic implementation
 */
export class TrackerEvent implements UntrackedEvent, Contexts {
  // Event interface
  readonly _type: string;
  id: string;
  time?: number;

  // Contexts interface
  readonly location_stack: AbstractLocationContext[];
  readonly global_contexts: AbstractGlobalContext[];

  /**
   * Configures the TrackerEvent instance via a TrackerEventConfig and optionally one or more ContextConfig.
   *
   * TrackerEventConfig is used mainly to configure the `event` property, although it can also carry Contexts.
   *
   * ContextConfigs are used to configure location_stack and global_contexts. If multiple configurations have been
   * provided they will be merged onto each other to produce a single location_stack and global_contexts.
   */
  constructor({ _type, id, ...otherEventProps }: TrackerEventConfig, ...contextConfigs: ContextsConfig[]) {
    // Let's copy the entire eventConfiguration in state
    this._type = _type;
    Object.assign(this, otherEventProps);

    // If the Event does not have an id yet, generate one
    this.id = id ?? generateUUID();

    // Start with empty context lists
    let new_location_stack: AbstractLocationContext[] = [];
    let new_global_contexts: AbstractGlobalContext[] = [];

    // Process ContextConfigs first. Same order as they have been passed
    contextConfigs.forEach(({ location_stack, global_contexts }) => {
      new_location_stack = [...new_location_stack, ...(location_stack ?? [])];
      new_global_contexts = [...new_global_contexts, ...(global_contexts ?? [])];
    });

    // And finally add the TrackerEvent Contexts on top. For Global Contexts instead we do the opposite.
    this.location_stack = [...new_location_stack, ...(otherEventProps.location_stack ?? [])];
    this.global_contexts = [...(otherEventProps.global_contexts ?? []), ...new_global_contexts];
  }

  /**
   * Tracking time setter.
   * Defaults to Date.now() if not timestampMs is provided.
   */
  setTime(timestampMs: number = Date.now()) {
    this.time = timestampMs;
  }

  /**
   * Custom JSON serializer that cleans up the discriminatory properties we use internally to differentiate
   * between Contexts and Event types. This ensures the Event we send to Collectors has only OSF properties.
   */
  toJSON() {
    // All discriminating properties start with this prefix
    const DISCRIMINATING_PROPERTY_PREFIX: DiscriminatingPropertyPrefix = '__';

    // Deep-clone the TrackerEvent to avoid mutating the original
    const cleanedTrackerEvent: TrackerEvent = { ...this };

    // Our cleaning function
    const cleanObjectFromDiscriminatingProperties = <T extends object>(obj: T) => {
      getObjectKeys(obj).forEach((propertyName) => {
        if (propertyName.toString().startsWith(DISCRIMINATING_PROPERTY_PREFIX)) {
          delete obj[propertyName];
        }
      });
    };

    // Remove all discriminating properties from the TrackerEvent itself, its location_stack and its global_contexts
    cleanObjectFromDiscriminatingProperties(cleanedTrackerEvent);
    cleanedTrackerEvent.location_stack.map(cleanObjectFromDiscriminatingProperties);
    cleanedTrackerEvent.global_contexts.map(cleanObjectFromDiscriminatingProperties);

    return cleanedTrackerEvent;
  }
}

/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  AbstractEvent,
  AbstractGlobalContext,
  AbstractLocationContext,
  Contexts,
  EventAbstractDiscriminators,
} from '@objectiv/schema';
import { cleanObjectFromInternalProperties } from './cleanObjectFromInternalProperties';
import { ContextsConfig } from './Context';

/**
 * TrackerEvents can be constructed with simply an Event `type` and, optionally, their Contexts.
 * Contexts are entirely optional, although Collectors will mostly likely enforce minimal requirements around them.
 * E.g. An interactive TrackerEvent without a Location Stack is probably not descriptive enough to be acceptable.
 */
export type TrackerEventAttributes = Pick<AbstractEvent, '_type'> & ContextsConfig;

/**
 * The configuration object accepted by TrackerEvent's constructor
 * */
export type TrackerEventConfig = Pick<AbstractEvent, '_type' | 'id' | 'time'> & ContextsConfig;

/**
 * Our main TrackedEvent interface and basic implementation.
 */
export class TrackerEvent implements Contexts {
  readonly _type: string;
  readonly id: string;
  readonly time: number;
  readonly location_stack: AbstractLocationContext[];
  readonly global_contexts: AbstractGlobalContext[];

  /**
   * Configures the TrackerEvent instance via a TrackerEvent or TrackerEventConfig.
   * Optionally one or more ContextConfig can be specified as additional parameters.
   *
   * ContextConfigs are used to configure location_stack and global_contexts. If multiple configurations have been
   * provided they will be merged onto each other to produce a single location_stack and global_contexts.
   */
  constructor({ _type, id, time, ...otherProps }: TrackerEventConfig, ...contextConfigs: ContextsConfig[]) {
    this._type = _type;
    this.id = id;
    this.time = time;

    // Let's also set all the other props in state, this includes discriminatory properties and other internals
    Object.assign(this, otherProps);

    // Start with empty context lists
    let new_location_stack: AbstractLocationContext[] = [];
    let new_global_contexts: AbstractGlobalContext[] = [];

    // Process ContextConfigs first. Same order as they have been passed
    contextConfigs.forEach(({ location_stack, global_contexts }) => {
      new_location_stack = [...new_location_stack, ...(location_stack ?? [])];
      new_global_contexts = [...new_global_contexts, ...(global_contexts ?? [])];
    });

    // And finally add the TrackerEvent Contexts on top. For Global Contexts instead we do the opposite.
    this.location_stack = [...new_location_stack, ...(otherProps.location_stack ?? [])];
    this.global_contexts = [...(otherProps.global_contexts ?? []), ...new_global_contexts];
  }

  /**
   * Custom JSON serializer that cleans up the internally properties we use internally to differentiate between
   * Contexts and Event types and for validation. This ensures the Event we send to Collectors has only OSF properties.
   */
  toJSON() {
    return {
      ...cleanObjectFromInternalProperties(this),
      location_stack: this.location_stack.map(cleanObjectFromInternalProperties),
      global_contexts: this.global_contexts.map(cleanObjectFromInternalProperties),
    };
  }
}

/**
 * An Event ready to be validated.
 */
export type EventToValidate = TrackerEvent & EventAbstractDiscriminators;

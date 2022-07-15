/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { AbstractEvent, AbstractGlobalContext, AbstractLocationContext, Contexts } from '@objectiv/schema';
import { cleanObjectFromInternalProperties } from './cleanObjectFromInternalProperties';
import { ContextsConfig } from './Context';

/**
 * TrackerEvents are simply a combination of an `event` name and their Contexts.
 * Contexts are entirely optional, although Collectors will mostly likely enforce minimal requirements around them.
 * E.g. An interactive TrackerEvent without a Location Stack is probably not descriptive enough to be acceptable.
 */
export type UntrackedEventConfig = Pick<AbstractEvent, '_type'> & ContextsConfig;

/**
 * An Event before it has been handed over to the Tracker. It doesn't have `id` and `time` attributes yet.
 */
export class UntrackedEvent implements Contexts {
  readonly _type: string;
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
  constructor({ _type, ...otherEventProps }: UntrackedEventConfig, ...contextConfigs: ContextsConfig[]) {
    // Let's copy the entire eventConfiguration in state
    this._type = _type;

    // Let's also set all the other props in state, this includes discriminatory properties and other internals
    Object.assign(this, otherEventProps);

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

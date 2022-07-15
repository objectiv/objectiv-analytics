/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { EventAbstractDiscriminators } from '@objectiv/schema';
import { ContextsConfig } from './Context';
import { UntrackedEvent, UntrackedEventConfig } from './UntrackedEvent';

/**
 * TrackerEvents extends UntrackedEvents with obligatory `id` and `time` attributes.
 */
export type TrackerEventConfig = UntrackedEventConfig & {
  /**
   * The event unique identifier.
   */
  id: string;

  /**
   * The tracking time.
   */
  time: number;
};

/**
 * Our main TrackedEvent interface and basic implementation.
 */
export class TrackerEvent extends UntrackedEvent {
  id: string;
  time: number;

  /**
   * Configures the TrackerEvent instance via a TrackedEventConfig, which requires setting `id` and `time`.
   */
  constructor(trackedEventConfig: TrackerEventConfig, ...contextConfigs: ContextsConfig[]) {
    super(trackedEventConfig, ...contextConfigs);
    this.id = trackedEventConfig.id;
    this.time = trackedEventConfig.time;
  }
}

/**
 * An Event ready to be validated.
 */
export type EventToValidate = TrackerEvent & EventAbstractDiscriminators;

/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractEvent, AbstractGlobalContext, AbstractLocationContext } from '@objectiv/schema';
import { RecordedEventsInterface } from './RecordedEventsInterface';
import { TrackerTransportInterface } from './TrackerTransportInterface';

/**
 * A version of AbstractLocationContext without its discriminatory properties.
 */
export type RecordedAbstractLocationContext = Omit<AbstractLocationContext, '__location_context' | '__instance_id'>;

/**
 * A version of AbstractGlobalContext without its discriminatory properties.
 */
export type RecordedAbstractGlobalContext = Omit<AbstractGlobalContext, '__global_context' | '__instance_id'>;

/**
 * A predictable AbstractEvent. It has no `time`, a predictable identifier and no discriminatory properties.
 * Its location_stack and global_contexts also don't have any discriminatory properties.
 */
export type RecordedEvent = Omit<AbstractEvent, 'time' | 'location_stack' | 'global_contexts'> & {
  location_stack: RecordedAbstractLocationContext[];
  global_contexts: RecordedAbstractGlobalContext[];
};

/**
 * EventRecording instances can store lists of TrackerEvents for snapshot-testing or other debugging purposes.
 */
export type EventRecorderConfig = {
  /**
   * When set to false it will cause EventRecorder to become unusable. Trackers will not automatically record events.
   */
  enabled?: boolean;

  /**
   * Determines how many TrackerEvents will be recorded before rotating the oldest ones. Default to 1000.
   */
  maxEvents?: number;

  /**
   * Whether EventRecorder will start recording automatically. Default to true.
   */
  autoStart?: boolean;
};

/**
 * EventRecording instances can store lists of TrackerEvents for snapshot-testing or other debugging purposes.
 */
export type EventRecorderInterface = TrackerTransportInterface &
  Required<EventRecorderConfig> & {
    /**
     * When set to false it will cause EventRecorder to become unusable. Trackers will not automatically record events.
     */
    enabled: boolean;

    /**
     * Whether EventRecorder is recording or not.
     */
    recording: boolean;

    /**
     * A list of recorded events wrapped in a RecordedEvents instance for easier querying.
     */
    events: RecordedEventsInterface;

    /**
     * Allows reconfiguring EventRecorder
     */
    configure: (eventRecorderConfig?: EventRecorderConfig) => void;

    /**
     * Completely resets EventRecorder state.
     */
    clear: () => void;

    /**
     * Starts recording events.
     */
    start: () => void;

    /**
     * Stops recording events.
     */
    stop: () => void;
  };

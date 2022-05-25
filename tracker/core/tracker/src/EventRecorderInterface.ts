/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractEvent } from '@objectiv/schema';
import { TrackerTransportInterface } from './TrackerTransportInterface';

/**
 * A predictable AbstractEvent. It has no `time` and a predictable identifier.
 */
export type RecordedEvent = Omit<AbstractEvent, 'time'>;

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
     * Holds the list of recorded events.
     */
    events: RecordedEvent[];

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

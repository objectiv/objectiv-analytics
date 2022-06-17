/*
 * Copyright 2022 Objectiv B.V.
 */

export enum EventName {
  ApplicationLoadedEvent = 'ApplicationLoadedEvent',
  FailureEvent = 'FailureEvent',
  HiddenEvent = 'HiddenEvent',
  InputChangeEvent = 'InputChangeEvent',
  InteractiveEvent = 'InteractiveEvent',
  MediaEvent = 'MediaEvent',
  MediaLoadEvent = 'MediaLoadEvent',
  MediaPauseEvent = 'MediaPauseEvent',
  MediaStartEvent = 'MediaStartEvent',
  MediaStopEvent = 'MediaStopEvent',
  NonInteractiveEvent = 'NonInteractiveEvent',
  PressEvent = 'PressEvent',
  SuccessEvent = 'SuccessEvent',
  VisibleEvent = 'VisibleEvent',
}

export type AnyEventName =
  | 'ApplicationLoadedEvent'
  | 'FailureEvent'
  | 'HiddenEvent'
  | 'InputChangeEvent'
  | 'InteractiveEvent'
  | 'MediaEvent'
  | 'MediaLoadEvent'
  | 'MediaPauseEvent'
  | 'MediaStartEvent'
  | 'MediaStopEvent'
  | 'NonInteractiveEvent'
  | 'PressEvent'
  | 'SuccessEvent'
  | 'VisibleEvent';

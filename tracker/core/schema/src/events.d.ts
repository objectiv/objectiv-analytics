/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractInteractiveEvent, AbstractNonInteractiveEvent, AbstractMediaEvent } from './abstracts';

/**
 * The parent of Events that are the direct result of a user interaction, e.g. a button click.
 * Inheritance: InteractiveEvent -> AbstractInteractiveEvent -> AbstractEvent
 */
export interface InteractiveEvent extends AbstractInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'InteractiveEvent';
}

/**
 * The parent of Events that are not directly triggered by a user action.
 * Inheritance: NonInteractiveEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface NonInteractiveEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'NonInteractiveEvent';
}

/**
 * A NonInteractive event that is emitted after an application (eg. SPA) has finished loading.
 * Inheritance: ApplicationLoadedEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface ApplicationLoadedEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ApplicationLoadedEvent';
}

/**
 * A NonInteractiveEvent that is sent when a user action results in a error,
 * like an invalid email when sending a form.
 * Inheritance: FailureEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface FailureEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'FailureEvent';

  /**
   * Failure message.
   */
  message: string;
}

/**
 * Event triggered when user input is modified.
 * Inheritance: InputChangeEvent -> AbstractInteractiveEvent -> AbstractEvent
 */
export interface InputChangeEvent extends AbstractInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'InputChangeEvent';
}

/**
 * An InteractiveEvent that is sent when a user presses on a pressable element
 * (like a link, button, icon).
 * Inheritance: PressEvent -> AbstractInteractiveEvent -> AbstractEvent
 */
export interface PressEvent extends AbstractInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'PressEvent';
}

/**
 * A NonInteractiveEvent that's emitted after a LocationContext has become invisible.
 * Inheritance: HiddenEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface HiddenEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'HiddenEvent';
}

/**
 * A NonInteractiveEvent that's emitted after a section LocationContext has become visible.
 * Inheritance: VisibleEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface VisibleEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'VisibleEvent';
}

/**
 * A NonInteractiveEvent that is sent when a user action is successfully completed,
 * like sending an email form.
 * Inheritance: SuccessEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface SuccessEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'SuccessEvent';

  /**
   * Success message.
   */
  message: string;
}

/**
 * The parent of non-interactive events that are triggered by a media player.
 * It requires a MediaPlayerContext to detail the origin of the event.
 * Inheritance: MediaEvent -> AbstractMediaEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface MediaEvent extends AbstractMediaEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'MediaEvent';
}

/**
 * A MediaEvent that's emitted after a media item completes loading.
 * Inheritance: MediaLoadEvent -> AbstractMediaEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface MediaLoadEvent extends AbstractMediaEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'MediaLoadEvent';
}

/**
 * A MediaEvent that's emitted after a media item pauses playback.
 * Inheritance: MediaPauseEvent -> AbstractMediaEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface MediaPauseEvent extends AbstractMediaEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'MediaPauseEvent';
}

/**
 * A MediaEvent that's emitted after a media item starts playback.
 * Inheritance: MediaStartEvent -> AbstractMediaEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface MediaStartEvent extends AbstractMediaEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'MediaStartEvent';
}

/**
 * A MediaEvent that's emitted after a media item stops playback.
 * Inheritance: MediaStopEvent -> AbstractMediaEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface MediaStopEvent extends AbstractMediaEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'MediaStopEvent';
}

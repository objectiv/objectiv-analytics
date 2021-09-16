import { AbstractNonInteractiveEvent, AbstractVideoEvent, AbstractInteractiveEvent } from './abstracts';

/**
 * Non interactive events, are events that are not (directly) triggered by an interaction. For example:
 * Consider the following flow of events:
 * 1. press play in a video player -> ButtonEvent -> interactive
 * 2. Videoplayer starting playback -> MediaStartEvent -> non-interactive
 * Inheritance: NonInteractiveEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface NonInteractiveEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'NonInteractiveEvent';
}

/**
 * A non interactive event that is emitted after a document finishes loading. It should provide a
 * `WebDocumentContext` which should describe the state (eg. URL) of the event.
 * NOTE: with SPA's this probably only happens once, as page (re)loads don't happen after the initial page load
 * Inheritance: DocumentLoadedEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface DocumentLoadedEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'DocumentLoadedEvent';
}

/**
 * non interactive event that is emitted when the URL of a page has changed. Also contains a `WebDocumentContext`
 * that details the change.
 * Inheritance: URLChangeEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface URLChangeEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'URLChangeEvent';
}

/**
 * non interactive event that is emitted after an application (eg. SPA) has finished loading.
 * Contains a `SectionContext`
 * Inheritance: ApplicationLoadedEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface ApplicationLoadedEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ApplicationLoadedEvent';
}

/**
 * Non interactive event, emitted after a section (`SectionContext`) has become visible.
 * Inheritance: SectionVisibleEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface SectionVisibleEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'SectionVisibleEvent';
}

/**
 * Non interactive event, emitted after a section (`SectionContext`) has become invisible.
 * Inheritance: SectionHiddenEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface SectionHiddenEvent extends AbstractNonInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'SectionHiddenEvent';
}

/**
 * Family of non interactive events triggered by a video player
 * Inheritance: VideoEvent -> AbstractVideoEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface VideoEvent extends AbstractVideoEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'VideoEvent';
}

/**
 * Event emitted after a video completes loading.
 * Inheritance: VideoLoadEvent -> AbstractVideoEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface VideoLoadEvent extends AbstractVideoEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'VideoLoadEvent';
}

/**
 * Event emitted after a video starts playback.
 * Inheritance: VideoStartEvent -> AbstractVideoEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface VideoStartEvent extends AbstractVideoEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'VideoStartEvent';
}

/**
 * Event emitted after a video stops playback.
 * Inheritance: VideoStopEvent -> AbstractVideoEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface VideoStopEvent extends AbstractVideoEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'VideoStopEvent';
}

/**
 * Event emitted after a video pauses playback (toggle).
 * Inheritance: VideoPauseEvent -> AbstractVideoEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface VideoPauseEvent extends AbstractVideoEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'VideoPauseEvent';
}

/**
 * Events that are the direct result of a user interaction. Eg. a Button Click
 * Inheritance: InteractiveEvent -> AbstractInteractiveEvent -> AbstractEvent
 */
export interface InteractiveEvent extends AbstractInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'InteractiveEvent';
}

/**
 * Event triggered by a user clicking on an element
 * Inheritance: ClickEvent -> AbstractInteractiveEvent -> AbstractEvent
 */
export interface ClickEvent extends AbstractInteractiveEvent {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ClickEvent';
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

import {
  ApplicationLoadedEvent,
  ClickEvent,
  DocumentLoadedEvent,
  InputChangeEvent,
  SectionHiddenEvent,
  SectionVisibleEvent,
  URLChangedEvent,
  VideoEvent,
  VideoLoadEvent,
  VideoPauseEvent,
  VideoStartEvent,
  VideoStopEvent,
} from '@objectiv/schema';
import { ContextsConfig } from './Context';

/**
 * DocumentLoadedEvent factory
 */
export const makeDocumentLoadedEvent = (props?: ContextsConfig): DocumentLoadedEvent => ({
  _interactive_event: false,
  event: 'DocumentLoadedEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * URLChangedEvent factory
 */
export const makeURLChangedEvent = (props?: ContextsConfig): URLChangedEvent => ({
  _interactive_event: false,
  event: 'URLChangedEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * ApplicationLoadedEvent factory
 */
export const makeApplicationLoadedEvent = (props?: ContextsConfig): ApplicationLoadedEvent => ({
  _interactive_event: false,
  event: 'ApplicationLoadedEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * SectionVisibleEvent factory
 */
export const makeSectionVisibleEvent = (props?: ContextsConfig): SectionVisibleEvent => ({
  _interactive_event: false,
  event: 'SectionVisibleEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * SectionHiddenEvent factory
 */
export const makeSectionHiddenEvent = (props?: ContextsConfig): SectionHiddenEvent => ({
  _interactive_event: false,
  event: 'SectionHiddenEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * VideoEvent factory
 */
export const makeVideoEvent = (props?: ContextsConfig): VideoEvent => ({
  _interactive_event: false,
  _video_event: true,
  event: 'VideoEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * VideoLoadEvent factory
 */
export const makeVideoLoadEvent = (props?: ContextsConfig): VideoLoadEvent => ({
  _interactive_event: false,
  _video_event: true,
  event: 'VideoLoadEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * VideoStartEvent factory
 */
export const makeVideoStartEvent = (props?: ContextsConfig): VideoStartEvent => ({
  _interactive_event: false,
  _video_event: true,
  event: 'VideoStartEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * VideoStopEvent factory
 */
export const makeVideoStopEvent = (props?: ContextsConfig): VideoStopEvent => ({
  _interactive_event: false,
  _video_event: true,
  event: 'VideoStopEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * VideoPauseEvent factory
 */
export const makeVideoPauseEvent = (props?: ContextsConfig): VideoPauseEvent => ({
  _interactive_event: false,
  _video_event: true,
  event: 'VideoPauseEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * ClickEvent factory
 */
export const makeClickEvent = (props?: ContextsConfig): ClickEvent => ({
  _interactive_event: true,
  event: 'ClickEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

/**
 * ClickEvent factory
 */
export const makeInputChangeEvent = (props?: ContextsConfig): InputChangeEvent => ({
  _interactive_event: true,
  event: 'InputChangeEvent',
  globalContexts: props?.globalContexts ?? [],
  locationStack: props?.locationStack ?? [],
});

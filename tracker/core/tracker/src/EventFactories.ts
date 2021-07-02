import {
  ApplicationLoadedEvent,
  ClickEvent,
  DocumentLoadedEvent,
  InputChangeEvent,
  InteractiveEvent,
  NonInteractiveEvent,
  SectionHiddenEvent,
  SectionVisibleEvent,
  URLChangeEvent,
  VideoEvent,
  VideoLoadEvent,
  VideoPauseEvent,
  VideoStartEvent,
  VideoStopEvent,
  AbstractLocationContext,
  AbstractGlobalContext,
} from '@objectiv/schema';
export const makeApplicationLoadedEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): ApplicationLoadedEvent => ({
  __non_interactive_event: true,
  event: 'ApplicationLoadedEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeClickEvent = (props: {
  location_stack: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): ClickEvent => ({
  __interactive_event: true,
  event: 'ClickEvent',
  location_stack: props.location_stack,
  global_contexts: props?.global_contexts ?? [],
});
export const makeDocumentLoadedEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): DocumentLoadedEvent => ({
  __non_interactive_event: true,
  event: 'DocumentLoadedEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeInputChangeEvent = (props: {
  location_stack: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): InputChangeEvent => ({
  __interactive_event: true,
  event: 'InputChangeEvent',
  location_stack: props.location_stack,
  global_contexts: props?.global_contexts ?? [],
});
export const makeInteractiveEvent = (props: {
  location_stack: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): InteractiveEvent => ({
  __interactive_event: true,
  event: 'InteractiveEvent',
  location_stack: props.location_stack,
  global_contexts: props?.global_contexts ?? [],
});
export const makeNonInteractiveEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): NonInteractiveEvent => ({
  __non_interactive_event: true,
  event: 'NonInteractiveEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeSectionHiddenEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): SectionHiddenEvent => ({
  __non_interactive_event: true,
  event: 'SectionHiddenEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeSectionVisibleEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): SectionVisibleEvent => ({
  __non_interactive_event: true,
  event: 'SectionVisibleEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeURLChangeEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): URLChangeEvent => ({
  __non_interactive_event: true,
  event: 'URLChangeEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeVideoEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): VideoEvent => ({
  __non_interactive_event: true,
  __video_event: true,
  event: 'VideoEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeVideoLoadEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): VideoLoadEvent => ({
  __non_interactive_event: true,
  __video_event: true,
  event: 'VideoLoadEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeVideoPauseEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): VideoPauseEvent => ({
  __non_interactive_event: true,
  __video_event: true,
  event: 'VideoPauseEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeVideoStartEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): VideoStartEvent => ({
  __non_interactive_event: true,
  __video_event: true,
  event: 'VideoStartEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});
export const makeVideoStopEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): VideoStopEvent => ({
  __non_interactive_event: true,
  __video_event: true,
  event: 'VideoStopEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

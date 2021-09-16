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

/** Creates instance of ApplicationLoadedEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<ApplicationLoadedEvent, 'id' | 'time'>} - ApplicationLoadedEvent: non interactive event that is emitted after an application (eg. SPA) has finished loading.
 * 	Contains a `SectionContext`
 */
export const makeApplicationLoadedEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<ApplicationLoadedEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'ApplicationLoadedEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of ClickEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<ClickEvent, 'id' | 'time'>} - ClickEvent: Event triggered by a user clicking on an element
 */
export const makeClickEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<ClickEvent, 'id' | 'time'> => ({
  __interactive_event: true,
  _type: 'ClickEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of DocumentLoadedEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<DocumentLoadedEvent, 'id' | 'time'>} - DocumentLoadedEvent: A non interactive event that is emitted after a document finishes loading. It should provide a
 * 	`WebDocumentContext` which should describe the state (eg. URL) of the event.
 * 	NOTE: with SPA's this probably only happens once, as page (re)loads don't happen after the initial page load
 */
export const makeDocumentLoadedEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<DocumentLoadedEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'DocumentLoadedEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of InputChangeEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<InputChangeEvent, 'id' | 'time'>} - InputChangeEvent: Event triggered when user input is modified.
 */
export const makeInputChangeEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<InputChangeEvent, 'id' | 'time'> => ({
  __interactive_event: true,
  _type: 'InputChangeEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of InteractiveEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<InteractiveEvent, 'id' | 'time'>} - InteractiveEvent: Events that are the direct result of a user interaction. Eg. a Button Click
 */
export const makeInteractiveEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<InteractiveEvent, 'id' | 'time'> => ({
  __interactive_event: true,
  _type: 'InteractiveEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of NonInteractiveEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<NonInteractiveEvent, 'id' | 'time'>} - NonInteractiveEvent: Non interactive events, are events that are not (directly) triggered by an interaction. For example:
 * 	Consider the following flow of events:
 * 	1. press play in a video player -> ButtonEvent -> interactive
 * 	2. Videoplayer starting playback -> MediaStartEvent -> non-interactive
 */
export const makeNonInteractiveEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<NonInteractiveEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'NonInteractiveEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of SectionHiddenEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<SectionHiddenEvent, 'id' | 'time'>} - SectionHiddenEvent: Non interactive event, emitted after a section (`SectionContext`) has become invisible.
 */
export const makeSectionHiddenEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<SectionHiddenEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'SectionHiddenEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of SectionVisibleEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<SectionVisibleEvent, 'id' | 'time'>} - SectionVisibleEvent: Non interactive event, emitted after a section (`SectionContext`) has become visible.
 */
export const makeSectionVisibleEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<SectionVisibleEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'SectionVisibleEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of URLChangeEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<URLChangeEvent, 'id' | 'time'>} - URLChangeEvent: non interactive event that is emitted when the URL of a page has changed. Also contains a `WebDocumentContext`
 * 	that details the change.
 */
export const makeURLChangeEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<URLChangeEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'URLChangeEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of VideoEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<VideoEvent, 'id' | 'time'>} - VideoEvent: Family of non interactive events triggered by a video player
 */
export const makeVideoEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<VideoEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __video_event: true,
  _type: 'VideoEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of VideoLoadEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<VideoLoadEvent, 'id' | 'time'>} - VideoLoadEvent: Event emitted after a video completes loading.
 */
export const makeVideoLoadEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<VideoLoadEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __video_event: true,
  _type: 'VideoLoadEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of VideoPauseEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<VideoPauseEvent, 'id' | 'time'>} - VideoPauseEvent: Event emitted after a video pauses playback (toggle).
 */
export const makeVideoPauseEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<VideoPauseEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __video_event: true,
  _type: 'VideoPauseEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of VideoStartEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<VideoStartEvent, 'id' | 'time'>} - VideoStartEvent: Event emitted after a video starts playback.
 */
export const makeVideoStartEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<VideoStartEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __video_event: true,
  _type: 'VideoStartEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of VideoStopEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<VideoStopEvent, 'id' | 'time'>} - VideoStopEvent: Event emitted after a video stops playback.
 */
export const makeVideoStopEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<VideoStopEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __video_event: true,
  _type: 'VideoStopEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

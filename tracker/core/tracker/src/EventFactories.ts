/*
 * Copyright 2022 Objectiv B.V.
 */

import {
  ApplicationLoadedEvent,
  FailureEvent,
  HiddenEvent,
  InputChangeEvent,
  InteractiveEvent,
  MediaEvent,
  MediaLoadEvent,
  MediaPauseEvent,
  MediaStartEvent,
  MediaStopEvent,
  NonInteractiveEvent,
  PressEvent,
  SuccessEvent,
  VisibleEvent,
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
 * @returns {Omit<ApplicationLoadedEvent, 'id' | 'time'>} - ApplicationLoadedEvent: A NonInteractive event that is emitted after an application (eg. SPA) has finished loading.
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

/** Creates instance of FailureEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @param {string} props.message - Failure message.
 * @returns {Omit<FailureEvent, 'id' | 'time'>} - FailureEvent: A NonInteractiveEvent that is sent when a user action results in a error,
 * 	like an invalid email when sending a form.
 */
export const makeFailureEvent = (props: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
  message: string;
}): Omit<FailureEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'FailureEvent',
  location_stack: props.location_stack ?? [],
  global_contexts: props.global_contexts ?? [],
  message: props.message,
});

/** Creates instance of HiddenEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<HiddenEvent, 'id' | 'time'>} - HiddenEvent: A NonInteractiveEvent that's emitted after a LocationContext has become invisible.
 */
export const makeHiddenEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<HiddenEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'HiddenEvent',
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
 * @returns {Omit<InteractiveEvent, 'id' | 'time'>} - InteractiveEvent: The parent of Events that are the direct result of a user interaction, e.g. a button click.
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

/** Creates instance of MediaEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<MediaEvent, 'id' | 'time'>} - MediaEvent: The parent of non-interactive events that are triggered by a media player.
 * 	It requires a MediaPlayerContext to detail the origin of the event.
 */
export const makeMediaEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<MediaEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __media_event: true,
  _type: 'MediaEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of MediaLoadEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<MediaLoadEvent, 'id' | 'time'>} - MediaLoadEvent: A MediaEvent that's emitted after a media item completes loading.
 */
export const makeMediaLoadEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<MediaLoadEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __media_event: true,
  _type: 'MediaLoadEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of MediaPauseEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<MediaPauseEvent, 'id' | 'time'>} - MediaPauseEvent: A MediaEvent that's emitted after a media item pauses playback.
 */
export const makeMediaPauseEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<MediaPauseEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __media_event: true,
  _type: 'MediaPauseEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of MediaStartEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<MediaStartEvent, 'id' | 'time'>} - MediaStartEvent: A MediaEvent that's emitted after a media item starts playback.
 */
export const makeMediaStartEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<MediaStartEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __media_event: true,
  _type: 'MediaStartEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of MediaStopEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<MediaStopEvent, 'id' | 'time'>} - MediaStopEvent: A MediaEvent that's emitted after a media item stops playback.
 */
export const makeMediaStopEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<MediaStopEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  __media_event: true,
  _type: 'MediaStopEvent',
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
 * @returns {Omit<NonInteractiveEvent, 'id' | 'time'>} - NonInteractiveEvent: The parent of Events that are not directly triggered by a user action.
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

/** Creates instance of PressEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<PressEvent, 'id' | 'time'>} - PressEvent: An InteractiveEvent that is sent when a user presses on a pressable element
 * 	(like a link, button, icon).
 */
export const makePressEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<PressEvent, 'id' | 'time'> => ({
  __interactive_event: true,
  _type: 'PressEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

/** Creates instance of SuccessEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @param {string} props.message - Success message.
 * @returns {Omit<SuccessEvent, 'id' | 'time'>} - SuccessEvent: A NonInteractiveEvent that is sent when a user action is successfully completed,
 * 	like sending an email form.
 */
export const makeSuccessEvent = (props: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
  message: string;
}): Omit<SuccessEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'SuccessEvent',
  location_stack: props.location_stack ?? [],
  global_contexts: props.global_contexts ?? [],
  message: props.message,
});

/** Creates instance of VisibleEvent
 * @param {Object} props - factory properties
 * @param {AbstractLocationContext[]} props.location_stack - The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
 *         deterministically describes where an event took place from global to specific.
 *         The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
 * @param {AbstractGlobalContext[]} props.global_contexts - Global contexts add global / general information about the event. They carry information that is not
 *         related to where the Event originated (location), such as device, platform or business data.
 * @returns {Omit<VisibleEvent, 'id' | 'time'>} - VisibleEvent: A NonInteractiveEvent that's emitted after a section LocationContext has become visible.
 */
export const makeVisibleEvent = (props?: {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
}): Omit<VisibleEvent, 'id' | 'time'> => ({
  __non_interactive_event: true,
  _type: 'VisibleEvent',
  location_stack: props?.location_stack ?? [],
  global_contexts: props?.global_contexts ?? [],
});

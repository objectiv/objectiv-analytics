/*
 * Copyright 2022 Objectiv B.V.
 */

/**
 * This is the abstract parent of all Events.
 * Inheritance: AbstractEvent
 */
export abstract class AbstractEvent {
  /**
   * The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
   *deterministically describes where an event took place from global to specific.
   *The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
   */
  location_stack: AbstractLocationContext[];

  /**
   * Global contexts add global / general information about the event. They carry information that is not
   *related to where the Event originated (location), such as device, platform or business data.
   */
  global_contexts: AbstractGlobalContext[];

  /**
   * String containing the name of the event type. (eg. ClickEvent).
   */
  _type: string;

  /**
   * Unique identifier for a specific instance of an event. Typically UUID's are a good way of
   *implementing this. On the collector side, events should be unique, this means duplicate id's result
   *in `not ok` events.
   */
  id: string;

  /**
   * Timestamp indicating when the event was generated.
   */
  time: number;
}

/**
 * AbstractContext defines the bare minimum properties for every Context. All Contexts inherit from it.
 * Inheritance: AbstractContext
 */
export abstract class AbstractContext {
  /**
   * A unique identifier to discriminate Context instances across Location Stacks.
   */
  __instance_id: string;

  /**
   * A unique string identifier to be combined with the Context Type (`_type`)
   *for Context instance uniqueness.
   */
  id: string;

  /**
   * A string literal used during serialization. Should always match the Context interface name.
   */
  _type: string;
}

/**
 * This is the abstract parent of all Global Contexts. Global contexts add general information to an Event.
 * Inheritance: AbstractGlobalContext -> AbstractContext
 */
export abstract class AbstractGlobalContext extends AbstractContext {
  readonly __global_context = true;
}

/**
 * AbstractLocationContext are the abstract parents of all Location Contexts.
 * Location Contexts are meant to describe where an event originated from in the visual UI.
 * Inheritance: AbstractLocationContext -> AbstractContext
 */
export abstract class AbstractLocationContext extends AbstractContext {
  readonly __location_context = true;
}

/**
 *
 * Inheritance: AbstractNonInteractiveEvent -> AbstractEvent
 */
export abstract class AbstractNonInteractiveEvent extends AbstractEvent {
  readonly __non_interactive_event = true;
}

/**
 *
 * Inheritance: AbstractInteractiveEvent -> AbstractEvent
 */
export abstract class AbstractInteractiveEvent extends AbstractEvent {
  readonly __interactive_event = true;
}

/**
 *
 * Inheritance: AbstractMediaEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export abstract class AbstractMediaEvent extends AbstractNonInteractiveEvent {
  readonly __media_event = true;
}

/**
 *
 * Inheritance: AbstractPressableContext -> AbstractLocationContext -> AbstractContext
 */
export abstract class AbstractPressableContext extends AbstractLocationContext {
  readonly __pressable_context = true;
}

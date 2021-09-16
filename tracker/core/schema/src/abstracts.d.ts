/**
 * Events must provide a `name` and optionally can, but most likely will, carry a list of Location and Global
 * Contexts. Additionally, every event must have an `ApplicationContext` to be able to distinguish from what
 * application the event originated.
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
   * String containing the name of the event type. (eg. ClickEvent)
   */
  _type: string;

  /**
   * Unique identifier for a specific instance of an event. Typically UUID's are a good way of
   *implementing this. On the collector side, events should be unique, this means duplicate id's result
   *in `not ok` events.
   */
  id: string;

  /**
   * Timestamp indicating when the event was generated
   */
  time: number;
}

/**
 * Abstract Contexts define either properties required by Collectors or internal ones for hierarchical
 * discrimination purposes.
 * All Contexts inherit from AbstractContext. It defines the bare minimum properties every Context must implement.
 * For example we never want to mix Location Contexts with Global Contexts and Events may requires specific Contexts
 * to be present in their Location Stack. Eg. a NavigationContext instead of a generic SectionContext.
 * This ensures that Events are carrying the Contexts they require, making them meaningful and identifiable.
 * All Contexts inherit from AbstractContext. It defines the bare minimum properties every Context must implement.
 * Inheritance: AbstractContext
 */
export abstract class AbstractContext {
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
 * This is the abstract parent of all location contexts. LocationContexts are used to populate Trackers or Events
 * `location_stack` properties. A Location Stack is meant to describe accurately where an Event originated in the
 * UI Eg. Sections, Menus, etc.
 * Inheritance: AbstractLocationContext -> AbstractContext
 */
export abstract class AbstractLocationContext extends AbstractContext {
  readonly __location_context = true;
}

/**
 * Global_contexts are used to populate Trackers or Events `global_contexts` properties. They carry information
 * that is not related to where the Event originated, such as device, platform or business data.
 * Inheritance: AbstractGlobalContext -> AbstractContext
 */
export abstract class AbstractGlobalContext extends AbstractContext {
  readonly __global_context = true;
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
 * Inheritance: AbstractVideoEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export abstract class AbstractVideoEvent extends AbstractNonInteractiveEvent {
  readonly __video_event = true;
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
 * Inheritance: AbstractSectionContext -> AbstractLocationContext -> AbstractContext
 */
export abstract class AbstractSectionContext extends AbstractLocationContext {
  readonly __section_context = true;
}

/**
 *
 * Inheritance: AbstractItemContext -> AbstractLocationContext -> AbstractContext
 */
export abstract class AbstractItemContext extends AbstractLocationContext {
  readonly __item_context = true;
}

/**
 *
 * Inheritance: AbstractActionContext -> AbstractItemContext -> AbstractLocationContext -> AbstractContext
 */
export abstract class AbstractActionContext extends AbstractItemContext {
  readonly __action_context = true;

  /**
   * The text of the interactive element or, for visuals, a string describing it
   */
  text: string;
}

/**
 * Abstract Contexts define either properties required by Collectors or internal ones for hierarchical discrimination
 * purposes.
 *
 * For example we never want to mix Location Contexts with Global Contexts and Events may requires specific Contexts
 * to be present in their Location Stack. Eg. a NavigationContext instead of a generic SectionContext.
 *
 * This ensures that Events are carrying the Contexts they require, making them meaningful and identifiable.
 *
 * TypeScript does not support multiple inheritance, thus we use property based discrimination instead.
 * For more info: https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions
 */

/**
 * All Contexts inherit from AbstractContext. It defines the bare minimum properties every Context must implement.
 *
 * Extending interfaces should narrow `_context_type` type from string to a string literal matching the interface name.
 *
 * Examples:
 *   readonly _context_type: 'SectionContext';
 *   readonly _context_type: 'DeviceContext';
 */
export abstract class AbstractContext {
  /**
   * A string literal used during serialization. Should always match the Context interface name.
   */
  readonly _context_type: string;

  /**
   * A unique string identifier to be combined with `_context_type` for Context instance uniqueness.
   */
  readonly id: string;
}

/**
 * GlobalContexts are used to populate Trackers or Events `globalContexts` properties.
 * They carry information that is not related to where the Event originated, such as device, platform or business data.
 */
export abstract class AbstractGlobalContext extends AbstractContext {
  /**
   * Discrimination property
   */
  readonly _global_context = true;
}

/**
 * LocationContexts are used to populate Trackers or Events `locationStack` properties.
 * A Location Stack is meant to describe accurately where an Event originated. Eg. Sections, Menus, etc.
 */
export abstract class AbstractLocationContext extends AbstractContext {
  /**
   * Discrimination property
   */
  readonly _location_context = true;
}

/**
 * SectionContexts are special LocationContexts representing a logical area of the UI or the system.
 * They can be often reasoned about as being containers of other LocationContexts but not the direct targets of Events.
 */
export abstract class AbstractSectionContext extends AbstractLocationContext {
  /**
   * Discrimination property
   */
  readonly _section_context = true;
}

/**
 * ItemContexts are special LocationContexts representing interactive elements of the UI or targets in a system.
 * These elements may trigger both Interactive and Non-Interactive Events. Eg. an Input field or a Button.
 */
export abstract class AbstractItemContext extends AbstractLocationContext {
  /**
   * Discrimination property
   */
  readonly _item_context = true;
}

/**
 * ActionContexts are a more specific version of ItemContext specifically meant to describe actionable Items.
 * These represent interactive elements that will trigger an Interactive Event. Eg. A Button or Link.
 */
export abstract class AbstractActionContext extends AbstractItemContext {
  /**
   * Discrimination property
   */
  readonly _action_context = true;

  /**
   * A string representing where the action will lead to
   * TODO: make this optional when OSF will support that
   */
  path: string;

  /**
   * The text of the interactive element or, for visuals, a string describing it
   */
  text: string;
}

/**
 * An interface coupling Location Stack and Global Contexts. Used by Tracker and Events.
 */
export interface Contexts {
  /**
   * A list of Location Contexts. Order matters as they must reconstruct a logical location in the UI or system.
   */
  readonly locationStack: AbstractLocationContext[];

  /**
   * A list of Global Contexts. In any order.
   */
  readonly globalContexts: AbstractGlobalContext[];
}

/**
 * Events must provide a `name` and optionally can, but most likely will, carry a list of Location and Global Contexts
 */
export abstract class AbstractEvent implements Contexts {
  /**
   * A string literal used during serialization. Should always match the Event interface name.
   */
  readonly event: string;

  /**
   * The Contexts interface implementation
   */
  readonly locationStack: AbstractLocationContext[];
  readonly globalContexts: AbstractGlobalContext[];
}

/**
 * Events that are not triggered directly by the user. Eg. asynchronous or automatic ones.
 */
export abstract class AbstractNonInteractiveEvent extends AbstractEvent {
  /**
   * Discrimination property
   */
  readonly _interactive_event = false;
}

/**
 * Events that are the direct result of a user interaction. Eg. a Button Click
 */
export abstract class AbstractInteractiveEvent extends AbstractEvent {
  /**
   * Discrimination property
   */
  readonly _interactive_event = true;
}

/**
 * A category of Non Interactive Events specifically meant to describe Media Player interactions.
 */
export interface AbstractVideoEvent extends AbstractNonInteractiveEvent {
  /**
   * Discrimination property
   */
  readonly _video_event: true;
}

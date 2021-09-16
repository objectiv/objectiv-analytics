import { AbstractSectionContext, AbstractItemContext, AbstractActionContext } from './abstracts';

/**
 * SectionContexts are special LocationContexts representing a logical area of the UI or the system.
 * They can be often reasoned about as being containers of other LocationContexts but not the direct targets of
 * Events.
 * Inheritance: SectionContext -> AbstractSectionContext -> AbstractLocationContext -> AbstractContext
 */
export interface SectionContext extends AbstractSectionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'SectionContext';
}

/**
 * global context about a web document. Should at least contain the current URL.
 * Inheritance: WebDocumentContext -> AbstractSectionContext -> AbstractLocationContext -> AbstractContext
 */
export interface WebDocumentContext extends AbstractSectionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'WebDocumentContext';

  /**
   * Property containing a (valid) URL
   */
  url: string;
}

/**
 * SectionContext for a screen
 * Inheritance: ScreenContext -> AbstractSectionContext -> AbstractLocationContext -> AbstractContext
 */
export interface ScreenContext extends AbstractSectionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ScreenContext';

  /**
   * name of the screen
   */
  screen: string;
}

/**
 * A `SectionContext` that is expandable.
 * Inheritance: ExpandableSectionContext -> AbstractSectionContext -> AbstractLocationContext -> AbstractContext
 */
export interface ExpandableSectionContext extends AbstractSectionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ExpandableSectionContext';
}

/**
 * A `SectionContext` containing a media player.
 * Inheritance: MediaPlayerContext -> AbstractSectionContext -> AbstractLocationContext -> AbstractContext
 */
export interface MediaPlayerContext extends AbstractSectionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'MediaPlayerContext';
}

/**
 * A `SectionContext` containing navigational elements, for example a menu.
 * Inheritance: NavigationContext -> AbstractSectionContext -> AbstractLocationContext -> AbstractContext
 */
export interface NavigationContext extends AbstractSectionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'NavigationContext';
}

/**
 * A `SectionContext` that is an overlay
 * Inheritance: OverlayContext -> AbstractSectionContext -> AbstractLocationContext -> AbstractContext
 */
export interface OverlayContext extends AbstractSectionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'OverlayContext';
}

/**
 * ItemContexts are special LocationContexts representing interactive elements of the UI or targets in a system.
 * These elements may trigger both Interactive and Non-Interactive Events. Eg. an Input field or a Button.
 * Inheritance: ItemContext -> AbstractItemContext -> AbstractLocationContext -> AbstractContext
 */
export interface ItemContext extends AbstractItemContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ItemContext';
}

/**
 * A location context, representing user input. For example, a form field, like input.
 * Inheritance: InputContext -> AbstractItemContext -> AbstractLocationContext -> AbstractContext
 */
export interface InputContext extends AbstractItemContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'InputContext';
}

/**
 * ActionContexts are a more specific version of ItemContext specifically meant to describe actionable Items.
 * These represent interactive elements that will trigger an Interactive Event. Eg. A Button or Link.
 * Inheritance: ActionContext -> AbstractActionContext -> AbstractItemContext -> AbstractLocationContext -> AbstractContext
 */
export interface ActionContext extends AbstractActionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ActionContext';
}

/**
 * interactive element, representing a button.
 * Inheritance: ButtonContext -> AbstractActionContext -> AbstractItemContext -> AbstractLocationContext -> AbstractContext
 */
export interface ButtonContext extends AbstractActionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ButtonContext';
}

/**
 * interactive element, representing a (hyper) link.
 * Inheritance: LinkContext -> AbstractActionContext -> AbstractItemContext -> AbstractLocationContext -> AbstractContext
 */
export interface LinkContext extends AbstractActionContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'LinkContext';

  /**
   * URL (href) the link points to
   */
  href: string;
}

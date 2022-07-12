/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractLocationContext, AbstractPressableContext } from './abstracts';

/**
 * A Location Context that describes an element that accepts user input, i.e. a form field.
 * Inheritance: InputContext -> AbstractLocationContext -> AbstractContext
 */
export interface InputContext extends AbstractLocationContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'InputContext';
}

/**
 * An Location Context that describes an interactive element (like a link, button, icon),
 * that the user can press and will trigger an Interactive Event.
 * Inheritance: PressableContext -> AbstractPressableContext -> AbstractLocationContext -> AbstractContext
 */
export interface PressableContext extends AbstractPressableContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'PressableContext';
}

/**
 * A PressableContext that contains an href.
 * Inheritance: LinkContext -> AbstractPressableContext -> AbstractLocationContext -> AbstractContext
 */
export interface LinkContext extends AbstractPressableContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'LinkContext';

  /**
   * URL (href) the link points to.
   */
  href: string;
}

/**
 * A Location Context that uniquely represents the top-level UI location of the user.
 * Inheritance: RootLocationContext -> AbstractLocationContext -> AbstractContext
 */
export interface RootLocationContext extends AbstractLocationContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'RootLocationContext';
}

/**
 * A Location Context that describes a section of the UI that can expand & collapse.
 * Inheritance: ExpandableContext -> AbstractLocationContext -> AbstractContext
 */
export interface ExpandableContext extends AbstractLocationContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ExpandableContext';
}

/**
 * A Location Context that describes a section of the UI containing a media player.
 * Inheritance: MediaPlayerContext -> AbstractLocationContext -> AbstractContext
 */
export interface MediaPlayerContext extends AbstractLocationContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'MediaPlayerContext';
}

/**
 * A Location Context that describes a section of the UI containing navigational elements, for example a menu.
 * Inheritance: NavigationContext -> AbstractLocationContext -> AbstractContext
 */
export interface NavigationContext extends AbstractLocationContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'NavigationContext';
}

/**
 * A Location Context that describes a section of the UI that represents an overlay, i.e. a Modal.
 * Inheritance: OverlayContext -> AbstractLocationContext -> AbstractContext
 */
export interface OverlayContext extends AbstractLocationContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'OverlayContext';
}

/**
 * A Location Context that describes a logical section of the UI that contains other Location Contexts.
 * Enabling Data Science to analyze this section specifically.
 * Inheritance: ContentContext -> AbstractLocationContext -> AbstractContext
 */
export interface ContentContext extends AbstractLocationContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ContentContext';
}

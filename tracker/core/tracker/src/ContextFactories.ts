/*
 * Copyright 2021 Objectiv B.V.
 */

import {
  ActionContext,
  ApplicationContext,
  ButtonContext,
  CookieIdContext,
  ErrorContext,
  ExpandableSectionContext,
  HttpContext,
  InputContext,
  ItemContext,
  LinkContext,
  MediaPlayerContext,
  NavigationContext,
  OverlayContext,
  ScreenContext,
  SectionContext,
  SessionContext,
  WebDocumentContext,
} from '@objectiv/schema';

/** Creates instance of ActionContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.text - The text of the interactive element or, for visuals, a string describing it
 * @returns {ActionContext} - ActionContext: ActionContexts are a more specific version of ItemContext specifically meant to describe actionable Items.
 * 	These represent interactive elements that will trigger an Interactive Event. Eg. A Button or Link.
 */
export const makeActionContext = (props: { id: string; text: string }): ActionContext => ({
  __location_context: true,
  __item_context: true,
  __action_context: true,
  _type: 'ActionContext',
  id: props.id,
  text: props.text,
});

/** Creates instance of ApplicationContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {ApplicationContext} - ApplicationContext: Global context containing the origin (application id) of the event
 */
export const makeApplicationContext = (props: { id: string }): ApplicationContext => ({
  __global_context: true,
  _type: 'ApplicationContext',
  id: props.id,
});

/** Creates instance of ButtonContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.text - The text of the interactive element or, for visuals, a string describing it
 * @returns {ButtonContext} - ButtonContext: interactive element, representing a button.
 */
export const makeButtonContext = (props: { id: string; text: string }): ButtonContext => ({
  __location_context: true,
  __item_context: true,
  __action_context: true,
  _type: 'ButtonContext',
  id: props.id,
  text: props.text,
});

/** Creates instance of CookieIdContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.cookie_id - Unique identifier from the session cookie
 * @returns {CookieIdContext} - CookieIdContext: Global context with information needed to reconstruct a user session.
 */
export const makeCookieIdContext = (props: { id: string; cookie_id: string }): CookieIdContext => ({
  __global_context: true,
  _type: 'CookieIdContext',
  id: props.id,
  cookie_id: props.cookie_id,
});

/** Creates instance of ErrorContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.message - Error message
 * @returns {ErrorContext} - ErrorContext: Generic global context to encapsulate any errors
 */
export const makeErrorContext = (props: { id: string; message: string }): ErrorContext => ({
  __global_context: true,
  _type: 'ErrorContext',
  id: props.id,
  message: props.message,
});

/** Creates instance of ExpandableSectionContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {ExpandableSectionContext} - ExpandableSectionContext: A `SectionContext` that is expandable.
 */
export const makeExpandableSectionContext = (props: { id: string }): ExpandableSectionContext => ({
  __location_context: true,
  __section_context: true,
  _type: 'ExpandableSectionContext',
  id: props.id,
});

/** Creates instance of HttpContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.referer - Full URL to HTTP referrer of the current page.
 * @param {string} props.user_agent - User-agent of the agent that sent the event.
 * @param {string} props.remote_address - (public) IP address of the agent that sent the event.
 * @returns {HttpContext} - HttpContext: Global context with meta information about the agent that sent the event.
 */
export const makeHttpContext = (props: {
  id: string;
  referer: string;
  user_agent: string;
  remote_address: string;
}): HttpContext => ({
  __global_context: true,
  _type: 'HttpContext',
  id: props.id,
  referer: props.referer,
  user_agent: props.user_agent,
  remote_address: props.remote_address,
});

/** Creates instance of InputContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {InputContext} - InputContext: A location context, representing user input. For example, a form field, like input.
 */
export const makeInputContext = (props: { id: string }): InputContext => ({
  __location_context: true,
  __item_context: true,
  _type: 'InputContext',
  id: props.id,
});

/** Creates instance of ItemContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {ItemContext} - ItemContext: ItemContexts are special LocationContexts representing interactive elements of the UI or targets in a system.
 * 	These elements may trigger both Interactive and Non-Interactive Events. Eg. an Input field or a Button.
 */
export const makeItemContext = (props: { id: string }): ItemContext => ({
  __location_context: true,
  __item_context: true,
  _type: 'ItemContext',
  id: props.id,
});

/** Creates instance of LinkContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.text - The text of the interactive element or, for visuals, a string describing it
 * @param {string} props.href - URL (href) the link points to
 * @returns {LinkContext} - LinkContext: interactive element, representing a (hyper) link.
 */
export const makeLinkContext = (props: { id: string; text: string; href: string }): LinkContext => ({
  __location_context: true,
  __item_context: true,
  __action_context: true,
  _type: 'LinkContext',
  id: props.id,
  text: props.text,
  href: props.href,
});

/** Creates instance of MediaPlayerContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {MediaPlayerContext} - MediaPlayerContext: A `SectionContext` containing a media player.
 */
export const makeMediaPlayerContext = (props: { id: string }): MediaPlayerContext => ({
  __location_context: true,
  __section_context: true,
  _type: 'MediaPlayerContext',
  id: props.id,
});

/** Creates instance of NavigationContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {NavigationContext} - NavigationContext: A `SectionContext` containing navigational elements, for example a menu.
 */
export const makeNavigationContext = (props: { id: string }): NavigationContext => ({
  __location_context: true,
  __section_context: true,
  _type: 'NavigationContext',
  id: props.id,
});

/** Creates instance of OverlayContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {OverlayContext} - OverlayContext: A `SectionContext` that is an overlay
 */
export const makeOverlayContext = (props: { id: string }): OverlayContext => ({
  __location_context: true,
  __section_context: true,
  _type: 'OverlayContext',
  id: props.id,
});

/** Creates instance of ScreenContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.screen - name of the screen
 * @returns {ScreenContext} - ScreenContext: SectionContext for a screen
 */
export const makeScreenContext = (props: { id: string; screen: string }): ScreenContext => ({
  __location_context: true,
  __section_context: true,
  _type: 'ScreenContext',
  id: props.id,
  screen: props.screen,
});

/** Creates instance of SectionContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {SectionContext} - SectionContext: SectionContexts are special LocationContexts representing a logical area of the UI or the system.
 * 	They can be often reasoned about as being containers of other LocationContexts but not the direct targets of
 * 	Events.
 */
export const makeSectionContext = (props: { id: string }): SectionContext => ({
  __location_context: true,
  __section_context: true,
  _type: 'SectionContext',
  id: props.id,
});

/** Creates instance of SessionContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {number} props.hit_number - Hit counter relative to the current session, this event originated in.
 * @returns {SessionContext} - SessionContext: Context with meta info pertaining to the current session.
 */
export const makeSessionContext = (props: { id: string; hit_number: number }): SessionContext => ({
  __global_context: true,
  _type: 'SessionContext',
  id: props.id,
  hit_number: props.hit_number,
});

/** Creates instance of WebDocumentContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.url - Property containing a (valid) URL
 * @returns {WebDocumentContext} - WebDocumentContext: global context about a web document. Should at least contain the current URL.
 */
export const makeWebDocumentContext = (props: { id: string; url: string }): WebDocumentContext => ({
  __location_context: true,
  __section_context: true,
  _type: 'WebDocumentContext',
  id: props.id,
  url: props.url,
});

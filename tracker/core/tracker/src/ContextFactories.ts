import {
  ActionContext,
  ButtonContext,
  CookieIdContext,
  DeviceContext,
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

/**
 * SectionContext Factory
 */
export const makeSectionContext = (props: { id: string }): SectionContext => ({
  __location_context: true,
  __section_context: true,
  _context_type: 'SectionContext',
  id: props.id,
});

/**
 * WebDocumentContext Factory
 */
export const makeWebDocumentContext = (props: { id: string; url: string }): WebDocumentContext => ({
  __location_context: true,
  __section_context: true,
  _context_type: 'WebDocumentContext',
  id: props.id,
  url: props.url,
});

/**
 * ScreenContext Factory
 */
export const makeScreenContext = (props: { id: string; screen: string }): ScreenContext => ({
  __location_context: true,
  __section_context: true,
  _context_type: 'ScreenContext',
  id: props.id,
  screen: props.screen,
});

/**
 * ExpandableSectionContext Factory
 */
export const makeExpandableSectionContext = (props: { id: string }): ExpandableSectionContext => ({
  __location_context: true,
  __section_context: true,
  _context_type: 'ExpandableSectionContext',
  id: props.id,
});

/**
 * MediaPlayerContext Factory
 */
export const makeMediaPlayerContext = (props: { id: string }): MediaPlayerContext => ({
  __location_context: true,
  __section_context: true,
  _context_type: 'MediaPlayerContext',
  id: props.id,
});

/**
 * NavigationContext Factory
 */
export const makeNavigationContext = (props: { id: string }): NavigationContext => ({
  __location_context: true,
  __section_context: true,
  _context_type: 'NavigationContext',
  id: props.id,
});

/**
 * OverlayContext Factory
 */
export const makeOverlayContext = (props: { id: string }): OverlayContext => ({
  __location_context: true,
  __section_context: true,
  _context_type: 'OverlayContext',
  id: props.id,
});

/**
 * ItemContext Factory
 */
export const makeItemContext = (props: { id: string }): ItemContext => ({
  __location_context: true,
  __item_context: true,
  _context_type: 'ItemContext',
  id: props.id,
});

/**
 * InputContext Factory
 */
export const makeInputContext = (props: { id: string }): InputContext => ({
  __location_context: true,
  __item_context: true,
  _context_type: 'InputContext',
  id: props.id,
});

/**
 * ActionContext Factory
 */
export const makeActionContext = (props: { id: string; path: string; text: string }): ActionContext => ({
  __location_context: true,
  __item_context: true,
  __action_context: true,
  _context_type: 'ActionContext',
  id: props.id,
  path: props.path,
  text: props.text,
});

/**
 * ButtonContext Factory
 */
export const makeButtonContext = (props: { id: string; text: string }): ButtonContext => ({
  __location_context: true,
  __item_context: true,
  __action_context: true,
  _context_type: 'ButtonContext',
  id: props.id,
  path: '', // TODO OSF does not support optional properties; default to empty string. See also AbstractActionContext
  text: props.text,
});

/**
 * LinkContext Factory
 */
export const makeLinkContext = (props: { id: string; href: string; text: string }): LinkContext => ({
  __location_context: true,
  __item_context: true,
  __action_context: true,
  _context_type: 'LinkContext',
  id: props.id,
  path: props.href,
  text: props.text,
});

/**
 * DeviceContext Factory
 */
export const makeDeviceContext = (props: { userAgent: string }): DeviceContext => ({
  __global_context: true,
  _context_type: 'DeviceContext',
  id: 'device',
  'user-agent': props.userAgent,
});

/**
 * ErrorContext Factory
 */
export const makeErrorContext = (props: { id: string; message: string }): ErrorContext => ({
  __global_context: true,
  _context_type: 'ErrorContext',
  id: props.id,
  message: props.message,
});

/**
 * CookieIdContext Factory
 */
export const makeCookieIdContext = (props: { id: string; cookieId: string }): CookieIdContext => ({
  __global_context: true,
  _context_type: 'CookieIdContext',
  id: props.id,
  cookie_id: props.cookieId,
});

/**
 * SessionContext Factory
 */
export const makeSessionContext = (props: { id: string; hitNumber: number }): SessionContext => ({
  __global_context: true,
  _context_type: 'SessionContext',
  id: props.id,
  hitNumber: props.hitNumber,
});

/**
 * SessionContext Factory
 */
export const makeHttpContext = (props: {
  id: string;
  host: string;
  userAgent: string;
  remoteAddr: string;
}): HttpContext => ({
  __global_context: true,
  _context_type: 'HttpContext',
  id: props.id,
  host: props.host,
  'user-agent': props.userAgent,
  remoteAddr: props.remoteAddr,
});

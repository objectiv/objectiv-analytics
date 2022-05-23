/*
 * Copyright 2022 Objectiv B.V.
 */

import {
  ApplicationContext,
  ContentContext,
  CookieIdContext,
  ExpandableContext,
  HttpContext,
  InputContext,
  LinkContext,
  MarketingContext,
  MediaPlayerContext,
  NavigationContext,
  OverlayContext,
  PathContext,
  PressableContext,
  RootLocationContext,
  SessionContext,
} from '@objectiv/schema';
import { GlobalContextName, LocationContextName } from './ContextNames';
import { generateUUID } from './helpers';

/** Creates instance of ApplicationContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {ApplicationContext} - ApplicationContext: A GlobalContext describing in which app the event happens, like a website or iOS app.
 */
export const makeApplicationContext = (props: { id: string }): ApplicationContext => ({
  __instance_id: generateUUID(),
  __global_context: true,
  _type: GlobalContextName.ApplicationContext,
  id: props.id,
});

/** Creates instance of ContentContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {ContentContext} - ContentContext: A Location Context that describes a logical section of the UI that contains other Location Contexts. Enabling Data Science to analyze this section specifically.
 */
export const makeContentContext = (props: { id: string }): ContentContext => ({
  __instance_id: generateUUID(),
  __location_context: true,
  _type: LocationContextName.ContentContext,
  id: props.id,
});

/** Creates instance of CookieIdContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.cookie_id - Unique identifier from the session cookie
 * @returns {CookieIdContext} - CookieIdContext: Global context with information needed to reconstruct a user session.
 */
export const makeCookieIdContext = (props: { id: string; cookie_id: string }): CookieIdContext => ({
  __instance_id: generateUUID(),
  __global_context: true,
  _type: GlobalContextName.CookieIdContext,
  id: props.id,
  cookie_id: props.cookie_id,
});

/** Creates instance of ExpandableContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {ExpandableContext} - ExpandableContext: A Location Context that describes a section of the UI that can expand & collapse.
 */
export const makeExpandableContext = (props: { id: string }): ExpandableContext => ({
  __instance_id: generateUUID(),
  __location_context: true,
  _type: LocationContextName.ExpandableContext,
  id: props.id,
});

/** Creates instance of HttpContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.referrer - Full URL to HTTP referrer of the current page.
 * @param {string} props.user_agent - User-agent of the agent that sent the event.
 * @param {string | null} props.remote_address - (public) IP address of the agent that sent the event.
 * @returns {HttpContext} - HttpContext: A GlobalContext describing meta information about the agent that sent the event.
 */
export const makeHttpContext = (props: {
  id: string;
  referrer: string;
  user_agent: string;
  remote_address?: string | null;
}): HttpContext => ({
  __instance_id: generateUUID(),
  __global_context: true,
  _type: GlobalContextName.HttpContext,
  id: props.id,
  referrer: props.referrer,
  user_agent: props.user_agent,
  remote_address: props.remote_address ?? null,
});

/** Creates instance of InputContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {InputContext} - InputContext: A Location Context that describes an element that accepts user input, i.e. a form field.
 */
export const makeInputContext = (props: { id: string }): InputContext => ({
  __instance_id: generateUUID(),
  __location_context: true,
  _type: LocationContextName.InputContext,
  id: props.id,
});

/** Creates instance of LinkContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.href - URL (href) the link points to.
 * @returns {LinkContext} - LinkContext: A PressableContext that contains an href.
 */
export const makeLinkContext = (props: { id: string; href: string }): LinkContext => ({
  __instance_id: generateUUID(),
  __location_context: true,
  __pressable_context: true,
  _type: LocationContextName.LinkContext,
  id: props.id,
  href: props.href,
});

/** Creates instance of MarketingContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {string} props.source - Identifies the advertiser, site, publication, etc
 * @param {string} props.medium - Advertising or marketing medium: cpc, banner, email newsletter, etc
 * @param {string} props.campaign - Individual campaign name, slogan, promo code, etc
 * @param {string | null} props.term - [Optional] Search keywords
 * @param {string | null} props.content - [Optional] Used to differentiate similar content, or links within the same ad
 * @param {string | null} props.source_platform - [Optional] To differentiate similar content, or links within the same ad.
 * @param {string | null} props.creative_format - [Optional] Identifies the creative used (e.g., skyscraper, banner, etc).
 * @param {string | null} props.marketing_tactic - [Optional] Identifies the marketing tactic used (e.g., onboarding, retention, acquisition etc).
 * @returns {MarketingContext} - MarketingContext: a context that captures marketing channel info, so users can do attribution, campaign
 * 	effectiveness and other models
 */
export const makeMarketingContext = (props: {
  id: string;
  source: string;
  medium: string;
  campaign: string;
  term?: string | null;
  content?: string | null;
  source_platform?: string | null;
  creative_format?: string | null;
  marketing_tactic?: string | null;
}): MarketingContext => ({
  __instance_id: generateUUID(),
  __global_context: true,
  _type: GlobalContextName.MarketingContext,
  id: props.id,
  source: props.source,
  medium: props.medium,
  campaign: props.campaign,
  term: props.term ?? null,
  content: props.content ?? null,
  source_platform: props.source_platform ?? null,
  creative_format: props.creative_format ?? null,
  marketing_tactic: props.marketing_tactic ?? null,
});

/** Creates instance of MediaPlayerContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {MediaPlayerContext} - MediaPlayerContext: A Location Context that describes a section of the UI containing a media player.
 */
export const makeMediaPlayerContext = (props: { id: string }): MediaPlayerContext => ({
  __instance_id: generateUUID(),
  __location_context: true,
  _type: LocationContextName.MediaPlayerContext,
  id: props.id,
});

/** Creates instance of NavigationContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {NavigationContext} - NavigationContext: A Location Context that describes a section of the UI containing navigational elements, for example a menu.
 */
export const makeNavigationContext = (props: { id: string }): NavigationContext => ({
  __instance_id: generateUUID(),
  __location_context: true,
  _type: LocationContextName.NavigationContext,
  id: props.id,
});

/** Creates instance of OverlayContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {OverlayContext} - OverlayContext: A Location Context that describes a section of the UI that represents an overlay, i.e. a Modal.
 * 	.
 */
export const makeOverlayContext = (props: { id: string }): OverlayContext => ({
  __instance_id: generateUUID(),
  __location_context: true,
  _type: LocationContextName.OverlayContext,
  id: props.id,
});

/** Creates instance of PathContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {PathContext} - PathContext: A GlobalContext describing the path where the user is when an event is sent.
 */
export const makePathContext = (props: { id: string }): PathContext => ({
  __instance_id: generateUUID(),
  __global_context: true,
  _type: GlobalContextName.PathContext,
  id: props.id,
});

/** Creates instance of PressableContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {PressableContext} - PressableContext: An Location Context that describes an interactive element (like a link, button, icon),
 * 	that the user can press and will trigger an Interactive Event.
 */
export const makePressableContext = (props: { id: string }): PressableContext => ({
  __instance_id: generateUUID(),
  __location_context: true,
  __pressable_context: true,
  _type: LocationContextName.PressableContext,
  id: props.id,
});

/** Creates instance of RootLocationContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @returns {RootLocationContext} - RootLocationContext: A Location Context that uniquely represents the top-level UI location of the user.
 */
export const makeRootLocationContext = (props: { id: string }): RootLocationContext => ({
  __instance_id: generateUUID(),
  __location_context: true,
  _type: LocationContextName.RootLocationContext,
  id: props.id,
});

/** Creates instance of SessionContext
 * @param {Object} props - factory properties
 * @param {string} props.id - A unique string identifier to be combined with the Context Type (`_type`)
 *         for Context instance uniqueness.
 * @param {number} props.hit_number - Hit counter relative to the current session, this event originated in.
 * @returns {SessionContext} - SessionContext: A GlobalContext describing meta information about the current session.
 */
export const makeSessionContext = (props: { id: string; hit_number: number }): SessionContext => ({
  __instance_id: generateUUID(),
  __global_context: true,
  _type: GlobalContextName.SessionContext,
  id: props.id,
  hit_number: props.hit_number,
});

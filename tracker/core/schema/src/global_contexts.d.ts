/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractGlobalContext } from './abstracts';

/**
 * A GlobalContext describing in which app the event happens, like a website or iOS app.
 * Inheritance: ApplicationContext -> AbstractGlobalContext -> AbstractContext
 */
export interface ApplicationContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ApplicationContext';
}

/**
 * Global context with information needed to reconstruct a user session.
 * Inheritance: CookieIdContext -> AbstractGlobalContext -> AbstractContext
 */
export interface CookieIdContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'CookieIdContext';

  /**
   * Unique identifier from the session cookie.
   */
  cookie_id: string;
}

/**
 * A GlobalContext describing meta information about the agent that sent the event.
 * Inheritance: HttpContext -> AbstractGlobalContext -> AbstractContext
 */
export interface HttpContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'HttpContext';

  /**
   * Full URL to HTTP referrer of the current page.
   */
  referrer: string;

  /**
   * User-agent of the agent that sent the event.
   */
  user_agent: string;

  /**
   * (public) IP address of the agent that sent the event.
   */
  remote_address: string | null;
}

/**
 * A GlobalContext containing the value of a single input element. Multiple can be present.
 * Inheritance: InputValueContext -> AbstractGlobalContext -> AbstractContext
 */
export interface InputValueContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'InputValueContext';

  /**
   * The value of the input element.
   */
  value: string;
}

/**
 * A GlobalContext describing the locale used by the user. E.g. an ISO 639-1 code.
 * Inheritance: LocaleContext -> AbstractGlobalContext -> AbstractContext
 */
export interface LocaleContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'LocaleContext';
}

/**
 * A GlobalContext describing the path where the user is when an event is sent.
 * Inheritance: PathContext -> AbstractGlobalContext -> AbstractContext
 */
export interface PathContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'PathContext';
}

/**
 * A GlobalContext describing meta information about the current session.
 * Inheritance: SessionContext -> AbstractGlobalContext -> AbstractContext
 */
export interface SessionContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'SessionContext';

  /**
   * Hit counter relative to the current session, this event originated in.
   */
  hit_number: number;
}

/**
 * a context that captures marketing channel info, so users can do attribution, campaign
 * effectiveness and other models.
 * Inheritance: MarketingContext -> AbstractGlobalContext -> AbstractContext
 */
export interface MarketingContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'MarketingContext';

  /**
   * Identifies the advertiser, site, publication, etc.
   */
  source: string;

  /**
   * Advertising or marketing medium: cpc, banner, email newsletter, etc.
   */
  medium: string;

  /**
   * Individual campaign name, slogan, promo code, etc.
   */
  campaign: string;

  /**
   * [Optional] Search keywords.
   */
  term: string | null;

  /**
   * [Optional] Used to differentiate similar content, or links within the same ad.
   */
  content: string | null;

  /**
   * [Optional] To differentiate similar content, or links within the same ad.
   */
  source_platform: string | null;

  /**
   * [Optional] Identifies the creative used (e.g., skyscraper, banner, etc).
   */
  creative_format: string | null;

  /**
   * [Optional] Identifies the marketing tactic used (e.g., onboarding, retention, acquisition etc).
   */
  marketing_tactic: string | null;
}

/**
 * A Global Context to track the identity of users across sessions, platforms, devices. Multiple can be present.
 * The `id` field is used to specify the scope of identification e.g. backend, md5(email), supplier_cookie, etc.
 * The `value` field should contain the unique identifier within that scope.
 * Inheritance: IdentityContext -> AbstractGlobalContext -> AbstractContext
 */
export interface IdentityContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'IdentityContext';

  /**
   * The unique identifier for this user/group/entity within the scope defined by `id`.
   */
  value: string;
}

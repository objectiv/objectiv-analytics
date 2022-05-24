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
   * Unique identifier from the session cookie
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
 * effectiveness and other models
 * Inheritance: MarketingContext -> AbstractGlobalContext -> AbstractContext
 */
export interface MarketingContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'MarketingContext';

  /**
   * Identifies the advertiser, site, publication, etc
   */
  source: string;

  /**
   * Advertising or marketing medium: cpc, banner, email newsletter, etc
   */
  medium: string;

  /**
   * Individual campaign name, slogan, promo code, etc
   */
  campaign: string;

  /**
   * [Optional] Search keywords
   */
  term: string | null;

  /**
   * [Optional] Used to differentiate similar content, or links within the same ad
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

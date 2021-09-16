import { AbstractGlobalContext } from './abstracts';

/**
 * Global context containing the origin (application id) of the event
 * Inheritance: ApplicationContext -> AbstractGlobalContext -> AbstractContext
 */
export interface ApplicationContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ApplicationContext';
}

/**
 * Global context containing meta info about the device that emitted the event.
 * Inheritance: DeviceContext -> AbstractGlobalContext -> AbstractContext
 */
export interface DeviceContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'DeviceContext';

  /**
   * String describing the user-agent that emitted the event
   */
  user_agent: string;
}

/**
 * Generic global context to encapsulate any errors
 * Inheritance: ErrorContext -> AbstractGlobalContext -> AbstractContext
 */
export interface ErrorContext extends AbstractGlobalContext {
  /**
   * Typescript discriminator
   */
  readonly _type: 'ErrorContext';

  /**
   * Error message
   */
  message: string;
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
 * Context with meta info pertaining to the current session.
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
 * Global context with meta information about the agent that sent the event.
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
  referer: string;

  /**
   * User-agent of the agent that sent the event.
   */
  user_agent: string;

  /**
   * (public) IP address of the agent that sent the event.
   */
  remote_address: string;
}

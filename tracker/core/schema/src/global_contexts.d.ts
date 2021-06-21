import { AbstractGlobalContext } from './abstracts';

export interface DeviceContext extends AbstractGlobalContext {
  readonly _context_type: 'DeviceContext';
  readonly id: 'device';
  'user-agent': string;
}

export interface ErrorContext extends AbstractGlobalContext {
  readonly _context_type: 'ErrorContext';
  message: string;
}

export interface CookieIdContext extends AbstractGlobalContext {
  readonly _context_type: 'CookieIdContext';
  cookie_id: string;
}

export interface SessionContext extends AbstractGlobalContext {
  readonly _context_type: 'SessionContext';
  hitNumber: number;
}

export interface HttpContext extends AbstractGlobalContext {
  readonly _context_type: 'HttpContext';
  host: string;
  'user-agent': string;
  remoteAddr: string;
}

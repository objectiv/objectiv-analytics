import { AbstractGlobalContext, AbstractLocationContext } from '@objectiv/schema';

/**
 * The configuration of the Contexts interface
 */
export type ContextsConfig = {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
};

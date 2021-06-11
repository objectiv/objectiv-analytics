import { AbstractGlobalContext, AbstractLocationContext } from '@objectiv/schema';

/**
 * The configuration of the Contexts interface
 */
export type ContextsConfig = {
  locationStack?: AbstractLocationContext[];
  globalContexts?: AbstractGlobalContext[];
};

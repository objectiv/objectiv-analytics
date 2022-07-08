/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContextsConfig, makeIdentityContext, TrackerPluginInterface } from '@objectiv/tracker-core';

/**
 * The required attributes of IdentityContext.
 */
export type IdentityContextAttributes = {
  id: string;
  value: string;
};

/**
 * The configuration object of IdentityContextPlugin.
 * Valid parameters are:
 *  - an IdentityContextAttributes object
 *  - an array of IdentityContextAttributes objects
 *  - a function returning an IdentityContextAttributes object
 *  - a function returning an array of IdentityContextAttributes objects
 */
export type IdentityContextPluginConfig =
  | IdentityContextAttributes
  | IdentityContextAttributes[]
  | (() => IdentityContextAttributes | IdentityContextAttributes[]);

/**
 * The IdentityContextPlugin adds one or more IdentityContexts as GlobalContexts before events are transported.
 */
export class IdentityContextPlugin implements TrackerPluginInterface {
  readonly pluginName = `IdentityContextPlugin`;
  readonly config: IdentityContextPluginConfig;

  /**
   * The constructor is merely responsible for processing the given configuration.
   */
  constructor(config: IdentityContextPluginConfig) {
    this.config = config;

    globalThis.objectiv.devTools?.TrackerConsole.log(
      `%c｢objectiv:${this.pluginName}｣ Initialized`,
      'font-weight: bold'
    );
  }

  /**
   * Factor and add the IdentityContext to the Event's Global Contexts
   */
  enrich(contexts: Required<ContextsConfig>): void {
    const identityContextAttributes = typeof this.config === 'function' ? this.config() : this.config;

    const identityContexts = (
      Array.isArray(identityContextAttributes) ? identityContextAttributes : [identityContextAttributes]
    ).map(makeIdentityContext);

    contexts.global_contexts.push(...identityContexts);
  }

  /**
   * Make this plugin always usable
   */
  isUsable(): boolean {
    return true;
  }
}

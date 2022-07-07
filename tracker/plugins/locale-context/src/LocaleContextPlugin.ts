/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContextsConfig, makeLocaleContext, TrackerPluginInterface } from '@objectiv/tracker-core';

/**
 * The configuration object of LocaleContextPlugin. Developers must specify a function returning the locale.
 */
export type LocaleContextPluginConfig = {
  idFactoryFunction: () => string | null | undefined;
};

/**
 * The LocaleContext Plugin executes the given idFactoryFunction to retrieve the identifier to factor a
 * LocaleContext which is attached to the Event's Global Contexts.
 * It implements the `enrich` lifecycle method. This ensures the locale is determined before each Event is sent.
 */
export class LocaleContextPlugin implements TrackerPluginInterface {
  readonly pluginName = `LocaleContextPlugin`;
  readonly idFactoryFunction: () => string | null | undefined;

  /**
   * The constructor is merely responsible for processing the given LocaleContextPluginConfig.
   */
  constructor(config: LocaleContextPluginConfig) {
    this.idFactoryFunction = config.idFactoryFunction;

    globalThis.objectiv.devTools?.TrackerConsole.log(
      `%c｢objectiv:${this.pluginName}｣ Initialized`,
      'font-weight: bold'
    );
  }

  /**
   * Generate a fresh LocaleContext before each TrackerEvent is handed over to the TrackerTransport.
   */
  enrich(contexts: Required<ContextsConfig>): void {
    const localeContextId = this.idFactoryFunction();

    if (!localeContextId) {
      globalThis.objectiv.devTools?.TrackerConsole.warn(
        `｢objectiv:${this.pluginName}｣ Cannot enrich. Could not determine locale.`
      );
      return;
    }

    const localeContext = makeLocaleContext({
      id: localeContextId,
    });
    contexts.global_contexts.push(localeContext);
  }

  /**
   * Make this plugin always usable. The provided idFactoryFunction may return `null` when detection is impossible.
   */
  isUsable(): boolean {
    return true;
  }
}

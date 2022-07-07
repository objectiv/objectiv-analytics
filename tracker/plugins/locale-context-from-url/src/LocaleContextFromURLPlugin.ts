/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContextsConfig, makeLocaleContext, TrackerPluginInterface } from '@objectiv/tracker-core';

/**
 * The configuration object of LocaleContextFromURLPlugin. Developers must specify a function returning the locale.
 */
export type LocaleContextFromURLPluginConfig = {
  idFactoryFunction: () => string | null | undefined;
};

/**
 * The LocaleContextFromURL Plugin gathers the current URL using the Location API, then applies or executes the given
 * RegExp or FactoryFunction to it in order to extract the locale information.
 * The resulting match, if any, is used to factor a LocaleContext which is attached to the Event's Global Contexts.
 * It implements the `enrich` lifecycle method. This ensures the locale is determined before each Event is sent.
 */
export class LocaleContextFromURLPlugin implements TrackerPluginInterface {
  readonly pluginName = `LocaleContextFromURLPlugin`;
  readonly idFactoryFunction: () => string | null | undefined;

  /**
   * The constructor is merely responsible for processing the given LocaleContextFromURLPluginConfig.
   */
  constructor(config: LocaleContextFromURLPluginConfig) {
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
    if (!this.isUsable()) {
      globalThis.objectiv.devTools?.TrackerConsole.error(
        `｢objectiv:${this.pluginName}｣ Cannot enrich. Plugin is not usable (document: ${typeof document}).`
      );
      return;
    }

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
   * Make this plugin usable only on web, eg: Document and Location APIs are both available
   */
  isUsable(): boolean {
    return typeof document !== 'undefined' && typeof document.location !== 'undefined';
  }
}

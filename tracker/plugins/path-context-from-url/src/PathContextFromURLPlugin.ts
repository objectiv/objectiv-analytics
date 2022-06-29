/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ContextsConfig, makePathContext, TrackerPluginInterface } from '@objectiv/tracker-core';

/**
 * The PathContextFromURL Plugin gathers the current URL using the Location API.
 * It implements the `enrich` lifecycle method. This ensures the URL is retrieved before each Event is sent.
 *
 * Event Validation:
 *  - Must be present in Global Contexts
 *  - Must not be present multiple times
 */
export class PathContextFromURLPlugin implements TrackerPluginInterface {
  readonly pluginName = `PathContextFromURLPlugin`;

  /**
   * Initializes validation rules.
   */
  initialize(): void {
    globalThis.objectiv.devTools?.TrackerConsole.log(
      `%c｢objectiv:${this.pluginName}｣ Initialized`,
      'font-weight: bold'
    );
  }

  /**
   * Generate a fresh PathContext before each TrackerEvent is handed over to the TrackerTransport.
   */
  enrich(contexts: Required<ContextsConfig>): void {
    if (!this.isUsable()) {
      globalThis.objectiv.devTools?.TrackerConsole.error(
        `｢objectiv:${this.pluginName}｣ Cannot enrich. Plugin is not usable (document: ${typeof document}).`
      );
      return;
    }

    const pathContext = makePathContext({
      id: document.location.href,
    });
    contexts.global_contexts.push(pathContext);
  }

  /**
   * Make this plugin usable only on web, eg: Document and Location APIs are both available
   */
  isUsable(): boolean {
    return typeof document !== 'undefined' && typeof document.location !== 'undefined';
  }
}

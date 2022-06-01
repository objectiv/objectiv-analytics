/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  ContextsConfig,
  GlobalContextName,
  makePathContext,
  TrackerEvent,
  TrackerInterface,
  TrackerPluginInterface,
  TrackerValidationRuleInterface,
} from '@objectiv/tracker-core';

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
  validationRules: TrackerValidationRuleInterface[] = [];
  initialized: boolean = false;

  /**
   * Initializes validation rules.
   */
  initialize({ platform }: TrackerInterface): void {
    if (globalThis.objectiv) {
      this.validationRules = [
        globalThis.objectiv.makeGlobalContextValidationRule({
          platform,
          logPrefix: this.pluginName,
          contextName: GlobalContextName.PathContext,
          once: true,
        }),
      ];
    }

    this.initialized = true;

    globalThis.objectiv?.TrackerConsole.log(`%c｢objectiv:${this.pluginName}｣ Initialized`, 'font-weight: bold');
  }

  /**
   * Generate a fresh PathContext before each TrackerEvent is handed over to the TrackerTransport.
   */
  enrich(contexts: Required<ContextsConfig>): void {
    const pathContext = makePathContext({
      id: document.location.href,
    });
    contexts.global_contexts.push(pathContext);
  }

  /**
   * If the Plugin is usable runs all validation rules.
   */
  validate(event: TrackerEvent): void {
    if (this.isUsable()) {
      if (!this.initialized) {
        globalThis.objectiv?.TrackerConsole.error(
          `｢objectiv:${this.pluginName}｣ Cannot validate. Make sure to initialize the plugin first.`
        );
        return;
      }
      this.validationRules.forEach((validationRule) => validationRule.validate(event));
    }
  }

  /**
   * Make this plugin usable only on web, eg: Document and Location APIs are both available
   */
  isUsable(): boolean {
    return typeof document !== 'undefined' && typeof document.location !== 'undefined';
  }
}

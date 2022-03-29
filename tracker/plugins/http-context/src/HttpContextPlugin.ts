/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  GlobalContextValidationRule,
  makeHttpContext,
  TrackerConsole,
  TrackerEvent,
  TrackerInterface,
  TrackerPluginInterface,
  TrackerValidationRuleInterface,
} from '@objectiv/tracker-core';

/**
 * The HttpContext Plugin gathers the current URL using the Location API.
 * It implements the `initialize` lifecycle method. This ensures the Context is generated when the tracker is created.
 */
export class HttpContextPlugin implements TrackerPluginInterface {
  readonly pluginName = `HttpContextPlugin`;
  readonly validationRules: TrackerValidationRuleInterface[];

  /**
   * The constructor is responsible for initializing validation rules.
   */
  constructor() {
    this.validationRules = [
      new GlobalContextValidationRule({
        logPrefix: this.pluginName,
        contextName: 'HttpContext',
        once: true,
      }),
    ];

    TrackerConsole.log(`%c｢objectiv:${this.pluginName}｣ Initialized`, 'font-weight: bold');
  }

  /**
   * Generate an HttpContext.
   */
  initialize(tracker: TrackerInterface): void {
    const httpContext = makeHttpContext({
      id: 'http_context',
      referrer: document.referrer ?? '',
      user_agent: navigator.userAgent ?? ''
    });
    tracker.global_contexts.push(httpContext);
  }

  /**
   * If the Plugin is usable runs all validation rules.
   */
  validate(event: TrackerEvent): void {
    if (this.isUsable()) {
      this.validationRules.forEach((validationRule) => validationRule.validate(event));
    }
  }

  /**
   * Make this plugin usable only on web, eg: Document and Navigation APIs are both available
   */
  isUsable(): boolean {
    return typeof document !== 'undefined' && typeof navigator !== 'undefined';
  }
}

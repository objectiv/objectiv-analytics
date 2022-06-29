/*
 * Copyright 2022 Objectiv B.V.
 */

import { ApplicationContext } from '@objectiv/schema';
import {
  ContextsConfig,
  makeApplicationContext,
  TrackerInterface,
  TrackerPluginInterface,
} from '@objectiv/tracker-core';

/**
 * The ApplicationContextPlugin adds an ApplicationContext as GlobalContext before events are transported.
 * ApplicationContext Validation is performed by OpenTaxonomyValidationPlugin
 */
export class ApplicationContextPlugin implements TrackerPluginInterface {
  readonly pluginName = `ApplicationContextPlugin`;
  initialized: boolean = false;
  applicationContext?: ApplicationContext;

  /**
   * Generates a ApplicationContext with the Tracker's applicationId.
   */
  initialize(tracker: TrackerInterface) {
    this.applicationContext = makeApplicationContext({
      id: tracker.applicationId,
    });

    this.initialized = true;

    if (globalThis.objectiv.devTools) {
      globalThis.objectiv.devTools.TrackerConsole.groupCollapsed(`｢objectiv:${this.pluginName}｣ Initialized`);
      globalThis.objectiv.devTools.TrackerConsole.log(`Application ID: ${tracker.applicationId}`);
      globalThis.objectiv.devTools.TrackerConsole.group(`Application Context:`);
      globalThis.objectiv.devTools.TrackerConsole.log(this.applicationContext);
      globalThis.objectiv.devTools.TrackerConsole.groupEnd();
      globalThis.objectiv.devTools.TrackerConsole.groupEnd();
    }
  }

  /**
   * Add the ApplicationContext to the Event's Global Contexts
   */
  enrich(contexts: Required<ContextsConfig>): void {
    if (!this.initialized) {
      globalThis.objectiv.devTools?.TrackerConsole.error(
        `｢objectiv:${this.pluginName}｣ Cannot enrich. Make sure to initialize the plugin first.`
      );
    }
    if (this.applicationContext) {
      contexts.global_contexts.push(this.applicationContext);
    }
  }

  /**
   * Make this plugin always usable
   */
  isUsable(): boolean {
    return true;
  }
}

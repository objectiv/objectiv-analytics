/*
 * Copyright 2022 Objectiv B.V.
 */

import { ApplicationContext } from '@objectiv/schema';
import { ContextsConfig } from '../Context';
import { makeApplicationContext } from '../ContextFactories';
import { TrackerInterface } from '../Tracker';
import { TrackerPluginInterface } from '../TrackerPluginInterface';

/**
 * The ApplicationContextPlugin adds an ApplicationContext as GlobalContext before events are transported.
 * ApplicationContext Validation is performed by OpenTaxonomyValidationPlugin
 */
export class ApplicationContextPlugin implements TrackerPluginInterface {
  readonly pluginName = `ApplicationContextPlugin`;
  applicationContext?: ApplicationContext;

  /**
   * Generates a ApplicationContext with the Tracker's applicationId.
   */
  initialize(tracker: TrackerInterface) {
    this.applicationContext = makeApplicationContext({
      id: tracker.applicationId,
    });

    if (globalThis.objectiv) {
      globalThis.objectiv.TrackerConsole.groupCollapsed(`｢objectiv:${this.pluginName}｣ Initialized`);
      globalThis.objectiv.TrackerConsole.log(`Application ID: ${tracker.applicationId}`);
      globalThis.objectiv.TrackerConsole.group(`Application Context:`);
      globalThis.objectiv.TrackerConsole.log(this.applicationContext);
      globalThis.objectiv.TrackerConsole.groupEnd();
      globalThis.objectiv.TrackerConsole.groupEnd();
    }
  }

  /**
   * Add the ApplicationContext to the Event's Global Contexts
   */
  enrich(contexts: Required<ContextsConfig>): void {
    if (!this.applicationContext) {
      globalThis.objectiv?.TrackerConsole.error(
        `｢objectiv:${this.pluginName}｣ Cannot enrich. Make sure to initialize the plugin first.`
      );
      return;
    }
    contexts.global_contexts.push(this.applicationContext);
  }

  /**
   * Make this plugin always usable
   */
  isUsable(): boolean {
    return true;
  }
}

import { ContextsConfig, makeRootLocationContext, TrackerPluginInterface } from '@objectiv/tracker-core';
import { makeRootLocationId } from './makeRootLocationId';

/**
 * The configuration object of RootLocationContextFromURLPlugin.
 */
export type RootLocationContextFromURLPluginConfig = {
  idFactoryFunction?: typeof makeRootLocationId;
};

/**
 * The RootLocationContextFromURL Plugin factors a RootLocationContext out of the first slug of the current URL.
 * RootLocationContext is validated by OpenTaxonomyValidationPlugin in Core Tracker.
 */
export class RootLocationContextFromURLPlugin implements TrackerPluginInterface {
  readonly pluginName = `RootLocationContextFromURLPlugin`;
  readonly idFactoryFunction: typeof makeRootLocationId;

  /**
   * The constructor is merely responsible for processing the given TrackerPluginConfiguration.
   */
  constructor(config?: RootLocationContextFromURLPluginConfig) {
    this.idFactoryFunction = config?.idFactoryFunction ?? makeRootLocationId;

    globalThis.objectiv.devTools?.TrackerConsole.log(
      `%c｢objectiv:${this.pluginName}｣ Initialized`,
      'font-weight: bold'
    );
  }

  /**
   * Generate a fresh RootLocationContext before each TrackerEvent is handed over to the TrackerTransport.
   */
  enrich(contexts: Required<ContextsConfig>): void {
    if (!this.isUsable()) {
      globalThis.objectiv.devTools?.TrackerConsole.error(
        `｢objectiv:${this.pluginName}｣ Cannot enrich. Plugin is not usable (document: ${typeof document}).`
      );
      return;
    }

    const rootLocationContextId = this.idFactoryFunction();

    if (rootLocationContextId) {
      contexts.location_stack.unshift(makeRootLocationContext({ id: rootLocationContextId }));
    } else {
      globalThis.objectiv.devTools?.TrackerConsole.error(
        `%c｢objectiv:${this.pluginName}｣ Could not generate a RootLocationContext from "${location.pathname}"`,
        'font-weight: bold'
      );
    }
  }

  /**
   * Make this plugin usable only on web, eg: Document and Location APIs are both available
   */
  isUsable(): boolean {
    return typeof document !== 'undefined' && typeof document.location !== 'undefined';
  }
}

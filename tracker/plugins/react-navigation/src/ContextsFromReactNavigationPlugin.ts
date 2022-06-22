/*
 * Copyright 2022 Objectiv B.V.
 */

import { makeRootLocationContext, TrackerPluginInterface } from '@objectiv/tracker-core';
import { ContextsConfig, makePathContext } from '@objectiv/tracker-core';
import { getPathFromState, NavigationContainerRefWithCurrent } from '@react-navigation/native';

/**
 * The configuration of ContextsFromReactNavigationPlugin always requires a React NavigationContainerRef.
 */
export type ContextsFromReactNavigationPluginConfig<ParamList extends ReactNavigation.RootParamList> = {
  navigationContainerRef: NavigationContainerRefWithCurrent<ParamList>;
};

/**
 * A plugin that can infer RootLocation and Path Contexts by querying React Navigation NavigationContainerRef state.
 */
export class ContextsFromReactNavigationPlugin<ParamList extends ReactNavigation.RootParamList>
  implements TrackerPluginInterface
{
  readonly pluginName = `ContextsFromReactNavigationPlugin`;
  readonly navigationContainerRef: NavigationContainerRefWithCurrent<ParamList>;

  /**
   * The constructor is responsible for processing the given configuration.
   */
  constructor(config: ContextsFromReactNavigationPluginConfig<ParamList>) {
    this.navigationContainerRef = config.navigationContainerRef;

    globalThis.objectiv.devTools?.TrackerConsole.log(
      `%c｢objectiv:${this.pluginName}｣ Initialized`,
      'font-weight: bold'
    );
  }

  /**
   * Generate RootLocationContext and PathContext from React Navigation Container ref state.
   */
  enrich(contexts: Required<ContextsConfig>) {
    let rootLocationContextId;
    let pathContextId;

    if (this.navigationContainerRef.isReady()) {
      const currentRoute = this.navigationContainerRef.getCurrentRoute();
      if (currentRoute && currentRoute.name) {
        rootLocationContextId = currentRoute.name;
      }
      pathContextId = getPathFromState(this.navigationContainerRef.getRootState());
    }

    contexts.location_stack.unshift(makeRootLocationContext({ id: rootLocationContextId ?? 'home' }));
    contexts.global_contexts.push(makePathContext({ id: pathContextId ?? '/' }));
  }

  /**
   * This plugin is always usable. If React Navigation is not ready it will still produce valid Contexts.
   */
  isUsable(): boolean {
    return true;
  }
}

import { ContextsConfig, TrackerPlugins } from '@objectiv/tracker-core';
import { defaultWebTrackerPluginsList, WebTracker, WebTrackerConfig } from '@objectiv/tracker-web';

/**
 * React Tracker configuration is identical to the Web Tracker configuration.
 */
export type ReactTrackerConfig = WebTrackerConfig;

/**
 * React Tracker extends the Web Tracker functionality with React specific Hooks and ContextProviders to simplify the
 * tracking of Sections, Component visibility and Component state.
 */
export class ReactTracker extends WebTracker {
  constructor(reactConfig: ReactTrackerConfig, ...contextConfigs: ContextsConfig[]) {
    let config = reactConfig;

    // Extend generic Web Plugins from Web Tracker with React specific ones
    if (!config.plugins) {
      config = {
        ...config,
        plugins: new TrackerPlugins([
          ...defaultWebTrackerPluginsList,
          // TODO add React plugins
        ]),
      };
    }

    // code-coverage mistakenly detects super class calls as uncovered code-forks. Related to TS transpiling.
    /* istanbul ignore next */
    super(config, ...contextConfigs);
  }
}

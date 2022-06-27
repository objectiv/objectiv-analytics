/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ContextsConfig } from './Context';
import { isValidIndex } from './helpers';
import { Tracker, TrackerInterface } from './Tracker';
import { TrackerEvent } from './TrackerEvent';
import { TrackerPluginInterface } from './TrackerPluginInterface';
import { TrackerPluginLifecycleInterface } from './TrackerPluginLifecycleInterface';
import { TrackerValidationLifecycleInterface } from './TrackerValidationLifecycleInterface';

/**
 * The configuration object of TrackerPlugins. It requires a Tracker instance and a list of plugins.
 */
export type TrackerPluginsConfiguration = {
  /**
   * The Tracker instance this TrackerPlugins is bound to.
   */
  tracker: Tracker;

  /**
   * An array of Plugins.
   */
  plugins: TrackerPluginInterface[];
};

/**
 * TrackerPlugins is responsible for constructing TrackerPlugin instances and orchestrating their callbacks.
 * It also makes sure to check if Plugins are usable, before executing their callbacks.
 *
 * @note plugin order matters, as they are executed sequentially, a plugin executed later has access to previous
 * Plugins mutations. For example a plugin meant to access the finalized version of the TrackerEvent should be placed
 * at the bottom of the list.
 */
export class TrackerPlugins implements TrackerPluginLifecycleInterface, TrackerValidationLifecycleInterface {
  readonly tracker: Tracker;
  plugins: TrackerPluginInterface[] = [];

  /**
   * Processes the given plugins and pushes them in the internal list, while validating their uniqueness.
   */
  constructor(trackerPluginsConfig: TrackerPluginsConfiguration) {
    this.tracker = trackerPluginsConfig.tracker;

    trackerPluginsConfig.plugins.map((plugin) => {
      if (this.has(plugin.pluginName)) {
        this.plugins = this.plugins.filter(({ pluginName }) => pluginName !== plugin.pluginName);
      }

      this.plugins.push(plugin);
    });

    if (globalThis.objectiv.devTools) {
      globalThis.objectiv.devTools.TrackerConsole.groupCollapsed(`｢objectiv:TrackerPlugins｣ Initialized`);
      globalThis.objectiv.devTools.TrackerConsole.group(`Plugins:`);
      globalThis.objectiv.devTools.TrackerConsole.log(this.plugins.map((plugin) => plugin.pluginName).join(', '));
      globalThis.objectiv.devTools.TrackerConsole.groupEnd();
      globalThis.objectiv.devTools.TrackerConsole.groupEnd();
    }
  }

  /**
   * Checks whether a Plugin instance exists by its name.
   */
  has(pluginName: string): boolean {
    return this.plugins.find((plugin) => plugin.pluginName === pluginName) !== undefined;
  }

  /**
   * Gets a Plugin instance by its name. Returns null if the plugin is not found.
   */
  get(pluginName: string): TrackerPluginInterface {
    const plugin = this.plugins.find((plugin) => plugin.pluginName === pluginName);

    if (!plugin) {
      throw new Error(`｢objectiv:TrackerPlugins｣ ${pluginName}: not found`);
    }

    return plugin;
  }

  /**
   * Adds a new Plugin at the end of the plugins list, or at the specified index, and initializes it.
   */
  add(plugin: TrackerPluginInterface, index?: number) {
    if (index !== undefined && !isValidIndex(index)) {
      throw new Error(`｢objectiv:TrackerPlugins｣ invalid index`);
    }

    if (this.has(plugin.pluginName)) {
      throw new Error(`｢objectiv:TrackerPlugins｣ ${plugin.pluginName}: already exists. Use "replace" instead`);
    }

    const spliceIndex = index ?? this.plugins.length;
    this.plugins.splice(spliceIndex, 0, plugin);

    globalThis.objectiv.devTools?.TrackerConsole.log(
      `%c｢objectiv:TrackerPlugins｣ ${plugin.pluginName} added at index ${spliceIndex}`,
      'font-weight: bold'
    );

    const pluginInstance = this.get(plugin.pluginName);
    pluginInstance.initialize && pluginInstance.initialize(this.tracker);
  }

  /**
   * Removes a Plugin by its name.
   */
  remove(pluginName: string) {
    const pluginInstance = this.get(pluginName);

    this.plugins = this.plugins.filter(({ pluginName }) => pluginName !== pluginInstance.pluginName);

    globalThis.objectiv.devTools?.TrackerConsole.log(
      `%c｢objectiv:TrackerPlugins｣ ${pluginInstance.pluginName} removed`,
      'font-weight: bold'
    );
  }

  /**
   * Replaces a plugin with a new one of the same type at the same index, unless a new index has been specified.
   */
  replace(plugin: TrackerPluginInterface, index?: number) {
    if (index !== undefined && !isValidIndex(index)) {
      throw new Error(`｢objectiv:TrackerPlugins｣ invalid index`);
    }

    const originalIndex = this.plugins.findIndex(({ pluginName }) => pluginName === plugin.pluginName);

    this.remove(plugin.pluginName);

    this.add(plugin, index ?? originalIndex);
  }

  /**
   * Calls each Plugin's `initialize` callback function, if defined.
   */
  initialize(tracker: TrackerInterface): void {
    this.plugins.forEach((plugin) => plugin.isUsable() && plugin.initialize && plugin.initialize(tracker));
  }

  /**
   * Calls each Plugin's `enrich` callback function, if defined.
   */
  enrich(contexts: Required<ContextsConfig>): void {
    this.plugins.forEach((plugin) => plugin.isUsable() && plugin.enrich && plugin.enrich(contexts));
  }

  /**
   * Calls each Plugin's `validate` callback function, if defined.
   */
  validate(event: TrackerEvent): void {
    this.plugins.forEach((plugin) => plugin.isUsable() && plugin.validate && plugin.validate(event));
  }
}

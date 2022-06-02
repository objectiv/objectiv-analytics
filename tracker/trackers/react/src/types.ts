/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { AllHTMLAttributes, ComponentType, ReactHTML } from 'react';

/**
 * Generic enriching the given type with a `Component` property that can be either a React Component or a JSX element.
 */
export type WithComponentProp<T> = T & { Component: ComponentType<T> | keyof ReactHTML };

/**
 * The props of all HTMLElement TrackedContexts.
 */
export type TrackedContextProps<T = HTMLElement> = WithComponentProp<AllHTMLAttributes<T>> & {
  /**
   * The unique id of the LocationContext
   */
  id: string;

  /**
   * Whether to forward the given id to the given Component
   */
  forwardId?: boolean;

  /**
   * Whether to normalize the given id, default to true
   */
  normalizeId?: boolean;
};

/**
 * The props of Contexts supporting Visibility events. Extends TrackedContextProps with then `isVisible` property.
 */
export type TrackedShowableContextProps = TrackedContextProps & {
  /**
   * Whether to track visibility events automatically when this prop changes state.
   */
  isVisible?: boolean;
};

/**
 * The props of TrackedPressableContext. Extends TrackedContextProps with then `isVisible` property.
 */
export type TrackedPressableContextProps = Omit<TrackedContextProps, 'id'> & {
  /**
   * The unique id of the LocationContext. Optional because we will attempt to auto-detect it.
   */
  id?: string;

  /**
   * The title is used to generate a unique identifier. Optional because we will attempt to auto-detect it.
   */
  title?: string;

  /**
   * Whether to forward the given title to the given Component.
   */
  forwardTitle?: boolean;
};

/**
 * Overrides TrackedContextProps to not require an id, assuming that semantically there should be only one Element
 */
export type SingletonTrackedElementProps = Omit<TrackedContextProps, 'Component' | 'id'> & {
  /**
   * Optional identifier to be provided only in case of uniqueness collisions, defaults to 'footer'
   */
  id?: string;
};

/**
 * Some extra options that may be useful for special cases, e.g. anchors without texts or external hrefs.
 * This is mainly used for TrackedContexts and Custom Components.
 *
 * TODO switch to this way of setting options, as opposed to the current prop merging
 */
export type ObjectivTrackingOptions = {
  /**
   * Whether to block and wait for the Tracker having sent the event, e.g. an external or a full page refresh link.
   */
  waitUntilTracked?: boolean;

  /**
   * The unique id of the LinkContext. Required for links without any title nor text.
   */
  contextId?: string;

  /**
   * Whether to normalize the given id, default to true.
   */
  normalizeId?: boolean;
};

/**
 * The prop containing Objectiv Tracking Options.
 */
export type TrackingOptionsProp = {
  /**
   * All Objectiv tracking related options reside under this prop.
   */
  objectiv?: ObjectivTrackingOptions;
};

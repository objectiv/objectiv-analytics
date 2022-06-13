/*
 * Copyright 2022 Objectiv B.V.
 */

import { GlobalContextName, LocationContextName } from './ContextNames';
import { TrackerPlatform } from './Tracker';
import { TrackerValidationRuleConfig, TrackerValidationRuleInterface } from './TrackerValidationRuleInterface';

/**
 * Defines options shared between rules that perform Context validation.
 */
export type ContextValidationRuleParameters<ContextType extends GlobalContextName | LocationContextName> =
  TrackerValidationRuleConfig & {
    /**
     * TrackerPlatform retrieved from the TrackerInstance. Used to retrieve platform-specific error messages.
     */
    platform: TrackerPlatform;

    /**
     * The name of the Context to validate, e.g. `RootLocationContext`, `ApplicationContext, etc.
     */
    contextName: ContextType;

    /**
     * Optional. Restricts whether the specified Context may be present multiple times.
     */
    once?: boolean;
  };

/**
 * GlobalContextValidationRule config object.
 */
export type GlobalContextValidationRuleParameters = ContextValidationRuleParameters<GlobalContextName>;

/**
 * GlobalContextValidationRule factory.
 */
export type GlobalContextValidationRuleFactory = (
  parameters: GlobalContextValidationRuleParameters
) => GlobalContextValidationRuleParameters & TrackerValidationRuleInterface;

/**
 * LocationStack order matters, the LocationContextValidationRule config supports specifying a required position.
 */
export type LocationContextValidationRuleParameters = ContextValidationRuleParameters<LocationContextName> & {
  /**
   * Optional. Restricts in which position the specified LocationContext may be.
   */
  position?: number;
};

/**
 * GlobalContextValidationRule factory.
 */
export type LocationContextValidationRuleFactory = (
  parameters: LocationContextValidationRuleParameters
) => LocationContextValidationRuleParameters & TrackerValidationRuleInterface;

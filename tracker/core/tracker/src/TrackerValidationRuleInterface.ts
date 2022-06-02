/*
 * Copyright 2022 Objectiv B.V.
 */

import { EventToValidate } from './TrackerEvent';
import { TrackerValidationLifecycleInterface } from './TrackerValidationLifecycleInterface';

/**
 * The TrackerValidationRuleConfig.
 */
export type TrackerValidationRuleConfig = {
  /**
   * Optional. Allows adding further information to the logging prefix, e.g. ｢objectiv:<logPrefix><ruleName>｣<message>
   */
  logPrefix?: string;

  /**
   * Optional. A predicated for discriminating which events are affected by this rule.
   */
  eventMatches?: (event: EventToValidate) => boolean;
};

/**
 * A ValidationRule must define its own `validationRuleName` and must define a `validate` callback.
 */
export interface TrackerValidationRuleInterface extends Required<TrackerValidationLifecycleInterface> {
  readonly validationRuleName: string;
  readonly logPrefix?: string;
}

/**
 * The TrackerValidationRule constructor interface.
 */
export interface TrackerValidationRuleConstructor {
  new (TrackerValidationRuleConfig: TrackerValidationRuleConfig): TrackerValidationRuleInterface;
}

/*
 * Copyright 2022 Objectiv B.V.
 */

import { LocationContextValidationRuleFactory, TrackerEvent } from '@objectiv/tracker-core';
import { LocationContextErrorMessages } from '../ContextErrorMessages';
import { TrackerConsole } from '../TrackerConsole';
import { LocationContextErrorType } from '../types';

/**
 * A generic configurable Rule that can verify, and console error, whether the given `context` is:
 * - present in Location Stack
 * - optionally, present only once
 * - optionally, present in a specific position
 */
export const makeLocationContextValidationRule: LocationContextValidationRuleFactory = (parameters) => {
  const validationRuleName = `LocationContextValidationRule`;

  TrackerConsole.groupCollapsed(
    `｢objectiv:${parameters.logPrefix?.concat(':')}${validationRuleName}｣ Initialized. Context: ${
      parameters.contextName
    }.`
  );
  TrackerConsole.group(`Parameters:`);
  TrackerConsole.log(parameters);
  TrackerConsole.groupEnd();
  TrackerConsole.groupEnd();

  return {
    validationRuleName,
    ...parameters,

    /**
     * Verifies whether the given Context is present, duplicated or in the wrong position in the given TrackerEvent.
     */
    validate(event: TrackerEvent): void {
      const index = event.location_stack.findIndex((context) => context._type === this.contextName);
      const matches = event.location_stack.filter((context) => context._type === this.contextName);

      let errorType: LocationContextErrorType | null = null;
      if (!matches.length) {
        errorType = LocationContextErrorType.LOCATION_CONTEXT_MISSING;
      } else if (this.once && matches.length > 1) {
        errorType = LocationContextErrorType.LOCATION_CONTEXT_DUPLICATED;
      } else if (typeof this.position === 'number' && index !== this.position) {
        errorType = LocationContextErrorType.LOCATION_CONTEXT_WRONG_POSITION;
      }

      if (errorType) {
        const errorMessagePrefix = `｢objectiv${this.logPrefix ? ':' + this.logPrefix : ''}｣`;
        const errorMessageTemplate = LocationContextErrorMessages[this.platform][errorType][this.contextName];
        const errorMessageBody = errorMessageTemplate.replace(/{{eventName}}/g, event._type);

        TrackerConsole.groupCollapsed(`%c${errorMessagePrefix} Error: ${errorMessageBody}`, 'color:red');
        TrackerConsole.group(`Event:`);
        TrackerConsole.log(event);
        TrackerConsole.groupEnd();
        TrackerConsole.groupEnd();
      }
    },
  };
};

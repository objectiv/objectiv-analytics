/*
 * Copyright 2022 Objectiv B.V.
 */

import { GlobalContextValidationRuleFactory, TrackerEvent } from '@objectiv/tracker-core';
import { GlobalContextErrorMessages } from '../ContextErrorMessages';
import { TrackerConsole } from '../TrackerConsole';
import { GlobalContextErrorType } from '../types';

/**
 * A generic configurable Rule that can verify, and console error, whether the given `context` is:
 * - present in Global Contexts
 * - optionally, present only once
 */
export const makeGlobalContextValidationRule: GlobalContextValidationRuleFactory = (parameters) => {
  const validationRuleName = `GlobalContextValidationRule`;

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
     * Verifies whether the given Context is present or duplicated in the given TrackerEvent.
     */
    validate(event: TrackerEvent): void {
      const matches = event.global_contexts.filter((context) => context._type === this.contextName);

      let errorType: GlobalContextErrorType | null = null;
      if (!matches.length) {
        errorType = GlobalContextErrorType.GLOBAL_CONTEXT_MISSING;
      } else if (this.once && matches.length > 1) {
        errorType = GlobalContextErrorType.GLOBAL_CONTEXT_DUPLICATED;
      }

      if (errorType) {
        const errorMessagePrefix = `｢objectiv${this.logPrefix ? ':' + this.logPrefix : ''}｣`;
        const errorMessageTemplate = GlobalContextErrorMessages[this.platform][errorType][this.contextName];
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

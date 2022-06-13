/*
 * Copyright 2022 Objectiv B.V.
 */

import { DefaultErrorMessagesByType } from './ErrorMessagesTemplates';
import { ContextErrorMessage, ContextName, ErrorType } from '../types';

/**
 * The parameters of preCompileErrorMessage
 */
export type PreCompileErrorMessageParameters<ErrorTypes extends ErrorType, ContextNames extends ContextName> = {
  errorMessagesTemplates: Partial<{
    [type in ErrorTypes]: Partial<ContextErrorMessage<ContextNames>>;
  }>;
  type: ErrorTypes;
  contextName: ContextNames;
  docsURL: string;
};

/**
 * Helper function to pre-compile error message templates `docsURL` and `contextName` placeholders.
 */
export function preCompileErrorMessage<ErrorTypes extends ErrorType, ContextNames extends ContextName>({
  errorMessagesTemplates,
  type,
  contextName,
  docsURL,
}: PreCompileErrorMessageParameters<ErrorTypes, ContextNames>) {
  let errorMessage = DefaultErrorMessagesByType[type];

  // Retrieve message template override, if set, by type and context name
  if (errorMessagesTemplates && errorMessagesTemplates[type]) {
    const errorMessagesTemplatesByType = errorMessagesTemplates[type] as ContextErrorMessage<ContextNames>;
    if (errorMessagesTemplatesByType[contextName]) {
      errorMessage = errorMessagesTemplatesByType[contextName];
    }
  }

  // Replace docsURL and contextName with actual values in message template
  errorMessage = errorMessage.replace(/{{docsURL}}/g, docsURL);
  errorMessage = errorMessage.replace(/{{contextName}}/g, contextName);

  return errorMessage;
}

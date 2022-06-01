/*
 * Copyright 2022 Objectiv B.V.
 */

import { GlobalContextName, LocationContextName, TrackerPlatform } from '@objectiv/tracker-core';

/**
 * GlobalContext error types
 */
export enum GlobalContextErrorType {
  GLOBAL_CONTEXT_MISSING = 'GLOBAL_CONTEXT_MISSING',
  GLOBAL_CONTEXT_DUPLICATED = 'GLOBAL_CONTEXT_DUPLICATED',
}

/**
 * LocationContext error types
 */
export enum LocationContextErrorType {
  LOCATION_CONTEXT_MISSING = 'LOCATION_CONTEXT_MISSING',
  LOCATION_CONTEXT_DUPLICATED = 'LOCATION_CONTEXT_DUPLICATED',
  LOCATION_CONTEXT_WRONG_POSITION = 'LOCATION_CONTEXT_WRONG_POSITION',
}

/**
 * Error messages are key:value structures where the keu is the contextName and the value is the message itself.
 */
export type ContextName = GlobalContextName | LocationContextName;
export type ContextErrorMessage<ContextNames extends ContextName> = { [contextName in ContextNames]: string };

/**
 * Messages are organized by type.
 */
export type ErrorType = GlobalContextErrorType | LocationContextErrorType;
export type ContextErrorMessageByType<ErrorTypes extends ErrorType, ContextNames extends ContextName> = {
  [type in ErrorTypes]: ContextErrorMessage<ContextNames>;
};

/**
 * Messages are organized further by platform.
 */
export type ContextErrorMessages<ErrorTypes extends ErrorType, ContextNames extends ContextName> = {
  [platform in TrackerPlatform]: ContextErrorMessageByType<ErrorTypes, ContextNames>;
};

/**
 * Messages Templates can override the default error messages, or extend them, with extra info per type and Context.
 */
export type ContextErrorMessagesTemplates<ErrorTypes extends ErrorType, ContextNames extends ContextName> = {
  [platform in TrackerPlatform]: Partial<{
    [type in ErrorTypes]: Partial<ContextErrorMessage<ContextNames>>;
  }>;
};

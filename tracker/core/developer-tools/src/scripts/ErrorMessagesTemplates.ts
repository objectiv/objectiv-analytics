/*
 * Copyright 2022 Objectiv B.V.
 */

import { GlobalContextName, LocationContextName, TrackerPlatform } from '@objectiv/tracker-core';
import { ContextErrorMessagesTemplates, GlobalContextErrorType, LocationContextErrorType } from '../types';

/**
 * These are platform-independent error messages that can be shown for any type of error and context.
 */
export const DefaultErrorMessagesByType: { [type in GlobalContextErrorType | LocationContextErrorType]: string } = {
  [GlobalContextErrorType.GLOBAL_CONTEXT_MISSING]:
    '{{contextName}} is missing from Global Contexts of {{eventName}}.\n' +
    'Taxonomy documentation: {{docsURL}}/taxonomy/reference/global-contexts/{{contextName}}.',
  [GlobalContextErrorType.GLOBAL_CONTEXT_DUPLICATED]:
    'Only one {{contextName}} should be present in Global Contexts of {{eventName}}.\n' +
    'Taxonomy documentation: {{docsURL}}/taxonomy/reference/global-contexts/{{contextName}}.',
  [LocationContextErrorType.LOCATION_CONTEXT_MISSING]:
    '{{contextName}} is missing from Location Stack of {{eventName}}.\n' +
    'Taxonomy documentation: {{docsURL}}/taxonomy/reference/location-contexts/{{contextName}}.',
  [LocationContextErrorType.LOCATION_CONTEXT_DUPLICATED]:
    'Only one {{contextName}} should be present in Location Stack of {{eventName}}.\n' +
    'Taxonomy documentation: {{docsURL}}/taxonomy/reference/location-contexts/{{contextName}}.',
  [LocationContextErrorType.LOCATION_CONTEXT_WRONG_POSITION]:
    '{{contextName}} is in the wrong position of the Location Stack of {{eventName}}.\n' +
    'Taxonomy documentation: {{docsURL}}/taxonomy/reference/location-contexts/{{contextName}}.',
};

/**
 * A global map of all GlobalContext Validation Error Message Templates per platform.
 */
export const GlobalContextErrorMessagesTemplates: ContextErrorMessagesTemplates<
  GlobalContextErrorType,
  GlobalContextName
> = {
  [TrackerPlatform.ANGULAR]: {},
  [TrackerPlatform.CORE]: {},
  [TrackerPlatform.BROWSER]: {},
  [TrackerPlatform.REACT]: {},
  [TrackerPlatform.REACT_NATIVE]: {},
};

/**
 * A global map of all LocationContext Validation Error Message Templates per platform.
 */
export const LocationContextErrorMessagesTemplates: ContextErrorMessagesTemplates<
  LocationContextErrorType,
  LocationContextName
> = {
  [TrackerPlatform.ANGULAR]: {
    [LocationContextErrorType.LOCATION_CONTEXT_MISSING]: {
      RootLocationContext:
        DefaultErrorMessagesByType.LOCATION_CONTEXT_MISSING +
        '\n' +
        'See also:\n' +
        '- Configuring Roots: {{docsURL}}/tracking/angular/how-to-guides/configuring-root-locations.\n' +
        '- tagRootLocation: {{docsURL}}/tracking/angular/api-reference/locationTaggers/tagRootLocation.',
    },
  },
  [TrackerPlatform.CORE]: {},
  [TrackerPlatform.BROWSER]: {
    [LocationContextErrorType.LOCATION_CONTEXT_MISSING]: {
      RootLocationContext:
        DefaultErrorMessagesByType.LOCATION_CONTEXT_MISSING +
        '\n' +
        'See also:\n' +
        '- Configuring Roots: {{docsURL}}/tracking/browser/how-to-guides/configuring-root-locations.\n' +
        '- tagRootLocation: {{docsURL}}/tracking/browser/api-reference/locationTaggers/tagRootLocation.',
    },
  },
  [TrackerPlatform.REACT]: {
    [LocationContextErrorType.LOCATION_CONTEXT_MISSING]: {
      RootLocationContext:
        DefaultErrorMessagesByType.LOCATION_CONTEXT_MISSING +
        '\n' +
        'See also:\n' +
        '- Configuring Roots: {{docsURL}}/tracking/react/how-to-guides/configuring-root-locations.\n' +
        '- TrackedRootLocationContext: {{docsURL}}/tracking/react/api-reference/trackedContexts/TrackedRootLocationContext.\n' +
        '- RootLocationContextWrapper: {{docsURL}}/tracking/react/api-reference/locationWrappers/RootLocationContextWrapper.',
    },
  },
  [TrackerPlatform.REACT_NATIVE]: {
    [LocationContextErrorType.LOCATION_CONTEXT_MISSING]: {
      RootLocationContext:
        DefaultErrorMessagesByType.LOCATION_CONTEXT_MISSING +
        '\n' +
        'See also:\n' +
        '- React Navigation Plugin: {{docsURL}}/tracking/react-native/plugins/react-navigation.\n' +
        '- RootLocationContextWrapper: {{docsURL}}/tracking/react-native/api-reference/locationWrappers/RootLocationContextWrapper.',
    },
  },
};

/*
 * Copyright 2022 Objectiv B.V.
 */

import { GlobalContextName, LocationContextName, TrackerPlatform } from '@objectiv/tracker-core';
import * as fs from 'fs';
import { GlobalContextErrorType, LocationContextErrorType } from '../types';
import { GlobalContextErrorMessagesTemplates, LocationContextErrorMessagesTemplates } from './ErrorMessagesTemplates';
import { preCompileErrorMessage } from './preCompileErrorMessage';

/**
 * Script to generate error messages for all platforms, error types and contexts.
 * Produces a ContextErrorMessages.ts file in the src folder.
 */

export const DOCUMENTATION_URL = 'https://objectiv.io/docs';
export const DESTINATION_FILENAME = './src/ContextErrorMessages.ts';

type ErrorMessagesMap = {
  [platform: string]: {
    [type: string]: {
      [context: string]: string;
    };
  };
};

let globalContextErrorMessagesMap: ErrorMessagesMap = {};
let locationContextErrorMessagesMap: ErrorMessagesMap = {};

Object.values(TrackerPlatform).forEach((platform) => {
  if (!globalContextErrorMessagesMap[platform]) {
    globalContextErrorMessagesMap[platform] = {};
  }
  if (!locationContextErrorMessagesMap[platform]) {
    locationContextErrorMessagesMap[platform] = {};
  }

  Object.values(GlobalContextErrorType).forEach((globalContextErrorType) => {
    if (!globalContextErrorMessagesMap[platform][globalContextErrorType]) {
      globalContextErrorMessagesMap[platform][globalContextErrorType] = {};
    }
    Object.values(GlobalContextName).forEach((globalContextName) => {
      globalContextErrorMessagesMap[platform][globalContextErrorType][globalContextName] = preCompileErrorMessage<
        GlobalContextErrorType,
        GlobalContextName
      >({
        errorMessagesTemplates: GlobalContextErrorMessagesTemplates[platform],
        type: globalContextErrorType,
        contextName: globalContextName,
        docsURL: DOCUMENTATION_URL,
      });
    });
  });

  Object.values(LocationContextErrorType).forEach((locationContextErrorType) => {
    if (!locationContextErrorMessagesMap[platform][locationContextErrorType]) {
      locationContextErrorMessagesMap[platform][locationContextErrorType] = {};
    }
    Object.values(LocationContextName).forEach((locationContextName) => {
      locationContextErrorMessagesMap[platform][locationContextErrorType][locationContextName] = preCompileErrorMessage<
        LocationContextErrorType,
        LocationContextName
      >({
        errorMessagesTemplates: LocationContextErrorMessagesTemplates[platform],
        type: locationContextErrorType,
        contextName: locationContextName,
        docsURL: DOCUMENTATION_URL,
      });
    });
  });
});

fs.writeFileSync(
  DESTINATION_FILENAME,
  `/*
 * Copyright ${new Date().getFullYear()} Objectiv B.V.
 */

import { GlobalContextName, LocationContextName } from '@objectiv/tracker-core';
import { ContextErrorMessages, GlobalContextErrorType, LocationContextErrorType } from './types';

`
);

const globalContextErrorMessages = JSON.stringify(globalContextErrorMessagesMap, null, 2);
fs.appendFileSync(
  DESTINATION_FILENAME,
  'export const GlobalContextErrorMessages: ContextErrorMessages<GlobalContextErrorType, GlobalContextName> = ' +
    globalContextErrorMessages +
    ';\n\n'
);

const locationContextErrorMessages = JSON.stringify(locationContextErrorMessagesMap, null, 2);
fs.appendFileSync(
  DESTINATION_FILENAME,
  'export const LocationContextErrorMessages: ContextErrorMessages<LocationContextErrorType, LocationContextName> = ' +
    locationContextErrorMessages +
    ';\n\n'
);

console.log(`Context error messages map saved to ${DESTINATION_FILENAME}.`);

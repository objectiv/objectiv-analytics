/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackerDeveloperToolsInterface } from '@objectiv/tracker-core';
import { EventRecorder } from './EventRecorder';
import { getLocationPath } from './getLocationPath';
import { LocationTree } from './LocationTree';
import { OpenTaxonomyValidationPlugin } from './OpenTaxonomyValidationPlugin';
import { TrackerConsole } from './TrackerConsole';
import { makeGlobalContextValidationRule } from './validationRules/makeGlobalContextValidationRule';
import { makeLocationContextValidationRule } from './validationRules/makeLocationContextValidationRule';

/**
 * A global object containing all DeveloperTools
 */
const developerTools: TrackerDeveloperToolsInterface = {
  EventRecorder,
  getLocationPath,
  LocationTree,
  makeGlobalContextValidationRule,
  makeLocationContextValidationRule,
  OpenTaxonomyValidationPlugin,
  TrackerConsole,
};

/**
 * Set developer tools in globals. Globals are created by Core Tracker.
 */
globalThis.objectiv.devTools = developerTools;

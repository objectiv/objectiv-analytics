/*
 * Copyright 2022 Objectiv B.V.
 */

import { LocationStack } from './Context';
import { GlobalContextValidationRuleFactory, LocationContextValidationRuleFactory } from './ContextValidationRules';
import { EventRecorderInterface } from './EventRecorderInterface';
import { LocationTreeInterface } from './LocationTreeInterface';
import { TrackerConsoleInterface } from './TrackerConsoleInterface';
import { TrackerPluginInterface } from './TrackerPluginInterface';
import { TrackerRepositoryInterface } from './TrackerRepositoryInterface';

/**
 * DeveloperTools interface definition.
 */
export interface TrackerDeveloperToolsInterface {
  EventRecorder: EventRecorderInterface;
  getLocationPath: (locationStack: LocationStack) => string;
  LocationTree: LocationTreeInterface;
  makeGlobalContextValidationRule: GlobalContextValidationRuleFactory;
  makeLocationContextValidationRule: LocationContextValidationRuleFactory;
  OpenTaxonomyValidationPlugin: TrackerPluginInterface;
  TrackerConsole: TrackerConsoleInterface;
  TrackerRepository: TrackerRepositoryInterface<any>;
}

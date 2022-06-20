/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackerDeveloperToolsInterface } from './TrackerDeveloperToolsInterface';
import { TrackerRepositoryInterface } from './TrackerRepositoryInterface';

/**
 * Globals interface definition.
 */
export interface TrackerGlobalsInterface {
  TrackerRepository: TrackerRepositoryInterface<any>;
  devTools?: TrackerDeveloperToolsInterface;
}

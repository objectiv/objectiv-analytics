/*
 * Copyright 2022 Objectiv B.V.
 */

/**
 * All possible Abstract Event discriminators. These are used by Validation Rules to skip checks on certain events.
 */
export type EventAbstractDiscriminators = {
  __non_interactive_event?: true;
  __interactive_event?: true;
  __media_event?: true;
};

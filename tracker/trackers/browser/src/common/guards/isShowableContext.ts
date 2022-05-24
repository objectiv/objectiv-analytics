/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName } from '@objectiv/tracker-core';
import { AnyLocationContext, AnyShowableContext } from '../../definitions/LocationContext';

/**
 * A type guard to determine if the given LocationContext supports HiddenEvent and VisibleEvent.
 */
export const isShowableContext = (locationContext: AnyLocationContext): locationContext is AnyShowableContext => {
  const showableLocationContextNames = [
    LocationContextName.OverlayContext.toString(),
    LocationContextName.ExpandableContext.toString(),
  ];

  return showableLocationContextNames.includes(locationContext._type);
};

/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName } from '@objectiv/tracker-core';
import { AnyLocationContext, AnyPressableContext } from '../../definitions/LocationContext';

/**
 * A type guard to determine if the given LocationContext supports PressEvent.
 */
export const isPressableContext = (locationContext: AnyLocationContext): locationContext is AnyPressableContext => {
  const pressableLocationContextNames = [
    LocationContextName.PressableContext.toString(),
    LocationContextName.LinkContext.toString(),
  ];

  return pressableLocationContextNames.includes(locationContext._type);
};

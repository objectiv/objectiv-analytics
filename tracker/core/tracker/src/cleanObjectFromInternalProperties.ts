/*
 * Copyright 2021 Objectiv B.V.
 */

import { DiscriminatingPropertyPrefix } from '@objectiv/schema';
import { getObjectKeys } from './helpers';

/**
 * All internal properties have this prefix. For convenience this corresponds to discriminating properties prefix.
 */
const INTERNAL_PROPERTY_PREFIX: DiscriminatingPropertyPrefix = '__';

/**
 * Removes all properties starting with INTERNAL_PROPERTY_PREFIX from the given object and returns a new clean object.
 */
export const cleanObjectFromInternalProperties = <T extends object>(obj: T) => {
  const objClone = Object.assign({}, obj);

  getObjectKeys(objClone).forEach((propertyName) => {
    if (propertyName.toString().startsWith(INTERNAL_PROPERTY_PREFIX)) {
      delete objClone[propertyName];
    }
  });

  return objClone;
};

/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';

/**
 * This function is invoked by the Plugin to retrieve the identifier of the RootLocationContext unless a custom one
 * has been specified. The resulting identifier is normalized.
 */
export const makeRootLocationId = () => {
  const pathname = location.pathname;

  return ['/', ''].includes(pathname) ? 'home' : makeIdFromString(pathname?.split('/')[1]);
};

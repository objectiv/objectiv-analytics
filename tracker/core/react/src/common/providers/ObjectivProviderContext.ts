/*
 * Copyright 2021 Objectiv B.V.
 */

import { createContext } from 'react';

/**
 * A Context to keep track of whether another ObjectivProvider is present higher up in the Component tree.
 * We want to prevent multiple ObjectivProviders to be nested as it's meant to be a singleton on top of the app.
 */
export const ObjectivProviderContext = createContext<boolean>(false);

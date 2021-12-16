/*
 * Copyright 2021 Objectiv B.V.
 */

import { LocationProviderContext } from './LocationProviderContext';
import { TrackerProviderContext } from './TrackerProviderContext';

/**
 * A combination of TrackerProvider and LocationProvider states. This is used by Location Wrapper render-props.
 */
export type TrackingContext = TrackerProviderContext & LocationProviderContext;

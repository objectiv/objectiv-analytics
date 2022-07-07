/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React from 'react';
import { TrackedInputContext, TrackedInputContextProps } from '../trackedContexts/TrackedInputContext';

/**
 * Generates a TrackedInputContext preconfigured with a <input> Element as Component.
 */
export const TrackedInput = React.forwardRef<HTMLInputElement, Omit<TrackedInputContextProps, 'Component'>>(
  (props, ref) => <TrackedInputContext {...props} Component={'input'} ref={ref} />
);

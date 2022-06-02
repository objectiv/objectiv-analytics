/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import { makeTitleFromChildren } from '@objectiv/tracker-react-core';
import React from 'react';
import { TrackingOptionsProp } from '../../types';

/**
 * Attempts to generate an id by looking at `id`, `title`, `children` and `objectiv.contextId` props.
 */
export const makeIdFromTrackedAnchorProps = (
  props: { id?: string; title?: string; children?: React.ReactNode } & TrackingOptionsProp
) => props.id ?? props.objectiv?.contextId ?? makeIdFromString(props.title ?? makeTitleFromChildren(props.children));

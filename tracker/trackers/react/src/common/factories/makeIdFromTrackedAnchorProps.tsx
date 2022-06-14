/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeIdFromString } from '@objectiv/tracker-core';
import { makeTitleFromChildren } from '@objectiv/tracker-react-core';
import React from 'react';
import { ObjectivTrackingOptions } from '../../types';

/**
 * The parameters of makeIdFromTrackedAnchorProps
 */
export type makeIdFromTrackedAnchorPropsParameters = ObjectivTrackingOptions & {
  id?: string;
  title?: string;
  children?: React.ReactNode;
};

/**
 * Attempts to generate an id by looking at `id`, `title`, `children` and `objectiv.contextId` props.
 */
export const makeIdFromTrackedAnchorProps = ({
  id,
  title,
  children,
  contextId,
  normalizeId = true,
}: makeIdFromTrackedAnchorPropsParameters) => {
  const resultId = id ?? contextId ?? title ?? makeTitleFromChildren(children);

  if (normalizeId) {
    return makeIdFromString(resultId);
  }

  return resultId;
};

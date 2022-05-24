/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LinkContextWrapper, useLocationStack } from '@objectiv/tracker-react-core';
import React from 'react';
import { makeAnchorClickHandler } from '../common/factories/makeAnchorClickHandler';
import { makeIdFromTrackedAnchorProps } from '../common/factories/makeIdFromTrackedAnchorProps';
import { TrackedPressableContextProps } from '../types';

/**
 * The props of TrackedLinkContext. Extends TrackedPressableProps with the `href` property.
 */
export type TrackedLinkContextProps = TrackedPressableContextProps & {
  /**
   * The destination url.
   */
  href: string;

  /**
   * Whether to forward the given href to the given Component.
   */
  forwardHref?: boolean;

  /**
   * Whether to block and wait for the Tracker having sent the event. Eg: a button redirecting to a new location.
   */
  waitUntilTracked?: boolean;
};

/**
 * Generates a new React Element already wrapped in an LinkContext.
 * Automatically tracks PressEvent when the given Component receives an `onClick` SyntheticEvent.
 */
export const TrackedLinkContext = React.forwardRef<HTMLElement, TrackedLinkContextProps>((props, ref) => {
  const {
    Component,
    id,
    title,
    href,
    forwardId = false,
    forwardTitle = false,
    forwardHref = false,
    waitUntilTracked = false,
    ...otherProps
  } = props;

  const linkId = makeIdFromTrackedAnchorProps(props);

  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
    ...(forwardTitle ? { title } : {}),
    ...(forwardHref ? { href } : {}),
  };

  const locationStack = useLocationStack();
  if (!linkId) {
    if (globalThis.objectiv) {
      const locationPath = globalThis.objectiv.getLocationPath(locationStack);
      globalThis.objectiv.TrackerConsole.error(
        `｢objectiv｣ Could not generate a valid id for LinkContext @ ${locationPath}. Please provide either the \`title\` or the \`id\` property manually.`
      );
    }

    return React.createElement(Component, componentProps);
  }

  return (
    <LinkContextWrapper id={linkId} href={href}>
      {(trackingContext) =>
        React.createElement(Component, {
          ...componentProps,
          onClick: makeAnchorClickHandler({
            trackingContext,
            anchorHref: href,
            waitUntilTracked: props.waitUntilTracked,
            onClick: props.onClick,
          }),
        })
      }
    </LinkContextWrapper>
  );
});

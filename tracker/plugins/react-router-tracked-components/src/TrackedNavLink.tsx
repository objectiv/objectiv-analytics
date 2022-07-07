/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  LinkContextWrapper,
  makeAnchorClickHandler,
  makeIdFromTrackedAnchorProps,
  useLocationStack,
} from '@objectiv/tracker-react';
import React from 'react';
import { NavLink, NavLinkProps, useHref } from 'react-router-dom';
import { ReactRouterTrackingOptionsProp } from './types';

/**
 * Wrapped NavLink will accept all NavLinkProps and, optionally, ReactRouterTrackingOptionsProp.
 */
export type TrackedNavLinkProps = NavLinkProps & ReactRouterTrackingOptionsProp;

/**
 * Wraps NavLink in a LinkContext and automatically instruments tracking PressEvent on click.
 */
export const TrackedNavLink = React.forwardRef<HTMLAnchorElement, TrackedNavLinkProps>((props, ref) => {
  const { objectiv, children, ...otherProps } = props;

  // Use ReactRouter hooks to generate the `href` prop.
  const linkContextHref = useHref(props.to);

  // Attempt to generate an id for LinkContext by looking at `id`, `title`, `children` and `objectiv.contextId` props.
  const linkContextId = makeIdFromTrackedAnchorProps({ ...props, ...objectiv });

  // If we couldn't generate an `id`, log the issue and return a regular Link component.
  const locationStack = useLocationStack();
  if (!linkContextId) {
    if (globalThis.objectiv.devTools) {
      const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
      globalThis.objectiv.devTools.TrackerConsole.error(
        `｢objectiv｣ Could not generate id for LinkContext @ ${locationPath}. Either add the \`title\` prop or specify an id manually via the  \`id\` option of the \`objectiv\` prop.`
      );
    }
    return (
      <NavLink {...otherProps} ref={ref}>
        {children}
      </NavLink>
    );
  }

  return (
    <LinkContextWrapper id={linkContextId} href={linkContextHref}>
      {(trackingContext) => (
        <NavLink
          {...otherProps}
          ref={ref}
          onClick={makeAnchorClickHandler({
            trackingContext,
            anchorHref: linkContextHref,
            waitUntilTracked: props.reloadDocument,
            onClick: props.onClick,
          })}
        >
          {children}
        </NavLink>
      )}
    </LinkContextWrapper>
  );
});

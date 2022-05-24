/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackingContext, trackPressEvent } from '@objectiv/tracker-react-core';
import React from 'react';

/**
 * This symbol is used to mark an event as handled in case we re-dispatch it. This allows us to skip handling the
 * re-dispatched event and causing an infinite loop.
 */
const EVENT_REDISPATCHED_PROPERTY = Symbol('OBJECTIV_EVENT_REDISPATCHED');

/**
 * Update the type definition of MouseEvent to allow it to get the redispatched property.
 */
declare global {
  interface MouseEvent {
    [EVENT_REDISPATCHED_PROPERTY]: boolean;
  }
}

/**
 * Anchor click handler factory parameters
 */
export type AnchorClickHandlerParameters = {
  /**
   * TrackingContext can be retrieved either from LocationWrapper render-props or via useTrackingContext.
   */
  trackingContext: TrackingContext;

  /**
   * The anchor href. This is used only when external is set to true, to resume navigation.
   */
  anchorHref: string;

  /**
   * If `true` the handler will cancel the given Event, wait until tracked (best-effort) and then resume navigation.
   */
  waitUntilTracked?: boolean;

  /**
   * Custom onClick handler that may have been passed to the Tracked Component. Will be invoked after tracking.
   */
  onClick?: (event: React.MouseEvent<HTMLAnchorElement>) => void;
};

/**
 * Anchor click handler factory
 */
export const makeAnchorClickHandler =
  (props: AnchorClickHandlerParameters) => async (event: React.MouseEvent<HTMLAnchorElement>) => {
    if (!props.waitUntilTracked) {
      // Track PressEvent: non-blocking.
      trackPressEvent(props.trackingContext);

      // Execute onClick prop, if any.
      props.onClick && props.onClick(event);
    } else {
      const nativeEvent = event.nativeEvent;

      if (nativeEvent[EVENT_REDISPATCHED_PROPERTY]) {
        // This is a redispatched event so skip it
        return;
      }

      // Prevent event from being handled by the user agent.
      event.preventDefault();

      // Track PressEvent: best-effort blocking.
      await trackPressEvent({
        ...props.trackingContext,
        options: {
          // Best-effort: wait for Queue to be empty. Times out to max 1s on very slow networks.
          waitForQueue: true,
          // Regardless whether waiting resulted in PressEvent being tracked, flush the Queue.
          flushQueue: true,
        },
      });

      // Execute onClick prop, if any.
      props.onClick && props.onClick(event);

      // Resume navigation by redispatching a clone of the original event
      const eventClone = new (nativeEvent.constructor as any)(nativeEvent.type, nativeEvent);
      eventClone[EVENT_REDISPATCHED_PROPERTY] = true;
      const target = event.currentTarget || event.target;
      target.dispatchEvent(eventClone);
    }
  };

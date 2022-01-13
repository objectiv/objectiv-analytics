/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import {
  LocationContextWrapper,
  LocationTree,
  makeContentContext,
  ObjectivProvider,
  trackPressEvent,
  usePressEventTracker,
} from '../src';

describe('LocationContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a LocationContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const locationContextProps = { locationContext: makeContentContext({ id: 'test-section' }) };
    const TrackedButton = () => {
      const trackPressEvent = usePressEventTracker();
      return <div onClick={trackPressEvent}>Trigger Event</div>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <LocationContextWrapper {...locationContextProps}>
          <TrackedButton />
        </LocationContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'ContentContext',
            id: 'test-section',
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a LocationContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const locationContextProps = { locationContext: makeContentContext({ id: 'test-section' }) };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <LocationContextWrapper {...locationContextProps}>
          {(trackingContext) => <div onClick={() => trackPressEvent(trackingContext)}>Trigger Event</div>}
        </LocationContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'ContentContext',
            id: 'test-section',
          }),
        ],
      })
    );
  });
});
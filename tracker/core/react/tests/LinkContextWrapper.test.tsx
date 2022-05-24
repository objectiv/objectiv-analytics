/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import { LinkContextWrapper, ObjectivProvider, trackPressEvent, usePressEventTracker } from '../src';

describe('LinkContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a LinkContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const linkContextProps = { id: 'test-link', href: 'test' };
    const TrackedButton = () => {
      const trackPressEvent = usePressEventTracker();
      return <a onClick={trackPressEvent}>Trigger Event</a>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <LinkContextWrapper {...linkContextProps}>
          <TrackedButton />
        </LinkContextWrapper>
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
            _type: LocationContextName.LinkContext,
            ...linkContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a LinkContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const linkContextProps = { id: 'test-link', href: 'test' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <LinkContextWrapper {...linkContextProps}>
          {(trackingContext) => <a onClick={() => trackPressEvent(trackingContext)}>Trigger Event</a>}
        </LinkContextWrapper>
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
            _type: LocationContextName.LinkContext,
            ...linkContextProps,
          }),
        ],
      })
    );
  });
});

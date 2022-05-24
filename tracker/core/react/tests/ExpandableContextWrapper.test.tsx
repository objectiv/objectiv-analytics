/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import { ExpandableContextWrapper, ObjectivProvider, trackPressEvent, usePressEventTracker } from '../src';

describe('ExpandableContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a ExpandableContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const expandableContentContextProps = { id: 'test-expandable-section' };
    const ClickableDiv = () => {
      const trackPressEvent = usePressEventTracker();
      return <span onClick={trackPressEvent}>Trigger Event</span>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ExpandableContextWrapper {...expandableContentContextProps}>
          <ClickableDiv />
        </ExpandableContextWrapper>
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
            _type: LocationContextName.ExpandableContext,
            ...expandableContentContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a ExpandableContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const expandableContentContextProps = { id: 'test-expandable-section' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ExpandableContextWrapper {...expandableContentContextProps}>
          {(trackingContext) => <div onClick={() => trackPressEvent(trackingContext)}>Trigger Event</div>}
        </ExpandableContextWrapper>
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
            _type: LocationContextName.ExpandableContext,
            ...expandableContentContextProps,
          }),
        ],
      })
    );
  });
});

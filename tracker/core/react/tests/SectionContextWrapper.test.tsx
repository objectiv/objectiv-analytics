/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationContextName, Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import { ContentContextWrapper, ObjectivProvider, trackPressEvent, usePressEventTracker } from '../src';

describe('ContentContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a ContentContext (trigger via Component)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const sectionContextProps = { id: 'test-section' };
    const TrackedButton = () => {
      const trackPressEvent = usePressEventTracker();
      return <div onClick={() => trackPressEvent()}>Trigger Event</div>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ContentContextWrapper {...sectionContextProps}>
          <TrackedButton />
        </ContentContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: [
          expect.objectContaining({
            _type: LocationContextName.ContentContext,
            ...sectionContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a ContentContext (trigger via render-props)', () => {
    const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });
    jest.spyOn(LogTransport, 'handle');

    const sectionContextProps = { id: 'test-section' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ContentContextWrapper {...sectionContextProps}>
          {(trackingContext) => <div onClick={() => trackPressEvent(trackingContext)}>Trigger Event</div>}
        </ContentContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(LogTransport.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: [
          expect.objectContaining({
            _type: LocationContextName.ContentContext,
            ...sectionContextProps,
          }),
        ],
      })
    );
  });
});

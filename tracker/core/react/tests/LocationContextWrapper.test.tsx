/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import {
  LocationContextWrapper,
  LocationTree,
  makeSectionContext,
  ObjectivProvider,
  trackClickEvent,
  useClickEventTracker,
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

    const locationContextProps = { locationContext: makeSectionContext({ id: 'test-section' }) };
    const TrackedButton = () => {
      const trackClickEvent = useClickEventTracker();
      return <div onClick={trackClickEvent}>Trigger Event</div>;
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
        _type: 'ClickEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'SectionContext',
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

    const locationContextProps = { locationContext: makeSectionContext({ id: 'test-section' }) };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <LocationContextWrapper {...locationContextProps}>
          {(trackingContext) => <div onClick={() => trackClickEvent(trackingContext)}>Trigger Event</div>}
        </LocationContextWrapper>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ClickEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'SectionContext',
            id: 'test-section',
          }),
        ],
      })
    );
  });
});

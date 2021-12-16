/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import {
  ExpandableSectionContextWrapper,
  LocationTree,
  ObjectivProvider,
  trackClickEvent,
  useClickEventTracker,
} from '../src';

describe('ExpandableSectionContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a ExpandableSectionContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const expandableSectionContextProps = { id: 'test-expandable-section' };
    const ClickableDiv = () => {
      const trackClickEvent = useClickEventTracker();
      return <span onClick={trackClickEvent}>Trigger Event</span>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ExpandableSectionContextWrapper {...expandableSectionContextProps}>
          <ClickableDiv />
        </ExpandableSectionContextWrapper>
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
            _type: 'ExpandableSectionContext',
            ...expandableSectionContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a ExpandableSectionContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const expandableSectionContextProps = { id: 'test-expandable-section' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <ExpandableSectionContextWrapper {...expandableSectionContextProps}>
          {(trackingContext) => <div onClick={() => trackClickEvent(trackingContext)}>Trigger Event</div>}
        </ExpandableSectionContextWrapper>
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
            _type: 'ExpandableSectionContext',
            ...expandableSectionContextProps,
          }),
        ],
      })
    );
  });
});

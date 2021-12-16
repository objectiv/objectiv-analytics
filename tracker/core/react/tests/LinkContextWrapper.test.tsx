/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import { LinkContextWrapper, LocationTree, ObjectivProvider, trackClickEvent, useClickEventTracker } from '../src';

describe('LinkContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a LinkContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const linkContextProps = { id: 'test-link', text: 'text', href: 'test' };
    const TrackedButton = () => {
      const trackClickEvent = useClickEventTracker();
      return <a onClick={trackClickEvent}>Trigger Event</a>;
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
        _type: 'ClickEvent',
        location_stack: [
          expect.objectContaining({
            _type: 'LinkContext',
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

    const linkContextProps = { id: 'test-link', text: 'text', href: 'test' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <LinkContextWrapper {...linkContextProps}>
          {(trackingContext) => <a onClick={() => trackClickEvent(trackingContext)}>Trigger Event</a>}
        </LinkContextWrapper>
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
            _type: 'LinkContext',
            ...linkContextProps,
          }),
        ],
      })
    );
  });
});

/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import {
  LocationTree,
  MediaPlayerContextWrapper,
  ObjectivProvider,
  trackClickEvent,
  useClickEventTracker,
} from '../src';

describe('MediaPlayerContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given children in a MediaPlayerContext (trigger via Component)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const mediaPlayerContextProps = { id: 'test-media-player' };
    const TrackedButton = () => {
      const trackClickEvent = useClickEventTracker();
      return <div onClick={trackClickEvent}>Trigger Event</div>;
    };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <MediaPlayerContextWrapper {...mediaPlayerContextProps}>
          <TrackedButton />
        </MediaPlayerContextWrapper>
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
            _type: 'MediaPlayerContext',
            ...mediaPlayerContextProps,
          }),
        ],
      })
    );
  });

  it('should wrap the given children in a MediaPlayerContext (trigger via render-props)', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });
    jest.spyOn(spyTransport, 'handle');

    const mediaPlayerContextProps = { id: 'test-media-player' };
    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <MediaPlayerContextWrapper {...mediaPlayerContextProps}>
          {(trackingContext) => <div onClick={() => trackClickEvent(trackingContext)}>Trigger Event</div>}
        </MediaPlayerContextWrapper>
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
            _type: 'MediaPlayerContext',
            ...mediaPlayerContextProps,
          }),
        ],
      })
    );
  });
});

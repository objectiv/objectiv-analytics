/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render, screen } from '@testing-library/react';
import React, { createRef } from 'react';
import { ObjectivProvider, ReactTracker, TrackedExpandableContext, usePressEventTracker } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

const TrackedButton = () => {
  const trackPressEvent = usePressEventTracker();
  return <div onClick={trackPressEvent}>Trigger Event</div>;
};

describe('TrackedExpandableContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in an ExpandableContext', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'expandable-id'}>
          <TrackedButton />
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /trigger event/i));

    expect(spyTransport.handle).toHaveBeenCalledTimes(2);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.ExpandableContext,
            id: 'expandable-id',
          }),
        ]),
      })
    );
  });

  it('should not track an HiddenEvent when initialized with isVisible=false', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'expandable-id'} isVisible={false}>
          <TrackedButton />
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    expect(spyTransport.handle).not.toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'HiddenEvent',
      })
    );
  });

  it('should track an VisibleEvent when isVisible switches from false to true and vice-versa a HiddenEvent', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const { rerender } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'expandable-id'} isVisible={false}>
          <TrackedButton />
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    expect(spyTransport.handle).not.toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'HiddenEvent',
      })
    );

    jest.resetAllMocks();

    rerender(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'expandable-id'} isVisible={true}>
          <TrackedButton />
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'VisibleEvent',
      })
    );

    jest.resetAllMocks();

    rerender(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'expandable-id'} isVisible={false}>
          <TrackedButton />
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'HiddenEvent',
      })
    );
  });

  it('should allow forwarding the id property', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'expandable-id-1'} data-testid={'test-expandable-1'}>
          test
        </TrackedExpandableContext>
        <TrackedExpandableContext
          Component={'div'}
          id={'expandable-id-2'}
          forwardId={true}
          data-testid={'test-expandable-2'}
        >
          test
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    expect(screen.getByTestId('test-expandable-1').getAttribute('id')).toBe(null);
    expect(screen.getByTestId('test-expandable-2').getAttribute('id')).toBe('expandable-id-2');
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });
    const ref = createRef<HTMLDivElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'ul'} id={'expandable-id'} ref={ref}>
          <li>option 1</li>
          <li>option 2</li>
          <li>option 3</li>
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <ul>
        <li>
          option 1
        </li>
        <li>
          option 2
        </li>
        <li>
          option 3
        </li>
      </ul>
    `);
  });
});

/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render, screen } from '@testing-library/react';
import React, { createRef } from 'react';
import {
  ObjectivProvider,
  ReactTracker,
  TrackedDiv,
  TrackedExpandableContext,
  TrackedRootLocationContext,
  usePressEventTracker,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

const TrackedButton = () => {
  const trackPressEvent = usePressEventTracker();
  return <div onClick={() => trackPressEvent()}>Trigger Event</div>;
};

describe('TrackedExpandableContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in an ExpandableContext', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'expandable-id'}>
          <TrackedButton />
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /trigger event/i));

    expect(logTransport.handle).toHaveBeenCalledTimes(2);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
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

  it('should allow disabling id normalization', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const TrackedButton = ({ children }: { children: React.ReactNode }) => {
      const trackPressEvent = usePressEventTracker();
      return <div onClick={() => trackPressEvent()}>{children}</div>;
    };

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'Expandable id 1'}>
          <TrackedButton>Trigger Event 1</TrackedButton>
        </TrackedExpandableContext>
        <TrackedExpandableContext Component={'div'} id={'Expandable id 2'} normalizeId={false}>
          <TrackedButton>Trigger Event 2</TrackedButton>
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /trigger event 1/i));
    fireEvent.click(getByText(container, /trigger event 2/i));

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.ExpandableContext,
            id: 'expandable-id-1',
          }),
        ]),
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      3,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.ExpandableContext,
            id: 'Expandable id 2',
          }),
        ]),
      })
    );
  });

  it('should console.error if an id cannot be automatically generated', () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext Component={'div'} id={'root'}>
          <TrackedDiv id={'content'}>
            <TrackedExpandableContext Component={'div'} id={'☹️'}>
              {/* nothing to see here */}
            </TrackedExpandableContext>
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for ExpandableContext @ RootLocation:root / Content:content. Please provide the `id` property.'
    );
  });

  it('should not track an HiddenEvent when initialized with isVisible=false', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'expandable-id'} isVisible={false}>
          <TrackedButton />
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    expect(logTransport.handle).not.toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'HiddenEvent',
      })
    );
  });

  it('should track an VisibleEvent when isVisible switches from false to true and vice-versa a HiddenEvent', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { rerender } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedExpandableContext Component={'div'} id={'expandable-id'} isVisible={false}>
          <TrackedButton />
        </TrackedExpandableContext>
      </ObjectivProvider>
    );

    expect(logTransport.handle).not.toHaveBeenCalledWith(
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

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(
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

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'HiddenEvent',
      })
    );
  });

  it('should allow forwarding the id property', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

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
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });
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

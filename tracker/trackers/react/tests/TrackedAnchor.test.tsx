/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import { ObjectivProvider, ReactTracker, TrackedAnchor } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedAnchor', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in a LinkContext', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedAnchor href={'/some-url'}>Trigger Event</TrackedAnchor>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.LinkContext,
            id: 'trigger-event',
            href: '/some-url',
          }),
        ]),
      })
    );
  });

  it('should allow disabling id normalization', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedAnchor href={'/some-url'}>Trigger Event 1</TrackedAnchor>
        <TrackedAnchor href={'/some-url'} normalizeId={false}>
          Trigger Event 2
        </TrackedAnchor>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event 1/i));
    fireEvent.click(getByText(container, /trigger event 2/i));

    expect(logTransport.handle).toHaveBeenCalledTimes(2);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.LinkContext,
            id: 'trigger-event-1',
            href: '/some-url',
          }),
        ]),
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.LinkContext,
            id: 'Trigger Event 2',
            href: '/some-url',
          }),
        ]),
      })
    );
  });

  it('should forwardHref to the given Component', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedAnchor href={'/some-url'} id={'test'}>
          Trigger Event
        </TrackedAnchor>
      </ObjectivProvider>
    );

    expect(container).toMatchInlineSnapshot(`
      <div>
        <a
          href="/some-url"
        >
          Trigger Event
        </a>
      </div>
    `);
  });
});

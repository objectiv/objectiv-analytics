/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import { ObjectivProvider, ReactTracker, TrackedAnchor } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedAnchor', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in a LinkContext', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedAnchor href={'/some-url'}>Trigger Event</TrackedAnchor>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(
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

  it('should forwardHref to the given Component', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

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

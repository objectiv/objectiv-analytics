/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import { ObjectivProvider, ReactTracker, TrackedButton } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedButton', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.trackersMap.delete('app-id');
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in a PressableContext', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedButton>Trigger Event</TrackedButton>
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
            _type: LocationContextName.PressableContext,
            id: 'trigger-event',
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
        <TrackedButton>Trigger Event 1</TrackedButton>
        <TrackedButton normalizeId={false}>Trigger Event 2</TrackedButton>
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
            _type: LocationContextName.PressableContext,
            id: 'trigger-event-1',
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
            _type: LocationContextName.PressableContext,
            id: 'Trigger Event 2',
          }),
        ]),
      })
    );
  });
});

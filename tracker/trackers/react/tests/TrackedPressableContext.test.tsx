/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render, screen, waitFor } from '@testing-library/react';
import React, { createRef } from 'react';
import {
  ObjectivProvider,
  ReactTracker,
  TrackedDiv,
  TrackedPressableContext,
  TrackedRootLocationContext,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedPressableContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
    jest.useRealTimers();
  });

  it('should wrap the given Component in a PressableContext', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedPressableContext Component={'button'} id={'pressable-id'}>
          Trigger Event
        </TrackedPressableContext>
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
            _type: LocationContextName.PressableContext,
            id: 'pressable-id',
          }),
        ]),
      })
    );
  });

  it('should allow forwarding the id property', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedPressableContext Component={'button'} id={'pressable-id-1'} data-testid={'test-pressable-1'}>
          test
        </TrackedPressableContext>
        <TrackedPressableContext
          Component={'button'}
          id={'pressable-id-2'}
          forwardId={true}
          data-testid={'test-pressable-2'}
        >
          test
        </TrackedPressableContext>
      </ObjectivProvider>
    );

    expect(screen.getByTestId('test-pressable-1').getAttribute('id')).toBe(null);
    expect(screen.getByTestId('test-pressable-2').getAttribute('id')).toBe('pressable-id-2');
  });

  it('should console.error if an id cannot be automatically generated', () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext Component={'div'} id={'root'}>
          <TrackedDiv id={'content'}>
            <TrackedPressableContext Component={'button'}>{/* nothing to see here */}</TrackedPressableContext>
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for PressableContext @ RootLocation:root / Content:content. Please provide either the `title` or the `id` property manually.'
    );
  });

  it('should allow forwarding the title property', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedPressableContext
          Component={'a'}
          id={'pressable-id-1'}
          title={'Press me'}
          data-testid={'test-pressable-1'}
        >
          test
        </TrackedPressableContext>
        <TrackedPressableContext
          Component={'a'}
          id={'pressable-id-2'}
          title={'Press me'}
          forwardTitle={true}
          data-testid={'test-pressable-2'}
        >
          test
        </TrackedPressableContext>
      </ObjectivProvider>
    );

    expect(screen.getByTestId('test-pressable-1').getAttribute('title')).toBe(null);
    expect(screen.getByTestId('test-pressable-2').getAttribute('title')).toBe('Press me');
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });
    const ref = createRef<HTMLDivElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedPressableContext Component={'a'} ref={ref}>
          Press me!
        </TrackedPressableContext>
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <a>
        Press me!
      </a>
    `);
  });

  it('should execute the given onClick as well', async () => {
    const clickSpy = jest.fn();
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedPressableContext Component={'button'} id={'pressable-id'} onClick={clickSpy}>
          Press me
        </TrackedPressableContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /press me/i));

    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(1));
  });
});

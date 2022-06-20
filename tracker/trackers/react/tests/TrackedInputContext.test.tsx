/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { LocationContextName, TrackerRepository } from '@objectiv/tracker-core';
import { fireEvent, render, screen } from '@testing-library/react';
import React, { createRef } from 'react';
import { ObjectivProvider, ReactTracker, TrackedDiv, TrackedInputContext, TrackedRootLocationContext } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedInputContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    TrackerRepository.trackersMap.clear();
    TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in an InputContext and not trigger InputChangeEvent on mount', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext Component={'input'} type={'text'} id={'input-id'} data-testid={'test-input'} />
      </ObjectivProvider>
    );

    fireEvent.blur(screen.getByTestId('test-input'));

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
  });

  it('should allow disabling id normalization', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext Component={'input'} type={'text'} id={'Input id 1'} data-testid={'test-input-1'} />
        <TrackedInputContext
          Component={'input'}
          type={'text'}
          id={'Input id 2'}
          normalizeId={false}
          data-testid={'test-input-2'}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.blur(screen.getByTestId('test-input-1'), { target: { value: 'some new text 1' } });
    fireEvent.blur(screen.getByTestId('test-input-2'), { target: { value: 'some new text 2' } });

    expect(spyTransport.handle).toHaveBeenCalledTimes(2);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'input-id-1',
          }),
        ]),
      })
    );
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'Input id 2',
          }),
        ]),
      })
    );
  });

  it('should console.error if an id cannot be automatically generated', () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext Component={'div'} id={'root'}>
          <TrackedDiv id={'content'}>
            <TrackedInputContext Component={'input'} type={'text'} id={'☹️'} />
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for InputContext @ RootLocation:root / Content:content. Please provide the `id` property.'
    );
  });

  it('should not track an InputChangeEvent when value did not change from the previous InputChangeEvent', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          Component={'input'}
          type={'text'}
          id={'input-id'}
          defaultValue={'some text'}
          data-testid={'test-input'}
        />
      </ObjectivProvider>
    );

    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some text' } });
    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some text' } });
    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some text' } });

    expect(spyTransport.handle).not.toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'InputChangeEvent',
      })
    );
  });

  it('should track an InputChangeEvent when value changed from the previous InputChangeEvent', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          Component={'input'}
          type={'text'}
          id={'input-id'}
          defaultValue={'some text'}
          data-testid={'test-input'}
        />
      </ObjectivProvider>
    );

    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some new text' } });

    expect(spyTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'input-id',
          }),
        ]),
      })
    );
  });

  it('should allow forwarding the id property', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          Component={'div'}
          type={'text'}
          defaultValue={'test 1'}
          id={'input-id-1'}
          data-testid={'test-input-1'}
        />
        <TrackedInputContext
          Component={'div'}
          type={'text'}
          defaultValue={'test 2'}
          id={'input-id-2'}
          forwardId={true}
          data-testid={'test-input-2'}
        />
      </ObjectivProvider>
    );

    expect(screen.getByTestId('test-input-1').getAttribute('id')).toBe(null);
    expect(screen.getByTestId('test-input-2').getAttribute('id')).toBe('input-id-2');
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });
    const ref = createRef<HTMLInputElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext Component={'input'} type={'text'} defaultValue={'test 1'} id={'input-id'} ref={ref} />
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <input
        type="text"
        value="test 1"
      />
    `);
  });

  it('should execute the given onBlur as well', () => {
    const blurSpy = jest.fn();
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          Component={'input'}
          type={'text'}
          defaultValue={''}
          id={'input-id'}
          onBlur={blurSpy}
          data-testid={'test-input'}
        />
      </ObjectivProvider>
    );

    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some text' } });

    expect(blurSpy).toHaveBeenCalledTimes(1);
  });
});

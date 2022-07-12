/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { expectToThrow, MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  GlobalContextName,
  LocationContextName,
  makeContentContext,
  Tracker,
  TrackerPlatform,
} from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import { LocationProvider, TrackingContextProvider, useLocationStack, useTracker, useTrackingContext } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);
globalThis.objectiv.devTools?.EventRecorder.configure({ enabled: false });

describe('TrackingContextProvider', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const tracker = new Tracker({ applicationId: 'app-id' });

  const expectedState = {
    locationStack: [],
    tracker: {
      platform: TrackerPlatform.CORE,
      active: true,
      applicationId: 'app-id',
      global_contexts: [],
      location_stack: [],
      plugins: expect.objectContaining({
        plugins: [
          {
            pluginName: 'OpenTaxonomyValidationPlugin',
            initialized: true,
            validationRules: [
              {
                validationRuleName: 'GlobalContextValidationRule',
                logPrefix: 'OpenTaxonomyValidationPlugin',
                contextName: GlobalContextName.ApplicationContext,
                platform: 'CORE',
                once: true,
                validate: expect.any(Function),
              },
              {
                validationRuleName: 'LocationContextValidationRule',
                logPrefix: 'OpenTaxonomyValidationPlugin',
                contextName: LocationContextName.RootLocationContext,
                platform: 'CORE',
                position: 0,
                once: true,
                validate: expect.any(Function),
                eventMatches: expect.any(Function),
              },
              {
                validationRuleName: 'GlobalContextValidationRule',
                logPrefix: 'OpenTaxonomyValidationPlugin',
                contextName: GlobalContextName.PathContext,
                platform: 'CORE',
                once: true,
                validate: expect.any(Function),
                eventMatches: expect.any(Function),
              },
            ],
          },
        ],
      }),
      queue: undefined,
      trackerId: 'app-id',
      transport: undefined,
    },
  };

  it('developers tools should have been imported', async () => {
    expect(globalThis.objectiv).not.toBeUndefined();
  });

  it('should support children components', () => {
    const Component = () => {
      const trackingContext = useTrackingContext();

      console.log(trackingContext);

      return null;
    };

    render(
      <TrackingContextProvider tracker={tracker}>
        <Component />
      </TrackingContextProvider>
    );

    expect(console.log).toHaveBeenCalledTimes(1);
    expect(console.log).toHaveBeenNthCalledWith(1, expectedState);
  });

  it('should support render-props', () => {
    render(
      <TrackingContextProvider tracker={tracker}>
        {(trackingContext) => console.log(trackingContext)}
      </TrackingContextProvider>
    );

    expect(console.log).toHaveBeenCalledTimes(1);
    expect(console.log).toHaveBeenNthCalledWith(1, expectedState);
  });

  it('should inherit location from parents', () => {
    const rootSection = makeContentContext({ id: 'root' });

    const Component = () => {
      const trackingContext = useTrackingContext();

      console.log(trackingContext);

      return null;
    };

    render(
      <LocationProvider locationStack={[rootSection]}>
        <TrackingContextProvider tracker={tracker}>
          <Component />
        </TrackingContextProvider>
      </LocationProvider>
    );

    expect(console.log).toHaveBeenCalledTimes(1);
    expect(console.log).toHaveBeenNthCalledWith(1, {
      locationStack: [rootSection],
      tracker: expectedState.tracker,
    });
  });

  it('should support extending the location', () => {
    const rootSection = makeContentContext({ id: 'root' });
    const childSection = makeContentContext({ id: 'child' });

    const Component = () => {
      const trackingContext = useTrackingContext();

      console.log(trackingContext);

      return null;
    };

    render(
      <LocationProvider locationStack={[rootSection]}>
        <TrackingContextProvider tracker={tracker} locationStack={[childSection]}>
          <Component />
        </TrackingContextProvider>
      </LocationProvider>
    );

    expect(console.log).toHaveBeenCalledTimes(1);
    expect(console.log).toHaveBeenNthCalledWith(1, {
      locationStack: [rootSection, childSection],
      tracker: expectedState.tracker,
    });
  });

  it('should throw when LocationProvider is not higher up in the component tree', () => {
    const Component = () => {
      useLocationStack();
      return null;
    };

    expectToThrow(
      () => {
        render(<Component />);
      },
      `
      Couldn't get a LocationStack. 
      Is the Component in a ObjectivProvider, TrackingContextProvider or LocationProvider?
    `
    );
  });

  it('should throw when TrackerProvider is not higher up in the component tree', () => {
    const Component = () => {
      useTracker();
      return null;
    };

    expectToThrow(
      () => {
        render(<Component />);
      },
      `
      Couldn't get a Tracker. 
      Is the Component in a ObjectivProvider, TrackingContextProvider or TrackerProvider?
    `
    );
  });
});

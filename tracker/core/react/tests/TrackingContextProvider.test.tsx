/*
 * Copyright 2021 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import {
  LocationProvider,
  makeSectionContext,
  TrackingContextProvider,
  useLocationStack,
  useTracker,
  useTrackingContext,
} from '../src';

describe('TrackingContextProvider', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const tracker = new Tracker({ applicationId: 'app-id' });

  const expectedState = {
    locationStack: [],
    tracker: {
      active: true,
      applicationId: 'app-id',
      console: undefined,
      global_contexts: [],
      location_stack: [],
      plugins: {
        console: undefined,
        plugins: [
          {
            applicationContext: { __global_context: true, _type: 'ApplicationContext', id: 'app-id' },
            console: undefined,
            pluginName: 'ApplicationContextPlugin',
          },
        ],
      },
      queue: undefined,
      trackerId: 'app-id',
      transport: undefined,
    },
  };

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
    const rootSection = makeSectionContext({ id: 'root' });

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
    const rootSection = makeSectionContext({ id: 'root' });
    const childSection = makeSectionContext({ id: 'child' });

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

    expect(() => render(<Component />)).toThrow(`
      Couldn't get a LocationStack. 
      Is the Component in a ObjectivProvider, TrackingContextProvider or LocationProvider?
    `);
  });

  it('should throw when TrackerProvider is not higher up in the component tree', () => {
    const Component = () => {
      useTracker();
      return null;
    };

    expect(() => render(<Component />)).toThrow(`
      Couldn't get a Tracker. 
      Is the Component in a ObjectivProvider, TrackingContextProvider or TrackerProvider?
    `);
  });
});

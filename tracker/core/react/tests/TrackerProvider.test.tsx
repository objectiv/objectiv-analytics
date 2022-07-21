/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { GlobalContextName, LocationContextName, Tracker, TrackerPlatform } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import { TrackerProvider, useTracker } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);
globalThis.objectiv.devTools?.EventRecorder.configure({ enabled: false });

describe('TrackerProvider', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const tracker = new Tracker({ applicationId: 'app-id' });

  const expectedState = {
    tracker: {
      platform: TrackerPlatform.CORE,
      active: true,
      applicationId: 'app-id',
      generateGUID: expect.any(Function),
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
      const trackerContext = useTracker();

      console.log({ tracker: trackerContext });

      return null;
    };

    render(
      <TrackerProvider tracker={tracker}>
        <Component />
      </TrackerProvider>
    );

    expect(console.log).toHaveBeenCalledTimes(1);
    expect(console.log).toHaveBeenNthCalledWith(1, expectedState);
  });

  it('should support render-props', () => {
    render(<TrackerProvider tracker={tracker}>{(trackerContext) => console.log(trackerContext)}</TrackerProvider>);

    expect(console.log).toHaveBeenCalledTimes(1);
    expect(console.log).toHaveBeenNthCalledWith(1, expectedState);
  });
});

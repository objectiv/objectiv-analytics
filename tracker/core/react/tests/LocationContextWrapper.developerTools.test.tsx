/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import '@objectiv/developer-tools';
import { makeContentContext, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import { LocationContextWrapper, ObjectivProvider } from '../src';

describe('LocationContextWrapper', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('developers tools should have been imported', async () => {
    expect(globalThis.objectiv).not.toBeUndefined();
  });

  it('LocationTree should be called on mount and re-synced on re-render', () => {
    const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
    const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

    if (globalThis.objectiv) {
      jest.spyOn(globalThis.objectiv.LocationTree, 'add');
      jest.spyOn(globalThis.objectiv.LocationTree, 'remove');
    }

    const { rerender } = render(
      <ObjectivProvider tracker={tracker}>
        <LocationContextWrapper locationContext={makeContentContext({ id: 'test-section-1' })}>
          test
        </LocationContextWrapper>
      </ObjectivProvider>
    );

    expect(globalThis.objectiv?.LocationTree.add).toHaveBeenCalledTimes(1);
    expect(globalThis.objectiv?.LocationTree.remove).not.toHaveBeenCalled();

    jest.resetAllMocks();

    rerender(
      <ObjectivProvider tracker={tracker}>
        <LocationContextWrapper locationContext={makeContentContext({ id: 'test-section-2' })}>
          test
        </LocationContextWrapper>
      </ObjectivProvider>
    );

    expect(globalThis.objectiv?.LocationTree.add).toHaveBeenCalledTimes(1);
    expect(globalThis.objectiv?.LocationTree.remove).toHaveBeenCalledTimes(1);
  });
});

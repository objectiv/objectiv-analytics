/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import React from 'react';
import { ContentContextWrapper, ObjectivProvider, useParentLocationContext } from '../src/';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('useParentLocationContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should return the parent location context', () => {
    const tracker = new Tracker({ applicationId: 'app-id' });

    const TestChild = () => {
      const parentLocationContext = useParentLocationContext();

      console.log(parentLocationContext);

      return <div>test child</div>;
    };

    render(
      <ObjectivProvider tracker={tracker}>
        <ContentContextWrapper id={'parent-1'}>
          <ContentContextWrapper id={'parent-2'}>
            <TestChild />
          </ContentContextWrapper>
        </ContentContextWrapper>
      </ObjectivProvider>
    );

    expect(console.log).toHaveBeenCalledTimes(1);
    expect(console.log).toHaveBeenNthCalledWith(1, expect.objectContaining({ id: 'parent-2' }));
  });
});

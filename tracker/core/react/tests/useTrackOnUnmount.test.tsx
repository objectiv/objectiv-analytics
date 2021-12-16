/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionHiddenEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import { useEffect } from 'react';
import { TrackerProvider, useTrackOnUnmount } from '../src';

describe('useTrackOnUnmount', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
  const renderSpy = jest.fn();
  const tracker = new Tracker({ applicationId: 'app-id', transport: spyTransport });

  const Index = () => {
    return (
      <TrackerProvider tracker={tracker}>
        <Application />
      </TrackerProvider>
    );
  };

  const Application = () => {
    useTrackOnUnmount({ event: makeSectionHiddenEvent() });

    useEffect(renderSpy);

    return <>Test application</>;
  };

  it('should not execute on mount', () => {
    render(<Index />);

    expect(spyTransport.handle).not.toHaveBeenCalled();
  });

  it('should execute on unmount', () => {
    const { unmount } = render(<Index />);

    unmount();

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'SectionHiddenEvent' }));
  });

  it('should not execute on rerender', () => {
    const { rerender } = render(<Index />);

    rerender(<Index />);
    rerender(<Index />);

    expect(renderSpy).toHaveBeenCalledTimes(3);
    expect(spyTransport.handle).not.toHaveBeenCalled();
  });

  it('should allow overriding the tracker with a custom one', () => {
    const spyTransport2 = {
      transportName: 'spyTransport2',
      handle: jest.fn(),
      isUsable: () => true,
    };
    const anotherTracker = new Tracker({ applicationId: 'app-id', transport: spyTransport2 });
    const { unmount } = renderHook(() =>
      useTrackOnUnmount({ event: makeSectionHiddenEvent(), tracker: anotherTracker })
    );

    unmount();

    expect(spyTransport.handle).not.toHaveBeenCalled();
    expect(spyTransport2.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport2.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'SectionHiddenEvent' }));
  });
});

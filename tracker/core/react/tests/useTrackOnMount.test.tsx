/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionVisibleEvent, Tracker } from '@objectiv/tracker-core';
import { render } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import { useEffect } from 'react';
import { TrackerProvider, useTrackOnMount } from '../src';

describe('useTrackOnMount', () => {
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
    useTrackOnMount({ event: makeSectionVisibleEvent() });

    useEffect(renderSpy);

    return <>Test application</>;
  };

  it('should execute once on mount', () => {
    render(<Index />);

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'SectionVisibleEvent' }));
  });

  it('should not execute on unmount', () => {
    const { unmount } = render(<Index />);

    unmount();

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'SectionVisibleEvent' }));
  });

  it('should not execute on rerender', () => {
    const { rerender } = render(<Index />);

    rerender(<Index />);
    rerender(<Index />);

    expect(renderSpy).toHaveBeenCalledTimes(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'SectionVisibleEvent' }));
  });

  it('should allow overriding the tracker with a custom one', () => {
    const spyTransport2 = { transportName: 'spyTransport2', handle: jest.fn(), isUsable: () => true };
    const anotherTracker = new Tracker({ applicationId: 'app-id', transport: spyTransport2 });
    renderHook(() => useTrackOnMount({ event: makeSectionVisibleEvent(), tracker: anotherTracker }));

    expect(spyTransport.handle).not.toHaveBeenCalled();
    expect(spyTransport2.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport2.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'SectionVisibleEvent' }));
  });
});

import { render } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import { useEffect } from 'react';
import { ReactTracker, TrackerContextProvider, useTrackApplicationLoaded } from '../src';

describe('useTrackApplicationLoaded', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const spyTransport = {
    transportName: 'SpyTransport',
    handle: jest.fn(),
    isUsable: () => true,
  };

  const renderSpy = jest.fn();

  const tracker = new ReactTracker({ transport: spyTransport });

  const Index = () => {
    return (
      <TrackerContextProvider tracker={tracker}>
        <Application />
      </TrackerContextProvider>
    );
  };

  const Application = () => {
    useTrackApplicationLoaded();

    useEffect(renderSpy);

    return <>Test application</>;
  };

  it('should execute once on mount', () => {
    render(<Index />);

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ event: 'ApplicationLoadedEvent' }));
  });

  it('should not execute on unmount', () => {
    const { unmount } = render(<Index />);

    unmount();

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ event: 'ApplicationLoadedEvent' }));
  });

  it('should not execute on rerender', () => {
    const { rerender } = render(<Index />);

    rerender(<Index />);
    rerender(<Index />);

    expect(renderSpy).toHaveBeenCalledTimes(3);
    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ event: 'ApplicationLoadedEvent' }));
  });

  it('should allow overriding the tracker with a custom one', () => {
    const spyTransport2 = {
      transportName: 'spyTransport2',
      handle: jest.fn(),
      isUsable: () => true,
    };
    const anotherTracker = new ReactTracker({ transport: spyTransport2 });
    renderHook(() => useTrackApplicationLoaded(anotherTracker));

    expect(spyTransport.handle).not.toHaveBeenCalled();
    expect(spyTransport2.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport2.handle).toHaveBeenCalledWith(expect.objectContaining({ event: 'ApplicationLoadedEvent' }));
  });
});

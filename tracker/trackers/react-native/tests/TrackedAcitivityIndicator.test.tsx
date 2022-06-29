/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { render } from '@testing-library/react-native';
import React from 'react';
import {
  ReactNativeTracker,
  RootLocationContextWrapper,
  TrackedActivityIndicator,
  TrackedActivityIndicatorProps,
  TrackingContextProvider,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedActivityIndicator', () => {
  const logTransport = new LogTransport();
  jest.spyOn(logTransport, 'handle');
  const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: logTransport });

  const TestTrackedActivityIndicator = (props: TrackedActivityIndicatorProps & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedActivityIndicator {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should not track VisibleEvent nor HiddenEvent when visible is undefined', () => {
    const { rerender } = render(<TestTrackedActivityIndicator id={'test-activity-indicator'} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} />);
    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} />);
    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should not track VisibleEvent when visible toggles from undefined to true', () => {
    const { rerender } = render(<TestTrackedActivityIndicator id={'test-activity-indicator'} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should not track HiddenEvent when visible toggles from true to undefined', () => {
    const { rerender } = render(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={undefined} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should not track VisibleEvent when visible did not change', () => {
    const { rerender } = render(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={true} />);
    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={true} />);
    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should not track HiddenEvent when visible did not change', () => {
    const { rerender } = render(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={false} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={false} />);
    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={false} />);
    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={false} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should track VisibleEvent when visible toggles from false to true', () => {
    const { rerender } = render(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={false} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={true} />);

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'VisibleEvent' }));
  });

  it('should track HiddenEvent when visible toggles from true to false', () => {
    const { rerender } = render(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedActivityIndicator id={'test-activity-indicator'} animating={false} />);

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'HiddenEvent' }));
  });
});

/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { render } from '@testing-library/react-native';
import React from 'react';
import {
  ReactNativeTracker,
  RootLocationContextWrapper,
  TrackedModal,
  TrackedModalProps,
  TrackingContextProvider,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedModal', () => {
  const logTransport = new LogTransport();
  jest.spyOn(logTransport, 'handle');
  const tracker = new ReactNativeTracker({ applicationId: 'app-id', transport: logTransport });

  const TestTrackedModal = (props: TrackedModalProps & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedModal {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should not track VisibleEvent nor HiddenEvent when visible is undefined', () => {
    const { rerender } = render(<TestTrackedModal id={'test-modal'} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedModal id={'test-modal'} />);
    rerender(<TestTrackedModal id={'test-modal'} />);
    rerender(<TestTrackedModal id={'test-modal'} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should not track VisibleEvent when visible toggles from undefined to true', () => {
    const { rerender } = render(<TestTrackedModal id={'test-modal'} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedModal id={'test-modal'} visible={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should not track HiddenEvent when visible toggles from true to undefined', () => {
    const { rerender } = render(<TestTrackedModal id={'test-modal'} visible={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedModal id={'test-modal'} visible={undefined} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should not track VisibleEvent when visible did not change', () => {
    const { rerender } = render(<TestTrackedModal id={'test-modal'} visible={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedModal id={'test-modal'} visible={true} />);
    rerender(<TestTrackedModal id={'test-modal'} visible={true} />);
    rerender(<TestTrackedModal id={'test-modal'} visible={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should not track HiddenEvent when visible did not change', () => {
    const { rerender } = render(<TestTrackedModal id={'test-modal'} visible={false} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedModal id={'test-modal'} visible={false} />);
    rerender(<TestTrackedModal id={'test-modal'} visible={false} />);
    rerender(<TestTrackedModal id={'test-modal'} visible={false} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));
  });

  it('should track VisibleEvent when visible toggles from false to true', () => {
    const { rerender } = render(<TestTrackedModal id={'test-modal'} visible={false} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedModal id={'test-modal'} visible={true} />);

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'VisibleEvent' }));
  });

  it('should track HiddenEvent when visible toggles from true to false', () => {
    const { rerender } = render(<TestTrackedModal id={'test-modal'} visible={true} />);

    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'VisibleEvent' }));
    expect(logTransport.handle).not.toHaveBeenCalledWith(expect.objectContaining({ _type: 'HiddenEvent' }));

    rerender(<TestTrackedModal id={'test-modal'} visible={false} />);

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'HiddenEvent' }));
  });
});

/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { Tracker } from '@objectiv/tracker-core';
import { fireEvent, render, screen } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import React from 'react';
import { useEffect, useState } from 'react';
import { TrackerProvider, useTrackOnChange } from '../src';

describe('useTrackOnChange', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const LogTransport = { transportName: 'LogTransport', handle: jest.fn(), isUsable: () => true };
  const renderSpy = jest.fn();
  const tracker = new Tracker({ applicationId: 'app-id', transport: LogTransport });

  const menuToggleEvent = { _type: 'MenuToggleEvent', location_stack: [], global_contexts: [] };

  const Index = () => {
    return (
      <TrackerProvider tracker={tracker}>
        <Application />
      </TrackerProvider>
    );
  };

  const Menu = ({ isOpen }: { isOpen: boolean }) => {
    return !isOpen ? null : (
      <ul>
        <li>Menu1</li>
        <li>Menu2</li>
        <li>Menu3</li>
      </ul>
    );
  };

  const Application = () => {
    const [menuOpen, setMenuOpen] = useState(false);
    useTrackOnChange({ state: menuOpen, event: menuToggleEvent });

    useEffect(renderSpy);

    return (
      <>
        Test application
        <Menu isOpen={menuOpen} />
        <button data-testid="toggle-menu" onClick={() => setMenuOpen(!menuOpen)} value="Toggle Menu" />
      </>
    );
  };

  it('should not execute on mount', () => {
    render(<Index />);

    expect(LogTransport.handle).not.toHaveBeenCalled();
  });

  it('should not execute on unmount', () => {
    const { unmount } = render(<Index />);

    unmount();

    expect(LogTransport.handle).not.toHaveBeenCalled();
  });

  it('should not execute on rerender', () => {
    const { rerender } = render(<Index />);

    rerender(<Index />);
    rerender(<Index />);

    expect(renderSpy).toHaveBeenCalledTimes(3);
    expect(LogTransport.handle).not.toHaveBeenCalled();
  });

  it('should execute on state change', () => {
    render(<Index />);

    const toggleMenuButton = screen.getByTestId('toggle-menu');

    fireEvent.click(toggleMenuButton);
    fireEvent.click(toggleMenuButton);
    fireEvent.click(toggleMenuButton);

    expect(LogTransport.handle).toHaveBeenCalledTimes(3);
    expect(LogTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'MenuToggleEvent' }));
  });

  it('should allow overriding the tracker with a custom one', () => {
    const LogTransport2 = { transportName: 'LogTransport2', handle: jest.fn(), isUsable: () => true };
    const anotherTracker = new Tracker({ applicationId: 'app-id', transport: LogTransport2 });
    const { rerender } = renderHook((state) =>
      useTrackOnChange({ state, event: menuToggleEvent, tracker: anotherTracker })
    );

    rerender({ state: true });

    expect(LogTransport.handle).not.toHaveBeenCalled();
    expect(LogTransport2.handle).toHaveBeenCalledTimes(1);
    expect(LogTransport2.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'MenuToggleEvent' }));
  });
});

/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeSectionHiddenEvent, makeSectionVisibleEvent, Tracker } from '@objectiv/tracker-core';
import { fireEvent, render, screen } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import { useEffect, useState } from 'react';
import { TrackerProvider, useTrackOnToggle } from '../src';

describe('useTrackOnToggle', () => {
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

  const Menu = () => (
    <ul>
      <li>Menu1</li>
      <li>Menu2</li>
      <li>Menu3</li>
    </ul>
  );

  const Application = () => {
    const [menuOpen, setMenuOpen] = useState(false);
    useTrackOnToggle({ state: menuOpen, trueEvent: makeSectionVisibleEvent(), falseEvent: makeSectionHiddenEvent() });

    useEffect(renderSpy);

    return (
      <>
        Test application
        {menuOpen ? <Menu /> : null}
        <button data-testid="toggle-menu" onClick={() => setMenuOpen(!menuOpen)} value="Toggle Menu" />
      </>
    );
  };

  it('should not execute on mount', () => {
    render(<Index />);

    expect(spyTransport.handle).not.toHaveBeenCalled();
  });

  it('should not execute on unmount', () => {
    const { unmount } = render(<Index />);

    unmount();

    expect(spyTransport.handle).not.toHaveBeenCalled();
  });

  it('should not execute on rerender', () => {
    const { rerender } = render(<Index />);

    rerender(<Index />);
    rerender(<Index />);

    expect(renderSpy).toHaveBeenCalledTimes(3);
    expect(spyTransport.handle).not.toHaveBeenCalled();
  });

  it('should execute on state change', () => {
    render(<Index />);

    const toggleMenuButton = screen.getByTestId('toggle-menu');

    fireEvent.click(toggleMenuButton);
    fireEvent.click(toggleMenuButton);
    fireEvent.click(toggleMenuButton);

    expect(spyTransport.handle).toHaveBeenCalledTimes(3);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'SectionVisibleEvent' }));
    expect(spyTransport.handle).toHaveBeenNthCalledWith(2, expect.objectContaining({ _type: 'SectionHiddenEvent' }));
    expect(spyTransport.handle).toHaveBeenNthCalledWith(3, expect.objectContaining({ _type: 'SectionVisibleEvent' }));
  });

  it('should allow overriding the tracker with a custom one', () => {
    const spyTransport2 = { transportName: 'spyTransport2', handle: jest.fn(), isUsable: () => true };
    const anotherTracker = new Tracker({ applicationId: 'app-id', transport: spyTransport2 });
    const { rerender } = renderHook(
      (state) =>
        useTrackOnToggle({
          state,
          trueEvent: makeSectionVisibleEvent(),
          falseEvent: makeSectionHiddenEvent(),
          tracker: anotherTracker,
        }),
      { initialProps: false }
    );

    rerender(true);
    rerender(false);

    expect(spyTransport.handle).not.toHaveBeenCalled();
    expect(spyTransport2.handle).toHaveBeenCalledTimes(2);
    expect(spyTransport2.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'SectionVisibleEvent' }));
    expect(spyTransport2.handle).toHaveBeenNthCalledWith(2, expect.objectContaining({ _type: 'SectionHiddenEvent' }));
  });
});

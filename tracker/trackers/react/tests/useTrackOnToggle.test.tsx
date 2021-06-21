import { makeSectionHiddenEvent, makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { fireEvent, render, screen } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import { useEffect, useState } from 'react';
import { ReactTracker, TrackerContextProvider, useTrackOnToggle } from '../src';

describe('useTrackOnToggle', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
  const renderSpy = jest.fn();
  const tracker = new ReactTracker({ transport: spyTransport });

  const Index = () => {
    return (
      <TrackerContextProvider tracker={tracker}>
        <Application />
      </TrackerContextProvider>
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
    useTrackOnToggle(menuOpen, makeSectionVisibleEvent(), makeSectionHiddenEvent());

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
    expect(spyTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ event: 'SectionVisibleEvent' }));
    expect(spyTransport.handle).toHaveBeenNthCalledWith(2, expect.objectContaining({ event: 'SectionHiddenEvent' }));
    expect(spyTransport.handle).toHaveBeenNthCalledWith(3, expect.objectContaining({ event: 'SectionVisibleEvent' }));
  });

  it('should allow overriding the tracker with a custom one', () => {
    const spyTransport2 = { transportName: 'spyTransport2', handle: jest.fn(), isUsable: () => true };
    const anotherTracker = new ReactTracker({ transport: spyTransport2 });
    const { rerender } = renderHook(
      (state) => useTrackOnToggle(state, makeSectionVisibleEvent(), makeSectionHiddenEvent(), anotherTracker),
      { initialProps: false }
    );

    rerender(true);
    rerender(false);

    expect(spyTransport.handle).not.toHaveBeenCalled();
    expect(spyTransport2.handle).toHaveBeenCalledTimes(2);
    expect(spyTransport2.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ event: 'SectionVisibleEvent' }));
    expect(spyTransport2.handle).toHaveBeenNthCalledWith(2, expect.objectContaining({ event: 'SectionHiddenEvent' }));
  });
});

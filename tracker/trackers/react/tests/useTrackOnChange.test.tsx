import { fireEvent, render, screen } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import { useEffect, useState } from 'react';
import { ReactTracker, TrackerContextProvider, useTrackOnChange } from '../src';

describe('useTrackOnChange', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
  const renderSpy = jest.fn();
  const tracker = new ReactTracker({ transport: spyTransport });

  const menuToggleEvent = { event: 'MenuToggleEvent', location_stack: [], global_contexts: [] };

  const Index = () => {
    return (
      <TrackerContextProvider tracker={tracker}>
        <Application />
      </TrackerContextProvider>
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
    useTrackOnChange(menuOpen, menuToggleEvent);

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
    expect(spyTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ event: 'MenuToggleEvent' }));
  });

  it('should allow overriding the tracker with a custom one', () => {
    const spyTransport2 = { transportName: 'spyTransport2', handle: jest.fn(), isUsable: () => true };
    const anotherTracker = new ReactTracker({ transport: spyTransport2 });
    const { rerender } = renderHook((state) => useTrackOnChange(state, menuToggleEvent, anotherTracker));

    rerender({ state: true });

    expect(spyTransport.handle).not.toHaveBeenCalled();
    expect(spyTransport2.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport2.handle).toHaveBeenCalledWith(expect.objectContaining({ event: 'MenuToggleEvent' }));
  });
});

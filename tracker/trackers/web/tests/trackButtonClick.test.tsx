import { makeButtonContext } from '@objectiv/tracker-core';
import { trackButtonClick, WebTracker } from '../src';

describe('trackButtonClick', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
  const tracker = new WebTracker({ transport: spyTransport });

  it('should execute when invoked', () => {
    trackButtonClick(makeButtonContext({ id: 'buttonA', text: 'confirm button' }), tracker);

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        event: 'ClickEvent',
        global_contexts: expect.arrayContaining([expect.objectContaining({ _context_type: 'DeviceContext' })]),
        location_stack: expect.arrayContaining([expect.objectContaining({ _context_type: 'ButtonContext' })]),
      })
    );
  });
});

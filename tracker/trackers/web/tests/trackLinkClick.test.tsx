import { makeLinkContext } from '@objectiv/tracker-core';
import { trackLinkClick, WebTracker } from '../src';

describe('trackLinkClick', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const spyTransport = { transportName: 'SpyTransport', handle: jest.fn(), isUsable: () => true };
  const tracker = new WebTracker({ transport: spyTransport });

  it('should execute when invoked', () => {
    trackLinkClick(makeLinkContext({ id: 'linkA', text: 'confirm link', href: '/path' }), tracker);

    expect(spyTransport.handle).toHaveBeenCalledTimes(1);
    expect(spyTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        event: 'ClickEvent',
        global_contexts: expect.arrayContaining([expect.objectContaining({ _context_type: 'DeviceContext' })]),
        location_stack: expect.arrayContaining([expect.objectContaining({ _context_type: 'LinkContext' })]),
      })
    );
  });
});

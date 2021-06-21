import {
  makeActionContext,
  makeButtonContext,
  makeCookieIdContext,
  makeDeviceContext,
  makeErrorContext,
  makeExpandableSectionContext,
  makeHttpContext,
  makeInputContext,
  makeItemContext,
  makeLinkContext,
  makeMediaPlayerContext,
  makeNavigationContext,
  makeOverlayContext,
  makeScreenContext,
  makeSectionContext,
  makeSessionContext,
  makeWebDocumentContext,
} from '../src';

describe('Context Factories', () => {
  it('SectionContext', () => {
    expect(makeSectionContext({ id: 'section-A' })).toStrictEqual({
      __location_context: true,
      __section_context: true,
      _context_type: 'SectionContext',
      id: 'section-A',
    });
  });

  it('WebDocumentContext', () => {
    expect(makeWebDocumentContext({ id: '#document-a', url: '/test' })).toStrictEqual({
      __location_context: true,
      __section_context: true,
      _context_type: 'WebDocumentContext',
      id: '#document-a',
      url: '/test',
    });
  });

  it('ScreenContext', () => {
    expect(makeScreenContext({ id: 'home-screen', screen: 'home-screen' })).toStrictEqual({
      __location_context: true,
      __section_context: true,
      _context_type: 'ScreenContext',
      id: 'home-screen',
      screen: 'home-screen',
    });
  });

  it('ExpandableSectionContext', () => {
    expect(makeExpandableSectionContext({ id: 'accordion-a' })).toStrictEqual({
      __location_context: true,
      __section_context: true,
      _context_type: 'ExpandableSectionContext',
      id: 'accordion-a',
    });
  });

  it('MediaPlayerContext', () => {
    expect(makeMediaPlayerContext({ id: 'player-1' })).toStrictEqual({
      __location_context: true,
      __section_context: true,
      _context_type: 'MediaPlayerContext',
      id: 'player-1',
    });
  });

  it('NavigationContext', () => {
    expect(makeNavigationContext({ id: 'top-nav' })).toStrictEqual({
      __location_context: true,
      __section_context: true,
      _context_type: 'NavigationContext',
      id: 'top-nav',
    });
  });

  it('OverlayContext', () => {
    expect(makeOverlayContext({ id: 'top-menu' })).toStrictEqual({
      __location_context: true,
      __section_context: true,
      _context_type: 'OverlayContext',
      id: 'top-menu',
    });
  });

  it('ItemContext', () => {
    expect(makeItemContext({ id: 'item-1' })).toStrictEqual({
      __location_context: true,
      __item_context: true,
      _context_type: 'ItemContext',
      id: 'item-1',
    });
  });

  it('InputContext', () => {
    expect(makeInputContext({ id: 'input-1' })).toStrictEqual({
      __location_context: true,
      __item_context: true,
      _context_type: 'InputContext',
      id: 'input-1',
    });
  });

  it('ActionContext', () => {
    expect(makeActionContext({ id: 'chevron-right', path: '/next', text: 'Next Slide' })).toStrictEqual({
      __location_context: true,
      __item_context: true,
      __action_context: true,
      _context_type: 'ActionContext',
      id: 'chevron-right',
      path: '/next',
      text: 'Next Slide',
    });
  });

  it('ButtonContext', () => {
    expect(makeButtonContext({ id: 'confirm-data', text: 'Confirm' })).toStrictEqual({
      __location_context: true,
      __item_context: true,
      __action_context: true,
      _context_type: 'ButtonContext',
      id: 'confirm-data',
      path: '',
      text: 'Confirm',
    });
  });

  it('LinkContext', () => {
    expect(makeLinkContext({ id: 'confirm-data', href: '/some/url', text: 'Click for Details' })).toStrictEqual({
      __location_context: true,
      __item_context: true,
      __action_context: true,
      _context_type: 'LinkContext',
      id: 'confirm-data',
      path: '/some/url',
      text: 'Click for Details',
    });
  });

  it('DeviceContext', () => {
    expect(makeDeviceContext({ userAgent: 'user agent string' })).toStrictEqual({
      __global_context: true,
      _context_type: 'DeviceContext',
      id: 'device',
      'user-agent': 'user agent string',
    });
  });

  it('ErrorContext', () => {
    expect(makeErrorContext({ id: 'error-id', message: 'error description' })).toStrictEqual({
      __global_context: true,
      _context_type: 'ErrorContext',
      id: 'error-id',
      message: 'error description',
    });
  });

  it('CookieIdContext', () => {
    expect(makeCookieIdContext({ id: 'error-id', cookieId: '12345' })).toStrictEqual({
      __global_context: true,
      _context_type: 'CookieIdContext',
      id: 'error-id',
      cookie_id: '12345', // Note: the cookieId parameter is mapped to cookie_id
    });
  });

  it('SessionContext', () => {
    expect(makeSessionContext({ id: 'session-id', hitNumber: 123 })).toStrictEqual({
      __global_context: true,
      _context_type: 'SessionContext',
      id: 'session-id',
      hitNumber: 123,
    });
  });

  it('HttpContext', () => {
    expect(makeHttpContext({ id: 'http', host: 'host', userAgent: 'ua', remoteAddr: '0.0.0.0' })).toStrictEqual({
      __global_context: true,
      _context_type: 'HttpContext',
      id: 'http',
      host: 'host',
      'user-agent': 'ua',
      remoteAddr: '0.0.0.0',
    });
  });
});

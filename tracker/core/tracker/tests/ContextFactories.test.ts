/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  makeApplicationContext,
  makeContentContext,
  makeCookieIdContext,
  makeExpandableContext,
  makeHttpContext,
  makeInputContext,
  makeLinkContext,
  makeMarketingContext,
  makeMediaPlayerContext,
  makeNavigationContext,
  makeOverlayContext,
  makePathContext,
  makePressableContext,
  makeRootLocationContext,
  makeSessionContext,
} from '../src';

describe('Context Factories', () => {
  it('ApplicationContext', () => {
    expect(makeApplicationContext({ id: 'app' })).toStrictEqual({
      __global_context: true,
      _type: 'ApplicationContext',
      id: 'app',
    });
  });

  it('ContentContext', () => {
    expect(makeContentContext({ id: 'content-A' })).toStrictEqual({
      __location_context: true,
      _type: 'ContentContext',
      id: 'content-A',
    });
  });

  it('CookieIdContext', () => {
    expect(makeCookieIdContext({ id: 'error-id', cookie_id: '12345' })).toStrictEqual({
      __global_context: true,
      _type: 'CookieIdContext',
      id: 'error-id',
      cookie_id: '12345', // Note: the cookieId parameter is mapped to cookie_id
    });
  });

  it('ExpandableContext', () => {
    expect(makeExpandableContext({ id: 'accordion-a' })).toStrictEqual({
      __location_context: true,
      _type: 'ExpandableContext',
      id: 'accordion-a',
    });
  });

  it('HttpContext', () => {
    expect(
      makeHttpContext({ id: 'http', referrer: 'referrer', user_agent: 'ua', remote_address: '0.0.0.0' })
    ).toStrictEqual({
      __global_context: true,
      _type: 'HttpContext',
      id: 'http',
      referrer: 'referrer',
      user_agent: 'ua',
      remote_address: '0.0.0.0',
    });

    expect(
      makeHttpContext({ id: 'http', referrer: 'referrer', user_agent: 'ua' })
    ).toStrictEqual({
      __global_context: true,
      _type: 'HttpContext',
      id: 'http',
      referrer: 'referrer',
      user_agent: 'ua',
      remote_address: null
    });
  });

  it('InputContext', () => {
    expect(makeInputContext({ id: 'input-1' })).toStrictEqual({
      __location_context: true,
      _type: 'InputContext',
      id: 'input-1',
    });
  });

  it('LinkContext', () => {
    expect(makeLinkContext({ id: 'confirm-data', href: '/some/url' })).toStrictEqual({
      __location_context: true,
      __pressable_context: true,
      _type: 'LinkContext',
      id: 'confirm-data',
      href: '/some/url',
    });
  });

  it('MarketingContext', () => {
    expect(
      makeMarketingContext({
        id: 'utm',
        campaign: 'test-campaign',
        medium: 'test-medium',
        source: 'test-source',
      })
    ).toStrictEqual({
      __global_context: true,
      _type: 'MarketingContext',
      id: 'utm',
      campaign: 'test-campaign',
      medium: 'test-medium',
      source: 'test-source',
      term: null,
      content: null,
    });
    expect(
      makeMarketingContext({
        id: 'utm',
        campaign: 'test-campaign',
        medium: 'test-medium',
        source: 'test-source',
        term: 'test-term',
        content: 'test-content',
      })
    ).toStrictEqual({
      __global_context: true,
      _type: 'MarketingContext',
      id: 'utm',
      campaign: 'test-campaign',
      medium: 'test-medium',
      source: 'test-source',
      term: 'test-term',
      content: 'test-content',
    });
  });

  it('MediaPlayerContext', () => {
    expect(makeMediaPlayerContext({ id: 'player-1' })).toStrictEqual({
      __location_context: true,
      _type: 'MediaPlayerContext',
      id: 'player-1',
    });
  });

  it('NavigationContext', () => {
    expect(makeNavigationContext({ id: 'top-nav' })).toStrictEqual({
      __location_context: true,
      _type: 'NavigationContext',
      id: 'top-nav',
    });
  });

  it('OverlayContext', () => {
    expect(makeOverlayContext({ id: 'top-menu' })).toStrictEqual({
      __location_context: true,
      _type: 'OverlayContext',
      id: 'top-menu',
    });
  });

  it('PathContext', () => {
    expect(makePathContext({ id: '/some/path' })).toStrictEqual({
      __global_context: true,
      _type: 'PathContext',
      id: '/some/path',
    });
  });

  it('PressableContext', () => {
    expect(makePressableContext({ id: 'confirm-data' })).toStrictEqual({
      __location_context: true,
      __pressable_context: true,
      _type: 'PressableContext',
      id: 'confirm-data',
    });
  });

  it('RootLocationContext', () => {
    expect(makeRootLocationContext({ id: 'page-A' })).toStrictEqual({
      __location_context: true,
      _type: 'RootLocationContext',
      id: 'page-A',
    });
  });

  it('SessionContext', () => {
    expect(makeSessionContext({ id: 'session-id', hit_number: 123 })).toStrictEqual({
      __global_context: true,
      _type: 'SessionContext',
      id: 'session-id',
      hit_number: 123,
    });
  });
});

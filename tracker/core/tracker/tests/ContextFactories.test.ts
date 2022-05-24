/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID } from '@objectiv/testing-tools';
import {
  GlobalContextName,
  LocationContextName,
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
  it(GlobalContextName.ApplicationContext, () => {
    expect(makeApplicationContext({ id: 'app' })).toStrictEqual({
      __instance_id: matchUUID,
      __global_context: true,
      _type: GlobalContextName.ApplicationContext,
      id: 'app',
    });
  });

  it(LocationContextName.ContentContext, () => {
    expect(makeContentContext({ id: 'content-A' })).toStrictEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.ContentContext,
      id: 'content-A',
    });
  });

  it(GlobalContextName.CookieIdContext, () => {
    expect(makeCookieIdContext({ id: 'error-id', cookie_id: '12345' })).toStrictEqual({
      __instance_id: matchUUID,
      __global_context: true,
      _type: GlobalContextName.CookieIdContext,
      id: 'error-id',
      cookie_id: '12345', // Note: the cookieId parameter is mapped to cookie_id
    });
  });

  it(LocationContextName.ExpandableContext, () => {
    expect(makeExpandableContext({ id: 'accordion-a' })).toStrictEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.ExpandableContext,
      id: 'accordion-a',
    });
  });

  it(GlobalContextName.HttpContext, () => {
    expect(
      makeHttpContext({ id: 'http', referrer: 'referrer', user_agent: 'ua', remote_address: '0.0.0.0' })
    ).toStrictEqual({
      __instance_id: matchUUID,
      __global_context: true,
      _type: GlobalContextName.HttpContext,
      id: 'http',
      referrer: 'referrer',
      user_agent: 'ua',
      remote_address: '0.0.0.0',
    });

    expect(makeHttpContext({ id: 'http', referrer: 'referrer', user_agent: 'ua' })).toStrictEqual({
      __instance_id: matchUUID,
      __global_context: true,
      _type: GlobalContextName.HttpContext,
      id: 'http',
      referrer: 'referrer',
      user_agent: 'ua',
      remote_address: null,
    });
  });

  it(LocationContextName.InputContext, () => {
    expect(makeInputContext({ id: 'input-1' })).toStrictEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.InputContext,
      id: 'input-1',
    });
  });

  it(LocationContextName.LinkContext, () => {
    expect(makeLinkContext({ id: 'confirm-data', href: '/some/url' })).toStrictEqual({
      __instance_id: matchUUID,
      __location_context: true,
      __pressable_context: true,
      _type: LocationContextName.LinkContext,
      id: 'confirm-data',
      href: '/some/url',
    });
  });

  it(GlobalContextName.MarketingContext, () => {
    expect(
      makeMarketingContext({
        id: 'utm',
        campaign: 'test-campaign',
        medium: 'test-medium',
        source: 'test-source',
      })
    ).toStrictEqual({
      __instance_id: matchUUID,
      __global_context: true,
      _type: GlobalContextName.MarketingContext,
      id: 'utm',
      campaign: 'test-campaign',
      medium: 'test-medium',
      source: 'test-source',
      term: null,
      content: null,
      source_platform: null,
      creative_format: null,
      marketing_tactic: null,
    });

    expect(
      makeMarketingContext({
        id: 'utm',
        campaign: 'test-campaign',
        medium: 'test-medium',
        source: 'test-source',
        term: 'test-term',
        content: 'test-content',
        source_platform: 'test-source-platform',
        creative_format: 'test-creative-format',
        marketing_tactic: 'test-marketing-tactic',
      })
    ).toStrictEqual({
      __instance_id: matchUUID,
      __global_context: true,
      _type: GlobalContextName.MarketingContext,
      id: 'utm',
      campaign: 'test-campaign',
      medium: 'test-medium',
      source: 'test-source',
      term: 'test-term',
      content: 'test-content',
      source_platform: 'test-source-platform',
      creative_format: 'test-creative-format',
      marketing_tactic: 'test-marketing-tactic',
    });
  });

  it(LocationContextName.MediaPlayerContext, () => {
    expect(makeMediaPlayerContext({ id: 'player-1' })).toStrictEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.MediaPlayerContext,
      id: 'player-1',
    });
  });

  it(LocationContextName.NavigationContext, () => {
    expect(makeNavigationContext({ id: 'top-nav' })).toStrictEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.NavigationContext,
      id: 'top-nav',
    });
  });

  it(LocationContextName.OverlayContext, () => {
    expect(makeOverlayContext({ id: 'top-menu' })).toStrictEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.OverlayContext,
      id: 'top-menu',
    });
  });

  it(GlobalContextName.PathContext, () => {
    expect(makePathContext({ id: '/some/path' })).toStrictEqual({
      __instance_id: matchUUID,
      __global_context: true,
      _type: GlobalContextName.PathContext,
      id: '/some/path',
    });
  });

  it(LocationContextName.PressableContext, () => {
    expect(makePressableContext({ id: 'confirm-data' })).toStrictEqual({
      __instance_id: matchUUID,
      __location_context: true,
      __pressable_context: true,
      _type: LocationContextName.PressableContext,
      id: 'confirm-data',
    });
  });

  it(LocationContextName.RootLocationContext, () => {
    expect(makeRootLocationContext({ id: 'page-A' })).toStrictEqual({
      __instance_id: matchUUID,
      __location_context: true,
      _type: LocationContextName.RootLocationContext,
      id: 'page-A',
    });
  });

  it(GlobalContextName.SessionContext, () => {
    expect(makeSessionContext({ id: 'session-id', hit_number: 123 })).toStrictEqual({
      __instance_id: matchUUID,
      __global_context: true,
      _type: GlobalContextName.SessionContext,
      id: 'session-id',
      hit_number: 123,
    });
  });
});

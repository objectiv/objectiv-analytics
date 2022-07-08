/*
 * Copyright 2022 Objectiv B.V.
 */

export enum GlobalContextName {
  ApplicationContext = 'ApplicationContext',
  CookieIdContext = 'CookieIdContext',
  HttpContext = 'HttpContext',
  IdentityContext = 'IdentityContext',
  InputValueContext = 'InputValueContext',
  LocaleContext = 'LocaleContext',
  MarketingContext = 'MarketingContext',
  PathContext = 'PathContext',
  SessionContext = 'SessionContext',
}

export type AnyGlobalContextName =
  | 'ApplicationContext'
  | 'CookieIdContext'
  | 'HttpContext'
  | 'IdentityContext'
  | 'InputValueContext'
  | 'LocaleContext'
  | 'MarketingContext'
  | 'PathContext'
  | 'SessionContext';

export enum LocationContextName {
  ContentContext = 'ContentContext',
  ExpandableContext = 'ExpandableContext',
  InputContext = 'InputContext',
  LinkContext = 'LinkContext',
  MediaPlayerContext = 'MediaPlayerContext',
  NavigationContext = 'NavigationContext',
  OverlayContext = 'OverlayContext',
  PressableContext = 'PressableContext',
  RootLocationContext = 'RootLocationContext',
}

export type AnyLocationContextName =
  | 'ContentContext'
  | 'ExpandableContext'
  | 'InputContext'
  | 'LinkContext'
  | 'MediaPlayerContext'
  | 'NavigationContext'
  | 'OverlayContext'
  | 'PressableContext'
  | 'RootLocationContext';

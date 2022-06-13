/*
 * Copyright 2022 Objectiv B.V.
 */

import { GlobalContextName, LocationContextName } from '@objectiv/tracker-core';
import { ContextErrorMessages, GlobalContextErrorType, LocationContextErrorType } from './types';

export const GlobalContextErrorMessages: ContextErrorMessages<GlobalContextErrorType, GlobalContextName> = {
  ANGULAR: {
    GLOBAL_CONTEXT_MISSING: {
      ApplicationContext:
        'ApplicationContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'CookieIdContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'HttpContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'MarketingContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'PathContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'SessionContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
    GLOBAL_CONTEXT_DUPLICATED: {
      ApplicationContext:
        'Only one ApplicationContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'Only one CookieIdContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'Only one HttpContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'Only one MarketingContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'Only one PathContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'Only one SessionContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
  },
  CORE: {
    GLOBAL_CONTEXT_MISSING: {
      ApplicationContext:
        'ApplicationContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'CookieIdContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'HttpContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'MarketingContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'PathContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'SessionContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
    GLOBAL_CONTEXT_DUPLICATED: {
      ApplicationContext:
        'Only one ApplicationContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'Only one CookieIdContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'Only one HttpContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'Only one MarketingContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'Only one PathContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'Only one SessionContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
  },
  BROWSER: {
    GLOBAL_CONTEXT_MISSING: {
      ApplicationContext:
        'ApplicationContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'CookieIdContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'HttpContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'MarketingContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'PathContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'SessionContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
    GLOBAL_CONTEXT_DUPLICATED: {
      ApplicationContext:
        'Only one ApplicationContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'Only one CookieIdContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'Only one HttpContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'Only one MarketingContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'Only one PathContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'Only one SessionContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
  },
  REACT: {
    GLOBAL_CONTEXT_MISSING: {
      ApplicationContext:
        'ApplicationContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'CookieIdContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'HttpContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'MarketingContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'PathContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'SessionContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
    GLOBAL_CONTEXT_DUPLICATED: {
      ApplicationContext:
        'Only one ApplicationContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'Only one CookieIdContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'Only one HttpContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'Only one MarketingContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'Only one PathContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'Only one SessionContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
  },
  REACT_NATIVE: {
    GLOBAL_CONTEXT_MISSING: {
      ApplicationContext:
        'ApplicationContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'CookieIdContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'HttpContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'MarketingContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'PathContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'SessionContext is missing from Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
    GLOBAL_CONTEXT_DUPLICATED: {
      ApplicationContext:
        'Only one ApplicationContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/ApplicationContext.',
      CookieIdContext:
        'Only one CookieIdContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/CookieIdContext.',
      HttpContext:
        'Only one HttpContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/HttpContext.',
      MarketingContext:
        'Only one MarketingContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/MarketingContext.',
      PathContext:
        'Only one PathContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/PathContext.',
      SessionContext:
        'Only one SessionContext should be present in Global Contexts of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/global-contexts/SessionContext.',
    },
  },
};

export const LocationContextErrorMessages: ContextErrorMessages<LocationContextErrorType, LocationContextName> = {
  ANGULAR: {
    LOCATION_CONTEXT_MISSING: {
      ContentContext:
        'ContentContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.\nSee also:\n- Configuring Roots: https://objectiv.io/docs/tracking/angular/how-to-guides/configuring-root-locations.\n- tagRootLocation: https://objectiv.io/docs/tracking/angular/api-reference/locationTaggers/tagRootLocation.',
    },
    LOCATION_CONTEXT_DUPLICATED: {
      ContentContext:
        'Only one ContentContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'Only one ExpandableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'Only one InputContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'Only one LinkContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'Only one MediaPlayerContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'Only one NavigationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'Only one OverlayContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'Only one PressableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'Only one RootLocationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
    LOCATION_CONTEXT_WRONG_POSITION: {
      ContentContext:
        'ContentContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
  },
  CORE: {
    LOCATION_CONTEXT_MISSING: {
      ContentContext:
        'ContentContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
    LOCATION_CONTEXT_DUPLICATED: {
      ContentContext:
        'Only one ContentContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'Only one ExpandableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'Only one InputContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'Only one LinkContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'Only one MediaPlayerContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'Only one NavigationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'Only one OverlayContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'Only one PressableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'Only one RootLocationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
    LOCATION_CONTEXT_WRONG_POSITION: {
      ContentContext:
        'ContentContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
  },
  BROWSER: {
    LOCATION_CONTEXT_MISSING: {
      ContentContext:
        'ContentContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.\nSee also:\n- Configuring Roots: https://objectiv.io/docs/tracking/browser/how-to-guides/configuring-root-locations.\n- tagRootLocation: https://objectiv.io/docs/tracking/browser/api-reference/locationTaggers/tagRootLocation.',
    },
    LOCATION_CONTEXT_DUPLICATED: {
      ContentContext:
        'Only one ContentContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'Only one ExpandableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'Only one InputContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'Only one LinkContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'Only one MediaPlayerContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'Only one NavigationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'Only one OverlayContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'Only one PressableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'Only one RootLocationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
    LOCATION_CONTEXT_WRONG_POSITION: {
      ContentContext:
        'ContentContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
  },
  REACT: {
    LOCATION_CONTEXT_MISSING: {
      ContentContext:
        'ContentContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.\nSee also:\n- Configuring Roots: https://objectiv.io/docs/tracking/react/how-to-guides/configuring-root-locations.\n- TrackedRootLocationContext: https://objectiv.io/docs/tracking/react/api-reference/trackedContexts/TrackedRootLocationContext.\n- RootLocationContextWrapper: https://objectiv.io/docs/tracking/react/api-reference/locationWrappers/RootLocationContextWrapper.',
    },
    LOCATION_CONTEXT_DUPLICATED: {
      ContentContext:
        'Only one ContentContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'Only one ExpandableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'Only one InputContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'Only one LinkContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'Only one MediaPlayerContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'Only one NavigationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'Only one OverlayContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'Only one PressableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'Only one RootLocationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
    LOCATION_CONTEXT_WRONG_POSITION: {
      ContentContext:
        'ContentContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
  },
  REACT_NATIVE: {
    LOCATION_CONTEXT_MISSING: {
      ContentContext:
        'ContentContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is missing from Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.\nSee also:\n- React Navigation Plugin: https://objectiv.io/docs/tracking/react-native/plugins/react-navigation.\n- RootLocationContextWrapper: https://objectiv.io/docs/tracking/react-native/api-reference/locationWrappers/RootLocationContextWrapper.',
    },
    LOCATION_CONTEXT_DUPLICATED: {
      ContentContext:
        'Only one ContentContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'Only one ExpandableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'Only one InputContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'Only one LinkContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'Only one MediaPlayerContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'Only one NavigationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'Only one OverlayContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'Only one PressableContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'Only one RootLocationContext should be present in Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
    LOCATION_CONTEXT_WRONG_POSITION: {
      ContentContext:
        'ContentContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ContentContext.',
      ExpandableContext:
        'ExpandableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/ExpandableContext.',
      InputContext:
        'InputContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/InputContext.',
      LinkContext:
        'LinkContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/LinkContext.',
      MediaPlayerContext:
        'MediaPlayerContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/MediaPlayerContext.',
      NavigationContext:
        'NavigationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/NavigationContext.',
      OverlayContext:
        'OverlayContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/OverlayContext.',
      PressableContext:
        'PressableContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/PressableContext.',
      RootLocationContext:
        'RootLocationContext is in the wrong position of the Location Stack of {{eventName}}.\nTaxonomy documentation: https://objectiv.io/docs/taxonomy/reference/location-contexts/RootLocationContext.',
    },
  },
};

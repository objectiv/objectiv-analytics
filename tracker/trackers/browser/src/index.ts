/*
 * Copyright 2021 Objectiv B.V.
 */

export * from '@objectiv/tracker-core';

export * from './common/factories/makeDefaultPluginsList';
export * from './common/factories/makeDefaultQueue';
export * from './common/factories/makeDefaultTransport';
export * from './common/guards/isParentTaggedElement';
export * from './common/guards/isTagChildrenElement';
export * from './common/guards/isTaggableElement';
export * from './common/guards/isTaggedElement';
export * from './common/parsers/parseTagChildren';
export * from './common/parsers/parseJson';
export * from './common/parsers/parseLocationContext';
export * from './common/parsers/parseTrackClicks';
export * from './common/parsers/parseTrackVisibility';
export * from './common/parsers/parseValidate';
export * from './common/stringifiers/stringifyTagChildren';
export * from './common/stringifiers/stringifyJson';
export * from './common/stringifiers/stringifyLocationContext';
export * from './common/stringifiers/stringifyTrackClicks';
export * from './common/stringifiers/stringifyTrackVisibility';
export * from './common/stringifiers/stringifyValidate';
export * from './common/compareTrackerConfigs';
export * from './common/findParentTaggedElements';
export * from './common/getElementLocationStack';
export * from './common/getLocationHref';
export * from './common/objectivWindowInterface';
export * from './common/runIfValueIsNotUndefined';
export * from './common/trackerErrorHandler';
export * from './common/windowExists';

export * from './definitions/BrowserTrackerConfig';
export * from './definitions/ChildrenTaggingQueries';
export * from './definitions/ChildrenTaggingQuery';
export * from './definitions/FlushQueueOptions';
export * from './definitions/GuardableElement';
export * from './definitions/InteractiveEventTrackerParameters';
export * from './definitions/LocationContext';
export * from './definitions/LocationTaggerParameters';
export * from './definitions/NonInteractiveEventTrackerParameters';
export * from './definitions/ParentTaggedElement';
export * from './definitions/TagLocationAttributes';
export * from './definitions/TagButtonParameters';
export * from './definitions/TagChildrenAttributes';
export * from './definitions/TagChildrenElement';
export * from './definitions/TagChildrenReturnValue';
export * from './definitions/TaggableElement';
export * from './definitions/TaggedElement';
export * from './definitions/TaggingAttribute';
export * from './definitions/TagLinkParameters';
export * from './definitions/TagLocationOptions';
export * from './definitions/TagLocationParameters';
export * from './definitions/TagLocationReturnValue';
export * from './definitions/TrackClicksAttribute';
export * from './definitions/TrackClicksOptions';
export * from './definitions/TrackedElement';
export * from './definitions/TrackerErrorHandlerCallback';
export * from './definitions/TrackVisibilityAttribute';
export * from './definitions/Uuid';
export * from './definitions/ValidateAttribute';
export * from './definitions/ValidChildrenTaggingQuery';
export * from './definitions/WaitForQueueOptions';
export * from './definitions/WaitUntilTrackedOptions';

export * from './eventTrackers/trackAborted';
export * from './eventTrackers/trackApplicationLoaded';
export * from './eventTrackers/trackClick';
export * from './eventTrackers/trackCompleted';
export * from './eventTrackers/trackEvent';
export * from './eventTrackers/trackInputChange';
export * from './eventTrackers/trackSectionHidden';
export * from './eventTrackers/trackSectionVisible';
export * from './eventTrackers/trackURLChange';
export * from './eventTrackers/trackVideoPause';
export * from './eventTrackers/trackVideoStart';
export * from './eventTrackers/trackVisibility';

export * from './locationTaggers/tagButton';
export * from './locationTaggers/tagChild';
export * from './locationTaggers/tagChildren';
export * from './locationTaggers/tagElement';
export * from './locationTaggers/tagExpandableElement';
export * from './locationTaggers/tagInput';
export * from './locationTaggers/tagLink';
export * from './locationTaggers/tagLocation';
export * from './locationTaggers/tagMediaPlayer';
export * from './locationTaggers/tagNavigation';
export * from './locationTaggers/tagOverlay';

export * from './mutationObserver/AutoTrackingState';
export * from './mutationObserver/makeBlurEventHandler';
export * from './mutationObserver/makeClickEventHandler';
export * from './mutationObserver/makeMutationCallback';
export * from './mutationObserver/processTagChildrenElement';
export * from './mutationObserver/trackNewElement';
export * from './mutationObserver/trackNewElements';
export * from './mutationObserver/trackRemovedElement';
export * from './mutationObserver/trackRemovedElements';
export * from './mutationObserver/trackVisibilityHiddenEvent';
export * from './mutationObserver/trackVisibilityVisibleEvent';

export * from './queues/TrackerQueueLocalStorage';

export * from './transports/DebugTransport';
export * from './transports/FetchAPITransport';
export * from './transports/XMLHttpRequestTransport';

export * from './BrowserTracker';
export * from './getOrMakeTracker';
export * from './getTracker';
export * from './getTrackerRepository';
export * from './makeTracker';
export * from './setDefaultTracker';
export * from './startAutoTracking';
export * from './stopAutoTracking';

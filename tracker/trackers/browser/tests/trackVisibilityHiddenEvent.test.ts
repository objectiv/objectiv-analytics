/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LogTransport, MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID } from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, getTrackerRepository, makeTracker, TaggingAttribute } from '../src';
import { trackVisibilityHiddenEvent } from '../src/mutationObserver/trackVisibilityHiddenEvent';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('trackVisibilityHiddenEvent', () => {
  beforeEach(() => {
    getTrackerRepository().trackersMap = new Map();
    getTrackerRepository().defaultTracker = undefined;
    jest.resetAllMocks();
    makeTracker({ applicationId: generateGUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('should not track elements without visibility tagging attributes', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');

    trackVisibilityHiddenEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not track elements with invalid visibility tagging attributes', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, 'null');

    trackVisibilityHiddenEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not track in mode:auto', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');

    trackVisibilityHiddenEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not track in mode:manual with isVisible:true', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":true}');

    trackVisibilityHiddenEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should track in mode:manual with isVisible:false', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":false}');

    trackVisibilityHiddenEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'HiddenEvent',
        global_contexts: [],
        location_stack: [],
      })
    );
  });

  it('should use given tracker instead of the global one', async () => {
    const trackerOverride = new BrowserTracker({ applicationId: 'override', transport: new LogTransport() });
    jest.spyOn(trackerOverride, 'trackEvent');

    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":false}');

    trackVisibilityHiddenEvent(trackedDiv, trackerOverride);

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(trackerOverride.trackEvent).toHaveBeenCalledTimes(1);
    expect(trackerOverride.trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'HiddenEvent',
        global_contexts: [],
        location_stack: [],
      })
    );
  });
});

/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID } from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, getTrackerRepository, makeTracker, TaggingAttribute } from '../src';
import { trackVisibilityVisibleEvent } from '../src/mutationObserver/trackVisibilityVisibleEvent';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('trackVisibilityVisibleEvent', () => {
  beforeEach(() => {
    getTrackerRepository().trackersMap = new Map();
    getTrackerRepository().defaultTracker = undefined;
    jest.resetAllMocks();
    makeTracker({ applicationId: generateGUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  afterEach(() => {});

  it('should not track elements without visibility tagging attributes', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not track elements with invalid visibility tagging attributes', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, 'null');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should track in mode:auto', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'VisibleEvent',
        global_contexts: [],
        location_stack: [],
      })
    );
  });

  it('should track in mode:manual with isVisible:true', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":true}');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'VisibleEvent',
        global_contexts: [],
        location_stack: [],
      })
    );
  });

  it('should not track in mode:manual with isVisible:false', async () => {
    const trackedDiv = makeTaggedElement('div-id', null, 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":false}');

    trackVisibilityVisibleEvent(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });
});

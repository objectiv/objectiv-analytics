/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, LocationContextName } from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, getTrackerRepository, makeTracker, TaggingAttribute } from '../src';
import { trackRemovedElements } from '../src/mutationObserver/trackRemovedElements';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('trackRemovedElements', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateGUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  afterEach(() => {
    getTrackerRepository().trackersMap = new Map();
    getTrackerRepository().defaultTracker = undefined;
    jest.resetAllMocks();
  });

  it('should skip all Elements that are not Tagged Element', async () => {
    const div = document.createElement('div');
    const anotherDiv = document.createElement('div');
    const button = document.createElement('button');

    anotherDiv.appendChild(button);
    div.appendChild(anotherDiv);

    trackRemovedElements(div, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should skip all Elements that do not have visibility tagging attributes', async () => {
    const trackedDiv = makeTaggedElement('div1', 'div1', 'div');
    const trackedChildDiv = makeTaggedElement('div2', 'div2', 'div');
    const trackedButton = makeTaggedElement('button', 'button', 'button');

    trackedDiv.appendChild(trackedChildDiv);
    trackedChildDiv.appendChild(trackedButton);

    trackRemovedElements(trackedDiv, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should trigger a visibility:hidden Event for Tagged Elements with visibility:auto attributes', async () => {
    const div = document.createElement('div');
    const trackedDiv = makeTaggedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');
    const trackedButton = makeTaggedElement('button', null, 'button');

    trackedDiv.appendChild(trackedButton);
    div.appendChild(trackedDiv);

    trackRemovedElements(div, getTracker());

    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'HiddenEvent',
        global_contexts: [],
        location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'div' })],
      })
    );
  });

  it('should not trigger a visibility:hidden Event for Tagged Elements with visibility:manual attributes', async () => {
    const div = document.createElement('div');
    const trackedDiv = makeTaggedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"manual","isVisible":true}');
    const trackedButton = makeTaggedElement('button', null, 'button');

    trackedDiv.appendChild(trackedButton);
    div.appendChild(trackedDiv);

    trackRemovedElements(div, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should TrackerConsole.error', async () => {
    const div = document.createElement('div');
    const trackedDiv = makeTaggedElement('div', 'div', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"broken"}');
    const trackedButton = makeTaggedElement('button', null, 'button');

    trackedDiv.appendChild(trackedButton);
    div.appendChild(trackedDiv);

    trackRemovedElements(div, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
  });

  it('should TrackerConsole.error', async () => {
    const div = document.createElement('div');
    jest.spyOn(div, 'querySelectorAll').mockImplementation(() => {
      throw new Error();
    });

    trackRemovedElements(div, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
  });
});

/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import '@objectiv/developer-tools';
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, LocationContextName } from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, getTrackerRepository, makeTracker, TaggingAttribute } from '../src';
import { trackNewElement } from '../src/mutationObserver/trackNewElement';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('trackNewElement', () => {
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

  it('developers tools should have been imported', async () => {
    expect(globalThis.objectiv).not.toBeUndefined();
  });

  it('should skip the Element if it is not a Tagged Element', async () => {
    const div = document.createElement('div');
    jest.spyOn(div, 'addEventListener');

    trackNewElement(div, getTracker());

    expect(div.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should skip collision checks if the Element is not a Tagged Element', async () => {
    const div = document.createElement('div');
    if (globalThis.objectiv.devTools) {
      jest.spyOn(globalThis.objectiv.devTools.LocationTree, 'add');
    }

    jest.resetAllMocks();

    trackNewElement(div, getTracker());

    expect(globalThis.objectiv.devTools?.LocationTree.add).not.toHaveBeenCalled();
  });

  it('should skip collision checks if the Element has the `validate` attribute disabling location check', async () => {
    const div = makeTaggedElement('div', 'div', 'div');
    if (globalThis.objectiv.devTools) {
      jest.spyOn(globalThis.objectiv.devTools.LocationTree, 'add');
    }

    trackNewElement(div, getTracker());
    expect(globalThis.objectiv.devTools?.LocationTree.add).toHaveBeenCalledTimes(1);

    jest.resetAllMocks();

    div.setAttribute(TaggingAttribute.validate, JSON.stringify({ locationUniqueness: false }));
    trackNewElement(div, getTracker());
    expect(globalThis.objectiv.devTools?.LocationTree.add).not.toHaveBeenCalled();
  });

  it('should skip the Element if it is already Tracked', async () => {
    const trackedButton = makeTaggedElement('button-id-1', 'test', 'button', true);
    trackedButton.setAttribute(TaggingAttribute.tracked, 'true');
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not attach click event listener', async () => {
    const trackedButton = makeTaggedElement('button-id-2', 'test', 'button', true);
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, 'false');
    trackedButton.setAttribute(TaggingAttribute.validate, JSON.stringify({ locationUniqueness: false }));
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should track visibility: visible event', async () => {
    const trackedDiv = makeTaggedElement('div-id-1', 'test', 'div');
    trackedDiv.setAttribute(TaggingAttribute.trackVisibility, '{"mode":"auto"}');
    trackedDiv.setAttribute(TaggingAttribute.validate, JSON.stringify({ locationUniqueness: false }));
    jest.spyOn(trackedDiv, 'addEventListener');

    trackNewElement(trackedDiv, getTracker());

    expect(trackedDiv.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'VisibleEvent',
        global_contexts: [],
        location_stack: [expect.objectContaining({ _type: LocationContextName.ContentContext, id: 'test' })],
      })
    );
  });

  it('should attach click event listener - passive', async () => {
    const trackedButton = makeTaggedElement('button-id-1', 'test', 'button', true);
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, 'true');
    trackedButton.setAttribute(TaggingAttribute.validate, JSON.stringify({ locationUniqueness: false }));
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedButton.addEventListener).toHaveBeenNthCalledWith(1, 'click', expect.any(Function), { passive: true });
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should attach click event listener - capture', async () => {
    const trackedButton = makeTaggedElement('button-id-1', 'test', 'button', true);
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, JSON.stringify({ waitUntilTracked: true }));
    trackedButton.setAttribute(TaggingAttribute.validate, JSON.stringify({ locationUniqueness: false }));
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedButton.addEventListener).toHaveBeenNthCalledWith(1, 'click', expect.any(Function), true);
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should attach click event listener - capture with custom options', async () => {
    const trackedButton = makeTaggedElement('button-id-1', 'test', 'button', true);
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, JSON.stringify({ waitUntilTracked: { timeoutMs: 5000 } }));
    trackedButton.setAttribute(TaggingAttribute.validate, JSON.stringify({ locationUniqueness: false }));
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedButton.addEventListener).toHaveBeenNthCalledWith(1, 'click', expect.any(Function), true);
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not attach click event listener and TrackerConsole.error', async () => {
    const trackedButton = makeTaggedElement('button-id-1', 'test', 'button', true);
    trackedButton.setAttribute('data-testid', 'test-button');
    trackedButton.setAttribute(TaggingAttribute.trackClicks, JSON.stringify({ waitUntilTracked: false }));
    jest.spyOn(trackedButton, 'addEventListener');

    trackNewElement(trackedButton, getTracker());

    expect(trackedButton.addEventListener).not.toHaveBeenCalled();
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
  });

  it('should attach blur event listener', async () => {
    const trackedInput = makeTaggedElement('input-id-1', 'test', 'input', false, true);
    trackedInput.setAttribute(TaggingAttribute.trackBlurs, 'true');
    trackedInput.setAttribute(TaggingAttribute.validate, JSON.stringify({ locationUniqueness: false }));
    jest.spyOn(trackedInput, 'addEventListener');

    trackNewElement(trackedInput, getTracker());

    expect(trackedInput.addEventListener).toHaveBeenCalledTimes(1);
    expect(trackedInput.addEventListener).toHaveBeenNthCalledWith(1, 'blur', expect.any(Function), { passive: true });
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should not attach blur event listener', async () => {
    const trackedInput = makeTaggedElement('input-id-1', 'test', 'input', false);
    trackedInput.setAttribute(TaggingAttribute.trackBlurs, 'false');
    trackedInput.setAttribute(TaggingAttribute.validate, JSON.stringify({ locationUniqueness: false }));
    jest.spyOn(trackedInput, 'addEventListener');

    trackNewElement(trackedInput, getTracker());

    expect(trackedInput.addEventListener).toHaveBeenCalledTimes(0);
    expect(getTracker().trackEvent).not.toHaveBeenCalled();
  });

  it('should TrackerConsole.error', async () => {
    const trackedInput = makeTaggedElement('input-id-1', 'test', 'input', true);
    trackedInput.setAttribute(TaggingAttribute.trackBlurs, 'true');
    jest.spyOn(trackedInput, 'addEventListener').mockImplementation(() => {
      throw new Error('nope');
    });

    trackNewElement(trackedInput, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
  });
});

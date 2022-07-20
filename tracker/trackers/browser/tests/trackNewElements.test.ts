/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import '@objectiv/developer-tools';
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, LocationContextName } from '@objectiv/tracker-core';
import {
  BrowserTracker,
  getTracker,
  getTrackerRepository,
  makeTracker,
  TaggingAttribute,
  tagOverlay,
  tagPressable,
} from '../src';
import { trackNewElements } from '../src/mutationObserver/trackNewElements';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('trackNewElements', () => {
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

  it('should apply tagging attributes to Elements tracked via Children Tracking and track them right away', async () => {
    const div1 = document.createElement('div');
    div1.setAttribute(
      TaggingAttribute.tagChildren,
      JSON.stringify([
        { queryAll: '#button', tagAs: tagPressable({ id: 'button' }) },
        { queryAll: '#child-div', tagAs: tagOverlay({ id: 'child-div' }) },
      ])
    );

    const button = document.createElement('button');
    button.setAttribute('id', 'button');

    const childDiv = document.createElement('div');
    childDiv.setAttribute('id', 'child-div');

    jest.spyOn(div1, 'addEventListener');
    jest.spyOn(button, 'addEventListener');
    jest.spyOn(childDiv, 'addEventListener');

    div1.appendChild(button);
    div1.appendChild(childDiv);

    trackNewElements(div1, getTracker());

    expect(div1.addEventListener).not.toHaveBeenCalled();
    expect(childDiv.addEventListener).not.toHaveBeenCalled();
    expect(button.addEventListener).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'VisibleEvent',
        global_contexts: [],
        location_stack: [expect.objectContaining({ _type: LocationContextName.OverlayContext, id: 'child-div' })],
      })
    );
  });

  it('should TrackerConsole.error', async () => {
    // @ts-ignore
    trackNewElements(null, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
  });

  describe('collisions', () => {
    it('should TrackerConsole.error if a collision occurs and both elements still exist', async () => {
      const root = document.createElement('root');
      const wrapper = document.createElement('div');
      const parent1 = makeTaggedElement('parentElement1', 'parent1', 'div');
      const parent2 = makeTaggedElement('parentElement2', 'parent2', 'div');
      const div1 = makeTaggedElement('element1', 'div', 'div');
      const div2 = makeTaggedElement('element2', 'div', 'div');
      parent1.append(div1);
      parent1.append(div2);
      parent2.append(parent1);
      wrapper.appendChild(parent2);
      root.appendChild(wrapper);

      trackNewElements(wrapper, getTracker());

      expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
      expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
        1,
        `｢objectiv｣ Location collision detected: Content:parent2 / Content:parent1 / Content:div`
      );
    });
  });
});

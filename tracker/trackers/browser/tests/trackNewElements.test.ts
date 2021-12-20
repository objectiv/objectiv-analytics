/*
 * Copyright 2021 Objectiv B.V.
 */

import { matchUUID } from '@objectiv/testing-tools';
import { generateUUID, makeOverlayContext } from '@objectiv/tracker-core';
import {
  BrowserTracker,
  getTracker,
  getTrackerRepository,
  makeTracker,
  tagButton,
  TaggingAttribute,
  tagOverlay,
} from '../src';
import { trackNewElements } from '../src/mutationObserver/trackNewElements';

describe('trackNewElements', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateUUID(), endpoint: 'test' });
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
        { queryAll: '#button', tagAs: tagButton({ id: 'button', text: 'button' }) },
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
        _type: 'SectionVisibleEvent',
        id: matchUUID,
        global_contexts: [],
        location_stack: [makeOverlayContext({ id: 'child-div' })],
      })
    );
  });

  it('should console error', async () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});

    // @ts-ignore
    trackNewElements(null, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });
});
